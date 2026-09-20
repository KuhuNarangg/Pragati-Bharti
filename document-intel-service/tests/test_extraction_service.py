from pathlib import Path
from app.services.extraction_service import extraction_service
from app.services.confidence import confidence_calculator


def test_pdf_question_extraction():
    sample_pdf = Path("sample_documents/clean_question_paper.pdf")
    assert sample_pdf.exists()

    questions = extraction_service.extract_questions(str(sample_pdf))
    assert isinstance(questions, list)
    assert len(questions) >= 3

    # Q1 verification
    q1 = questions[0]
    assert q1["question_number"] == "Q1"
    assert "operating system kernel" in q1["question_text"]
    assert q1["question_type"] == "mcq"
    assert len(q1["options"]) == 4

    # Multi-page continuation verification for Q2
    q2 = [q for q in questions if q.get("question_number") == "Q2"][0]
    assert q2["is_continuation"] is True
    assert 1 in q2["source_pages"] and 2 in q2["source_pages"]


def test_confidence_calculator():
    q_good = {
        "question_number": "Q1",
        "question_text": "What is the primary function of RAM in a computer system?",
        "question_type": "mcq",
        "options": ["A. Volatile memory", "B. Secondary storage", "C. Power unit", "D. Network adapter"],
        "source_pages": [1]
    }
    score, status, reasons = confidence_calculator.evaluate(q_good)
    assert score >= 0.85
    assert status == "success"

    q_incomplete = {
        "question_number": None,
        "question_text": "Short",
        "question_type": "mcq",
        "options": [],
        "source_pages": [1]
    }
    score_low, status_low, reasons_low = confidence_calculator.evaluate(q_incomplete)
    assert score_low < 0.60
    assert status_low == "review_needed"
    assert len(reasons_low) > 0
