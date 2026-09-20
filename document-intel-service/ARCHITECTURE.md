# Architecture Documentation: Document Intelligence & Question Extraction Service

## Overview

The **Document Intelligence & Question Extraction Service** is an asynchronous backend service designed to upload, process, extract, and match questions and answers from diverse document formats (PDFs, scanned images, rotated pages).

---

## High-Level System Architecture

```
                                    +-----------------------+
                                    |     Client / API      |
                                    +-----------+-----------+
                                                |
                                                v
                                    +-----------------------+
                                    |      FastAPI Web      |
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

### Component Breakdown

1. **FastAPI**: Provides non-blocking API handlers, OpenAPI documentation, request validation via Pydantic, and JWT authentication.
2. **PostgreSQL**: Stores relational metadata including users, documents, extracted questions, matched answers, and review flags.
3. **Redis**: Acts as the Celery task queue broker and result store.
4. **Celery Worker**: Executes document rasterization, extraction, confidence evaluation, and answer key matching asynchronously.
5. **Storage Layer**: Local filesystem storage organized by `storage/{user_id}/{document_id}/`.

---

## Core Data Models

- **Users**: Authentication & ownership model.
- **DocumentGroups**: Links related question papers and answer keys together.
- **Documents**: Tracks upload state (`pending` -> `processing` -> `completed` / `failed`), page count, file path, and document type.
- **Questions**: Contains extracted text, question type (`mcq`, `short_answer`), options array, source page mapping, confidence score, and extraction status.
- **Answers**: Holds extracted answer key information linked to questions, match confidence, and status (`matched` / `unmatched`).
- **ReviewFlags**: Flags low-confidence extractions or incomplete questions for human review with actionable error reasons.
