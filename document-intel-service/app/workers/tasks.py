import logging
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models.document import Document, DocumentStatus

logger = logging.getLogger(__name__)


@celery.task(name="process_document_task")
def process_document_task(document_id: int):
    """Async background task to process uploaded documents."""
    logger.info(f"Starting async processing for document ID: {document_id}")
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document ID {document_id} not found.")
            return {"status": "error", "message": "Document not found"}

        doc.status = DocumentStatus.PROCESSING.value
        db.commit()

        # Document processing logic (Stubbed for Phase 0/1)
        doc.status = DocumentStatus.COMPLETED.value
        db.commit()

        logger.info(f"Document ID {document_id} processed successfully.")
        return {"status": "success", "document_id": document_id}

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        if 'doc' in locals() and doc:
            doc.status = DocumentStatus.FAILED.value
            db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
