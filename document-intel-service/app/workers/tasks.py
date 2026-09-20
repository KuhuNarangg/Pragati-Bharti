import logging
from pathlib import Path
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.models.question import Question, ExtractionStatus
from app.models.review_flag import ReviewFlag
from app.services.extraction_service import extraction_service
from app.services.confidence import confidence_calculator

logger = logging.getLogger(__name__)


@celery.task(name="process_document_task")
def process_document_task(document_id: int):
    """Async background task to process uploaded documents, extract questions, evaluate confidence, and create review flags."""
    logger.info(f"Starting document extraction processing for document ID: {document_id}")
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document ID {document_id} not found.")
            return {"status": "error", "message": "Document not found"}

        # 1. Transition status to processing
        doc.status = DocumentStatus.PROCESSING.value
        db.commit()

        storage_path = doc.storage_path
        if not storage_path or not Path(storage_path).exists():
            doc.status = DocumentStatus.FAILED.value
            db.commit()
            return {"status": "failed", "error": "Storage path does not exist"}

        # 2. Extract questions from document
        extracted_data = extraction_service.extract_questions(storage_path)

        # 3. Save extracted questions & review flags
        total_questions = 0
        review_flags_created = 0
        max_page = 1

        for q_item in extracted_data:
            conf_score, ext_status, reasons = confidence_calculator.evaluate(q_item)
            
            # Track max page
            pages = q_item.get("source_pages") or [1]
            if pages:
                max_page = max(max_page, max(pages))

            question = Question(
                document_id=doc.id,
                question_number=q_item.get("question_number"),
                question_text=q_item.get("question_text") or "Unspecified question text",
                question_type=q_item.get("question_type") or "unknown",
                options=q_item.get("options"),
                source_pages=pages,
                confidence=conf_score,
                extraction_status=ext_status,
                image_refs=q_item.get("image_refs")
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            total_questions += 1

            # Auto-flag for human review if low confidence or reasons present
            if ext_status in [ExtractionStatus.REVIEW_NEEDED.value, ExtractionStatus.PARTIAL.value] or reasons:
                flag_reason = "; ".join(reasons) if reasons else "Extraction flagged for quality review"
                flag = ReviewFlag(
                    question_id=question.id,
                    reason=flag_reason,
                    resolved=False
                )
                db.add(flag)
                db.commit()
                review_flags_created += 1

        # 4. Update document completion status
        doc.page_count = max_page
        doc.status = DocumentStatus.COMPLETED.value
        db.commit()

        logger.info(f"Document ID {document_id} successfully processed. Extracted {total_questions} questions, created {review_flags_created} review flags.")
        return {
            "status": "success",
            "document_id": document_id,
            "questions_extracted": total_questions,
            "review_flags_created": review_flags_created
        }

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        if 'doc' in locals() and doc:
            doc.status = DocumentStatus.FAILED.value
            db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
