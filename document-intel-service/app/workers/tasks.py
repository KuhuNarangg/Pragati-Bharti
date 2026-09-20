import logging
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
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

        # 1. Update status to processing
        doc.status = DocumentStatus.PROCESSING.value
        db.commit()

        # 2. Inspect document and get page count
        file_path = Path(doc.storage_path)
        page_count = 0

        if file_path.exists():
            if file_path.suffix.lower() == ".pdf":
                try:
                    pdf_doc = fitz.open(file_path)
                    page_count = len(pdf_doc)
                    pdf_doc.close()
                except Exception as pdf_err:
                    logger.warning(f"PyMuPDF error reading page count: {pdf_err}")
                    page_count = 1
            elif file_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                page_count = 1

        doc.page_count = page_count
        doc.status = DocumentStatus.COMPLETED.value
        db.commit()

        logger.info(f"Document ID {document_id} processed successfully. Total pages: {page_count}")
        return {"status": "success", "document_id": document_id, "page_count": page_count}

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        if 'doc' in locals() and doc:
            doc.status = DocumentStatus.FAILED.value
            db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
