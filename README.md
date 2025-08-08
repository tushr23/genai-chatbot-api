
# GenAI Chatbot API

![CI](https://github.com/tushr23/genai-chatbot-api/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
[![codecov](https://codecov.io/gh/tushr23/genai-chatbot-api/graph/badge.svg?token=USR50RXZN8)](https://codecov.io/gh/tushr23/genai-chatbot-api)

## Introduction

A production-ready Generative AI Chatbot API built with Python, FastAPI, Hugging Face Transformers, and SQLite. Accepts user questions via REST API, generates smart answers using GPT-2, and logs every conversation. Easily deployable on AWS EC2 for real-world applications.

## Features
- Accepts user questions via API
- Generates answers using GPT-2 (Hugging Face)
- Logs conversations to a database
- Endpoint to view all logs
- Easy cloud deployment (AWS EC2)
- Well-documented code and API

## Tech Stack
- Python 3.10+
- FastAPI
- Hugging Face Transformers
- SQLite
- Uvicorn
- AWS EC2

## Quickstart

### Clone the repo
```bash
git clone https://github.com/tushr23/genai-chatbot-api.git
cd genai-chatbot-api
```

### Install requirements
```bash
pip install -r requirements.txt
```

### Run the app locally
```bash
python -m uvicorn main:app --reload
```

### Run with Docker (Recommended)
```bash
docker build -t genai-chatbot-api .
docker run -p 8000:8000 genai-chatbot-api
```

## API Usage

- **POST /v1/chat**
   - Request: `{ "question": "Your question here" }`
   - Response: `{ "answer": "Chatbot's answer" }`

- **GET /v1/logs**
   - Returns all saved conversations.

- **Interactive Docs:** Visit `/docs` for Swagger UI.

## Configuration

This project uses environment variables for flexible, secure configuration.

- `DATABASE_NAME`: Database file name (default: `chatbot.db`)
- `API_KEY`: Secret key for external services
- `DEBUG`: Set to `True` for debug mode

### How to set environment variables

- **Windows CMD:**
   ```
   set DATABASE_NAME=mydb.db
   set API_KEY=your-key
   set DEBUG=True
   python -m uvicorn main:app --reload
   ```
- **Linux/Mac:**
   ```
   export DATABASE_NAME=mydb.db
   export API_KEY=your-key
   export DEBUG=True
   python -m uvicorn main:app --reload
   ```
- **Docker:**
   ```
   docker run -e DATABASE_NAME=mydb.db -e API_KEY=your-key -e DEBUG=True -p 8000:8000 genai-chatbot-api
   ```

## Security & Best Practices

### Input Validation & Sanitization
- Blocks empty, too-long, and suspicious (SQL) questions
- All rejected questions are logged

### Rate Limiting
- 5 requests per minute per IP address
- Automated tests prove this works

### Error Handling
- Custom JSON error responses for 404, 500, and validation errors
- All errors are logged

### Advanced Logging
- Every request to `/v1/chat` and `/v1/logs` is logged with timestamp, IP, and details

## Deployment & Scaling

### Docker
- Build and run with Docker for easy deployment

### AWS EC2 (Cloud)
- Step-by-step guide for cloud deployment

### Performance Tips
- Run multiple workers for speed and reliability:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
- Use Gunicorn for production:
   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

### CI/CD with GitHub Actions
- Automated tests and coverage on every push/PR
- Example workflow: `.github/workflows/ci.yml`

## Test Coverage

Run all automated tests and check coverage:
```bash
pytest --cov=.
```
CI/CD runs these tests automatically.

## Contributing

Pull requests are welcome! For major changes, open an issue first to discuss.

## License

MIT

## Credits

Built by Tushr Verma