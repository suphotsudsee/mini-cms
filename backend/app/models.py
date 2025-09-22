import os

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(128))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    files = relationship("File", back_populates="news")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"))
    filename = Column(String(200))
    filepath = Column(String(300))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    news = relationship("News", back_populates="files")

    @property
    def is_image(self) -> bool:
        """Return True when the stored file is likely an image."""
        if not self.filename:
            return False
        _, ext = os.path.splitext(self.filename.lower())
        return ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"}
