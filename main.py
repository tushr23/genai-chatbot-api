# Systematic, human-like imports
import os
import logging
from fastapi import FastAPI, Request as FastAPIRequest, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from transformers import pipeline
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import db

# Logging setup
logging.basicConfig(level=logging.INFO)

# Configuration
API_KEY = os.environ.get("API_KEY")
DEBUG_RAW = os.environ.get("DEBUG", "False")
DEBUG = DEBUG_RAW == "True"
if API_KEY is None:
    logging.warning("API_KEY is not set. External services will not be available.")
if DEBUG_RAW not in ["True", "False"]:
    logging.warning(f"DEBUG environment variable set to invalid value: '{DEBUG_RAW}'. Defaulting to False.")
if DEBUG:
    print("Debug mode is ON")

# App setup
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    logging.warning(f"404 Not Found: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    logging.error(f"500 Internal Server Error: {request.url} - {getattr(exc, 'detail', str(exc))}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error. Please try again later."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Invalid request", "details": exc.errors()}
    )

# Model and DB setup
chatbot = pipeline("text-generation", model="gpt2")
db.create_table()

# Request schema
class ChatRequest(BaseModel):
    question: str

# Chat endpoint
@app.post("/v1/chat")
@limiter.limit("5/minute")
async def chat(request: ChatRequest, raw_request: FastAPIRequest):
    from datetime import datetime, timezone
    ip = raw_request.client.host if raw_request.client else "unknown"
    logging.info(f"[CHAT] {datetime.now(timezone.utc).isoformat()} | IP: {ip} | Question: {request.question}")

    question = request.question.strip()
    if not question:
        logging.warning("Received empty question input.")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Question cannot be empty."}
        )
    if len(question) > 200:
        logging.warning(f"Received suspiciously long question: {len(question)} chars.")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Question is too long. Limit to 200 characters."}
        )
    if any(word in question.lower() for word in ["select ", "drop ", "insert ", "delete ", "update ", "--"]):
        logging.warning(f"Received question with possible SQL injection attempt: {question}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid question content."}
        )
    answer = chatbot(question, max_length=50)[0]['generated_text']
    db.add_log(question, answer)
    return {"answer": answer}

# Logs endpoint
@app.get("/v1/logs")
async def get_logs(raw_request: FastAPIRequest):
    from datetime import datetime, timezone
    ip = raw_request.client.host if raw_request.client else "unknown"
    logging.info(f"[LOGS] {datetime.now(timezone.utc).isoformat()} | IP: {ip} | Logs requested")
    logs = db.get_logs()
    return {"logs": logs}
