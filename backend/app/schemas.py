from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FileBase(BaseModel):
    id: int
    filename: str
    filepath: str
    uploaded_at: datetime
    is_image: bool = False

    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    files: List[FileBase] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NewsCreate(BaseModel):
    title: str
    content: str


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str
