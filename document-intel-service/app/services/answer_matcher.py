import re
import difflib
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF


class AnswerMatcher:
    """Extracts answer key data and matches answers with extracted questions."""

    # Patterns for Answer Key Entries: Q1: A..., 1) B..., Q.1 - Answer text
    ANSWER_KEY_PATTERN = re.compile(
        r'^(?:Q(?:uestion)?\.?\s*(\d+[a-z]?)|(\d+)[\.\:\)])\s*[\:\-\s]\s*(.*)',
        re.IGNORECASE
    )

    def parse_answer_key(self, answer_key_path: str) -> List[Dict[str, Any]]:
        path = Path(answer_key_path)
        if not path.exists():
            return []

        entries = []
        try:
            doc = fitz.open(path)
            for page_num in range(len(doc)):
                text = doc[page_num].get_text("text") or ""
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                for line in lines:
                    match = self.ANSWER_KEY_PATTERN.match(line)
                    if match:
                        q_num_val = match.group(1) or match.group(2)
                        ans_text = match.group(3) or ""
                        q_num_str = f"Q{q_num_val}" if q_num_val else None

                        entries.append({
                            "question_number": q_num_str,
                            "raw_number": q_num_val,
                            "answer_text": ans_text.strip(),
                            "source_page": page_num + 1
                        })
            doc.close()
        except Exception:
            pass

        return entries

    def match_answer_for_question(
        self,
        question_number: Optional[str],
        question_text: str,
        answer_key_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Matches a single question against answer key entries."""
        if not answer_key_entries:
            return {
                "answer_text": "No confident match found",
                "source": None,
                "match_confidence": None,
                "status": "unmatched"
            }

        # 1. Primary Strategy: Match by Question Number
        if question_number:
            clean_q_num = re.sub(r'[^\d]', '', question_number)
            for entry in answer_key_entries:
                entry_q_num = re.sub(r'[^\d]', '', entry.get("question_number") or "")
                if clean_q_num and clean_q_num == entry_q_num:
                    return {
                        "answer_text": entry["answer_text"],
                        "source": f"Answer Key Page {entry['source_page']}",
                        "match_confidence": 0.95,
                        "status": "matched"
                    }

        # 2. Secondary Strategy: Fuzzy Text Similarity
        best_entry = None
        best_ratio = 0.0

        for entry in answer_key_entries:
            ans_text = entry["answer_text"]
            ratio = difflib.SequenceMatcher(None, question_text.lower(), ans_text.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_entry = entry

        # Threshold check: Never guess an answer if confidence is below 0.65
        if best_entry and best_ratio >= 0.65:
            return {
                "answer_text": best_entry["answer_text"],
                "source": f"Answer Key Page {best_entry['source_page']}",
                "match_confidence": round(best_ratio, 2),
                "status": "matched"
            }

        # Insufficient confidence -> Explicitly return unmatched
        return {
            "answer_text": "No confident match found",
            "source": None,
            "match_confidence": None,
            "status": "unmatched"
        }


answer_matcher = AnswerMatcher()
