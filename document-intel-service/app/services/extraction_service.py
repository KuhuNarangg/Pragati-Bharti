from typing import List, Dict, Any


class ExtractionService:
    """Service interface for extracting questions from documents (PDFs/Images)."""
    
    def extract_questions(self, file_path: str) -> List[Dict[str, Any]]:
        # Phase 0/1 stub: Returns controlled mock question data
        return [
            {
                "question_number": "Q1",
                "question_text": "What is the capital of France?",
                "question_type": "mcq",
                "options": ["A. London", "B. Paris", "C. Berlin", "D. Madrid"],
                "source_pages": [1],
                "confidence": 0.95,
                "extraction_notes": "Clean extraction",
                "is_continuation": False
            }
        ]


extraction_service = ExtractionService()
