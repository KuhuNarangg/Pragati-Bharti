# Document Intelligence & Question Extraction Service

A backend service built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, Celery, and PyMuPDF for automated document ingestion, question extraction, answer matching, and review flagging.

---

## 🚀 Quick Start with Docker Compose

Ensure Docker and Docker Compose are installed on your machine.

```bash
# 1. Navigate to service folder
cd document-intel-service

# 2. Copy environment variables
cp .env.example .env

# 3. Start services via Docker Compose
docker compose up --build -d

# 4. Check service health
curl http://localhost:8000/health
```

### Access Points:
- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## 🛠️ Manual / Local Development Setup

If running locally without Docker:

### 1. Prerequisites
- Python 3.11+
- PostgreSQL server running on `localhost:5432`
- Redis server running on `localhost:6379`

### 2. Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Database Migration
```bash
alembic upgrade head
```

### 4. Running Application & Workers
```bash
# Terminal 1: API Application
uvicorn app.main:app --reload --port 8000

# Terminal 2: Celery Worker
celery -A app.workers.celery_app.celery worker --loglevel=info
```

### 5. Running Tests
```bash
pytest -v
```

---

## 📂 Project Structure

```
document-intel-service/
├── README.md
├── PROGRESS.md
├── ARCHITECTURE.md
├── .env.example
├── .env
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── migrations/          # Alembic database migrations
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Settings configuration
│   ├── database.py      # SQLAlchemy setup
│   ├── models/          # User, Document, Question, Answer, ReviewFlag
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API Router Endpoints
│   ├── services/        # Storage, Extraction, Matching, Confidence, Security
│   ├── workers/         # Celery app and async tasks
│   └── core/            # Custom exception handling
├── tests/               # Pytest suite
└── sample_documents/    # Benchmark PDFs and images
```
