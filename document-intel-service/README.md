# Document Intelligence & Question Extraction Service

An enterprise backend service built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **Redis**, **Celery**, and **PyMuPDF** for automated document ingestion, multi-page question extraction, confidence scoring, answer key matching, and review flagging.

---

## 🚀 Features

- **JWT Authentication**: User registration, login, and secure user-scoped authorization.
- **Document Ingestion**: Supports PDF, JPG, JPEG, and PNG files up to 25 MB with storage organization (`storage/{user_id}/{document_id}/`).
- **Async Celery Workers**: Background processing for document parsing, page count inspection, and multi-document matching.
- **Pluggable Extraction Engine**: Extracts questions, multi-choice options, types (`mcq`, `short_answer`), and handles multi-page question continuation (`source_pages=[1, 2]`).
- **Confidence Scoring & Review Flagging**: Granular confidence evaluation engine ($0.0 \le \text{score} \le 1.0$) with automated review flagging (`GET /review-items`).
- **Answer Key Association**: Document Groups (`POST /document-groups`) linking question papers and answer keys with exact and fuzzy text matching (`GET /questions/{id}/answer`).
- **Production Error Handling**: Global exception handlers preventing stack trace leakage.

---

## ⚡ Quick Start with Docker Compose

Ensure Docker and Docker Compose are installed.

```bash
# 1. Navigate to service folder
cd document-intel-service

# 2. Copy environment variables
cp .env.example .env

# 3. Build and launch services
docker compose up --build -d

# 4. Verify system health
curl http://localhost:8000/health
```

### Endpoints & Documentation:
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## 🛠️ Local Development Setup

```bash
# 1. Create virtual environment & activate
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations
alembic upgrade head

# 4. Start local server
uvicorn app.main:app --reload --port 8000

# 5. Start Celery worker (in separate terminal)
celery -A app.workers.celery_app.celery worker --loglevel=info

# 6. Execute full Pytest suite
pytest -v
```

---

## 📋 API Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/health` | Service & DB & Redis health check | No |
| `POST` | `/auth/register` | User registration | No |
| `POST` | `/auth/login` | User login (returns JWT) | No |
| `POST` | `/documents/upload` | Upload PDF/image file | Yes |
| `GET` | `/documents` | List user's uploaded documents | Yes |
| `GET` | `/documents/{id}` | Get document metadata | Yes |
| `GET` | `/documents/{id}/status` | Get processing status | Yes |
| `DELETE` | `/documents/{id}` | Delete document & storage | Yes |
| `POST` | `/document-groups` | Create document group | Yes |
| `GET` | `/document-groups/{id}` | Get group details & linked docs | Yes |
| `GET` | `/questions` | List extracted questions | Yes |
| `GET` | `/questions/{id}` | Get question details | Yes |
| `GET` | `/questions/{id}/answer` | Get matched answer | Yes |
| `GET` | `/review-items` | Get low-confidence & flagged items | Yes |

---

## 🧪 Testing & Postman

- **Pytest Suite**: Includes unit and integration tests covering auth, upload validation, extraction, confidence, answer matching, and review endpoints (`pytest -v`).
- **Postman Collection**: Import [`postman_collection.json`](file:///Users/kuhunarang/Library/Mobile%20Documents/com~apple~CloudDocs/Desktop/Developer/pbnc/document-intel-service/postman_collection.json) to execute the complete API workflow.
- **Sample Output**: See [`docs/sample_output.json`](file:///Users/kuhunarang/Library/Mobile%20Documents/com~apple~CloudDocs/Desktop/Developer/pbnc/document-intel-service/docs/sample_output.json) for sample structured JSON responses.
