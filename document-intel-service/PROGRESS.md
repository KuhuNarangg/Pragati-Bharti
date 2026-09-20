# Document Intelligence & Question Extraction Service - Progress Tracker

## Phase Status Summary

| Phase | Description | Status |
|---|---|---|
| **Phase 0** | Project Foundation (FastAPI, DB, Celery, Redis, Docker, Migration, Health) | ✅ **Completed & Verified** |
| **Phase 1** | Auth + Upload + Async Processing | ✅ **Completed & Verified** |
| **Phase 2** | Real Document Extraction & Confidence/Review | ✅ **Completed & Verified** |
| **Phase 3** | Answer Key Association | ⏳ Pending Approval |
| **Phase 4** | Review API + Error Handling + Submission Polish | ⏳ Pending Approval |

---

## Phase 2 Breakdown

- [x] Pluggable Document Extraction Service (`app/services/extraction_service.py`)
- [x] PDF text layout extraction via PyMuPDF (`fitz`) with page index tracking
- [x] JPG/PNG layout parsing via Pillow
- [x] Multi-question detection with regex patterns (`Q1`, `1.`, `Question 1:`, options `A.`, `B.`, `(1)`, `(2)`)
- [x] Multi-page continuation merging across page boundaries (`source_pages=[1, 2]`)
- [x] Granular confidence calculator (`app/services/confidence.py`) evaluating text length, option count, missing numbers, and document noise
- [x] Automatic review flagging (`ReviewFlag` creation for low confidence or incomplete extractions)
- [x] Background task integration in Celery task (`process_document_task`)
- [x] Question retrieval endpoints (`GET /questions`, `GET /questions/{id}`)
- [x] Benchmark test documents in `sample_documents/` (`clean_question_paper.pdf`, `scanned_low_quality.jpg`, `rotated_page.png`, `answer_key.pdf`)
- [x] Test suite passing 100% (14 tests)
