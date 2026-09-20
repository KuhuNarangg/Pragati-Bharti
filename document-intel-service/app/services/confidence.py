from typing import Dict, Any, Tuple


class ConfidenceCalculator:
    """Calculates confidence score (0.0 to 1.0) and extraction status for extracted questions."""

    def evaluate(self, question_data: Dict[str, Any]) -> Tuple[float, str, list]:
        """Returns (confidence_score, extraction_status, review_reasons)."""
        reasons = []
        score = 1.0

        if not question_data.get("question_number"):
            score -= 0.2
            reasons.append("Missing question number")

        if not question_data.get("question_text") or len(question_data.get("question_text", "").strip()) < 5:
            score -= 0.4
            reasons.append("Incomplete or short question text")

        if question_data.get("question_type") == "mcq" and not question_data.get("options"):
            score -= 0.3
            reasons.append("MCQ question missing options")

        score = max(0.0, min(1.0, round(score, 2)))

        if score >= 0.85:
            status = "success"
        elif score >= 0.6:
            status = "partial"
        else:
            status = "review_needed"

        return score, status, reasons


confidence_calculator = ConfidenceCalculator()
