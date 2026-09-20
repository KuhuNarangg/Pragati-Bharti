from app.services.answer_matcher import answer_matcher


def test_answer_matcher_stub():
    res = answer_matcher.match_answer("What is capital of France?", "Q1", [])
    assert res["status"] == "matched"
    assert res["answer_text"] == "B. Paris"
