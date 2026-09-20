from typing import Dict, Any, Tuple, List


class ConfidenceCalculator:
    """Calculates granular confidence score (0.0 to 1.0) and determines extraction status."""

    def evaluate(self, question_data: Dict[str, Any]) -> Tuple[float, str, List[str]]:
        """Evaluates extraction signals and returns (score, status, reasons)."""
        reasons = []
        score = 1.0

        q_num = question_data.get("question_number")
        q_text = (question_data.get("question_text") or "").strip()
        q_type = question_data.get("question_type")
        options = question_data.get("options") or []
        notes = question_data.get("extraction_notes") or ""

        # Signal 1: Missing or ambiguous question number
        if not q_num:
            score -= 0.20
            reasons.append("Missing question number header")

        # Signal 2: Short or incomplete question text
        if len(q_text) < 10:
            score -= 0.35
            reasons.append("Very short or incomplete question text")
        elif len(q_text) < 25 and not options:
            score -= 0.15
            reasons.append("Potentially truncated short answer question")

        # Signal 3: MCQ missing options
        if q_type == "mcq":
            if len(options) == 0:
                score -= 0.35
                reasons.append("MCQ question identified but no options extracted")
            elif len(options) < 2:
                score -= 0.20
                reasons.append("MCQ question has fewer than 2 extracted options")

        # Signal 4: Extraction notes flags (OCR low quality / rotation / continuation)
        if "low_quality" in notes.lower() or "scanned" in notes.lower():
            score -= 0.15
            reasons.append("Low contrast or scanned document artifact detected")

        if question_data.get("is_continuation"):
            score -= 0.05
            reasons.append("Question spans multiple pages requiring continuation merge")

        # Clamp score between 0.00 and 1.00
        final_score = round(max(0.0, min(1.0, score)), 2)

        # Classification thresholds
        if final_score >= 0.85 and len(reasons) == 0:
            status = "success"
        elif final_score >= 0.60:
            status = "partial"
        else:
            status = "review_needed"

        if status == "partial" and any("Missing" in r or "incomplete" in r for r in reasons):
            status = "review_needed"

        return final_score, status, reasons


confidence_calculator = ConfidenceCalculator()
