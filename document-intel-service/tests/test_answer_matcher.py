from app.services.answer_matcher import answer_matcher


def test_answer_matcher_by_number():
    entries = [
        {"question_number": "Q1", "raw_number": "1", "answer_text": "A. Operating system kernel", "source_page": 1},
        {"question_number": "Q2", "raw_number": "2", "answer_text": "B. Processes have isolated memory space", "source_page": 1}
    ]

    res = answer_matcher.match_answer_for_question("Q1", "What is kernel?", entries)
    assert res["status"] == "matched"
    assert res["answer_text"] == "A. Operating system kernel"
    assert res["match_confidence"] == 0.95


def test_answer_matcher_unmatched():
    entries = [
        {"question_number": "Q10", "raw_number": "10", "answer_text": "Random Answer", "source_page": 1}
    ]

    res = answer_matcher.match_answer_for_question("Q1", "Unrelated question", entries)
    assert res["status"] == "unmatched"
    assert res["match_confidence"] is None
    assert "no confident match" in res["answer_text"].lower()
