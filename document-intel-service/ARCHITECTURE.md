# Architecture Documentation: Document Intelligence & Question Extraction Service

## Executive Summary

The **Document Intelligence & Question Extraction Service** is an enterprise-grade backend service built to ingest multi-page PDFs and scanned images, extract structured questions and multiple-choice options, evaluate granular confidence scores, match question papers with answer keys, and flag low-confidence items for human review.

---

## 🏗️ System Architecture

```
                                    +-----------------------+
                                    |   Client / Postman    |
                                    +-----------+-----------+
                                                |
                                                v
                                    +-----------------------+
                                    |     FastAPI Service   |
                                    | (JWT / OpenAPI / CORS)|
                                    +-----+-----------+-----+
                                          |           |
                                          v           v
                               +----------+--+     +--+----------+
                               |  PostgreSQL |     |    Redis    |
                               |   Database  |     | Message Bus |
                               +-------------+     +------+------+
                                                          |
                                                          v
                                                   +--------------+
                                                   | Celery Worker|
                                                   | Processing   |
                                                   +--------------+
```

### Technology Stack Rationale

1. **FastAPI**: Lightweight, high-performance asynchronous web framework exposing automatic OpenAPI/Swagger documentation, strict request/response data validation via Pydantic V2, and dependency injection for security/DB contexts.
2. **PostgreSQL**: Relational database supporting strict foreign key constraints, indexing for fast query lookup, JSONB/JSON storage for dynamic options and page metadata, and transactional safety.
3. **Redis**: In-memory data store acting as the message broker and result backend for Celery background jobs.
4. **Celery**: Distributed task queue for non-blocking asynchronous document processing, status tracking (`pending` -> `processing` -> `completed` / `failed`), and multi-document answer key matching.
5. **PyMuPDF (`fitz`) & Pillow**: High-speed, robust C-extension libraries for rendering PDFs, inspecting layout text structures, and extracting image geometries.

---

## 📁 Storage & File Organization

Files are stored safely on the local filesystem under:
```
storage/{user_id}/{document_id}/{filename}
```
- **Security**: File extensions (`.pdf`, `.jpg`, `.jpeg`, `.png`) and file size limits (<= 25 MB) are validated upon upload before writing to disk.
- **Isolation**: Each document is contained within a dedicated folder structure preventing filename collisions and directory traversal attacks.

---

## ⚙️ Core Component Strategy

### 1. Document Extraction Engine (`app/services/extraction_service.py`)
- **Interface Design**: Pluggable interface isolating document parsing from web API logic. The underlying engine (PyMuPDF, Tesseract, Google Vision, or Claude Vision) can be swapped seamlessly without altering API endpoints.
- **Regex Layout Engine**:
  - **Question Headers**: Recognizes diverse formats (`Q1`, `Q.1`, `Question 1:`, `1.`, `1)`, `(1)`).
  - **Options**: Matches option labels (`A.`, `B.`, `a)`, `(1)`, `(2)`).
  - **Type Classification**: Classifies questions into `mcq` or `short_answer`.
- **Multi-Page Continuation Merging**:
  - Detects incomplete question blocks across page boundaries.
  - Combines text seamlessly while tracking all source pages in `source_pages: [1, 2]`.

### 2. Confidence Evaluation & Review Flagging (`app/services/confidence.py`)
Confidence is calculated dynamically rather than blindly trusting external APIs ($0.0 \le \text{confidence} \le 1.0$):
- Missing question header ($-0.20$)
- Incomplete / very short text ($-0.35$)
- MCQ question with missing options ($-0.35$)
- Scanned / noise artifacts ($-0.15$)
- Multi-page continuation ($-0.05$)

**Review Flag Triggering**:
If $\text{confidence} < 0.85$ or key fields are missing, an automated `ReviewFlag` record is generated with actionable error descriptions accessible via `GET /review-items`.

### 3. Answer Key Association (`app/services/answer_matcher.py`)
Groups question papers and answer keys using `DocumentGroup`.
- **Primary Strategy**: Exact Question Number alignment (`Q1` <-> `Q1`).
- **Secondary Strategy**: Fuzzy text similarity via `difflib.SequenceMatcher` ($> 0.65$ ratio).
- **Guard Rail**: Never guesses answers. Low-confidence matches are explicitly marked as `unmatched`.

---

## 🔒 Security & Authorization

- **JWT Authentication**: 24-hour expiration tokens signed with `HS256` and configurable `SECRET_KEY`.
- **Password Security**: Passwords hashed using `bcrypt`.
- **User Scoping**: Every document, question, answer, and review item is explicitly scoped to `user_id`. Users cannot inspect or mutate another user's documents.
- **Sanitized Errors**: Global exception handlers prevent raw Python stack trace leaks.

---

## ⚖️ Trade-offs & Limitations

1. **Local Storage**: Local filesystem storage is used for the assignment demo. For production at scale, an object store like AWS S3 or Google Cloud Storage should replace `StorageService`.
2. **Vision/OCR Fallback**: PyMuPDF handles digital PDFs natively. For severely degraded handwritten scans, integrating an OCR API (e.g., Tesseract or Cloud Vision API) provides enhanced character recognition.
