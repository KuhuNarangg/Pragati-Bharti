import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.config import settings


class StorageService:
    def __init__(self, base_dir: str = settings.STORAGE_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_document(self, user_id: int, document_id: int, file: UploadFile) -> str:
        user_doc_dir = self.base_dir / str(user_id) / str(document_id)
        user_doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Safe filename
        safe_filename = Path(file.filename).name
        file_path = user_doc_dir / safe_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return str(file_path)

    def delete_document(self, storage_path: str) -> bool:
        path = Path(storage_path)
        if path.exists():
            if path.is_file():
                path.unlink()
                # Try to clean up parent directory if empty
                parent = path.parent
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
            elif path.is_dir():
                shutil.rmtree(path)
            return True
        return False


storage_service = StorageService()
