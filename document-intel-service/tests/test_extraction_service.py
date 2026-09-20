from app.services.extraction_service import extraction_service


def test_extraction_service_stub():
    results = extraction_service.extract_questions("sample.pdf")
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]["question_number"] == "Q1"
