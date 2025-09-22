from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    files: List[FileBase] = []
    class Config:
        from_attributes = True

class NewsCreate(BaseModel):
    title: str
    content: str

class UserLogin(BaseModel):
    username: str
    password: str
local_kw: Optional[str] = None  # ✅ ไม่ต้องส่งมาก็ได้