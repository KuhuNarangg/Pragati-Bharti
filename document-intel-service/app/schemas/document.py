from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DocumentGroupCreate(BaseModel):
    name: str


class DocumentGroupResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    group_id: Optional[int] = None
    filename: str
    doc_type: str
    status: str
    page_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentStatusResponse(BaseModel):
    id: int
    status: str
    page_count: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
