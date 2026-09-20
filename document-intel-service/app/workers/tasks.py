import logging
from pathlib import Path
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.question import Question, ExtractionStatus
from app.models.answer import Answer, AnswerStatus
from app.models.review_flag import ReviewFlag
from app.services.extraction_service import extraction_service
from app.services.confidence import confidence_calculator
from app.services.answer_matcher import answer_matcher

logger = logging.getLogger(__name__)


@celery.task(name="process_document_task")
def process_document_task(document_id: int):
    """Async background task to process uploaded documents, extract questions/answers, evaluate confidence, and associate answer keys."""
    logger.info(f"Starting document processing for document ID: {document_id}")
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

        # 2. Process based on document type
        if doc.doc_type == DocumentType.ANSWER_KEY.value:
            # Document is an Answer Key -> Trigger matching for grouped question paper
            _process_answer_key(db, doc)
        else:
            # Document is Question Paper -> Extract questions
            _process_question_paper(db, doc)

        # 3. If part of a group, run cross-document matching
        if doc.group_id:
            _trigger_group_answer_matching(db, doc.group_id)

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


def _process_question_paper(db, doc: Document):
    extracted_data = extraction_service.extract_questions(doc.storage_path)
    max_page = 1

    for q_item in extracted_data:
        conf_score, ext_status, reasons = confidence_calculator.evaluate(q_item)
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

        # Create review flag if low confidence or issues found
        if ext_status in [ExtractionStatus.REVIEW_NEEDED.value, ExtractionStatus.PARTIAL.value] or reasons:
            flag_reason = "; ".join(reasons) if reasons else "Extraction flagged for review"
            flag = ReviewFlag(
                question_id=question.id,
                reason=flag_reason,
                resolved=False
            )
            db.add(flag)
            db.commit()

    doc.page_count = max_page


def _process_answer_key(db, doc: Document):
    # Determine page count
    doc.page_count = 1


def _trigger_group_answer_matching(db, group_id: int):
    # Find answer key doc in group
    answer_key_doc = db.query(Document).filter(
        Document.group_id == group_id,
        Document.doc_type == DocumentType.ANSWER_KEY.value,
        Document.status != DocumentStatus.FAILED.value
    ).first()

    if not answer_key_doc or not Path(answer_key_doc.storage_path).exists():
        return

    # Parse answer key entries
    entries = answer_matcher.parse_answer_key(answer_key_doc.storage_path)
    if not entries:
        return

    # Find all questions in group's question papers
    questions = db.query(Question).join(Document, Question.document_id == Document.id).filter(
        Document.group_id == group_id,
        Document.doc_type == DocumentType.QUESTION_PAPER.value
    ).all()

    for q in questions:
        match_res = answer_matcher.match_answer_for_question(q.question_number, q.question_text, entries)
        
        # Check existing answer record
        existing_ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        if existing_ans:
            existing_ans.answer_text = match_res["answer_text"]
            existing_ans.source = match_res["source"]
            existing_ans.match_confidence = match_res["match_confidence"]
            existing_ans.status = match_res["status"]
        else:
            ans = Answer(
                question_id=q.id,
                answer_text=match_res["answer_text"],
                source=match_res["source"],
                match_confidence=match_res["match_confidence"],
                status=match_res["status"]
            )
            db.add(ans)
        db.commit()
