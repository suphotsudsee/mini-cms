import os
import shutil
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth

router = APIRouter(prefix="/news", tags=["News"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

@router.get("/", response_model=list[schemas.NewsBase])
def get_news(db: Session = Depends(database.get_db)):
    return db.query(models.News).order_by(models.News.created_at.desc()).all()

@router.post("/", response_model=schemas.NewsBase)
def create_news(news: schemas.NewsCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_news = models.News(title=news.title, content=news.content)
    db.add(new_news)
    db.commit()
    db.refresh(new_news)
    return new_news

@router.post("/{news_id}/files", response_model=schemas.FileBase)
def upload_file(news_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    target_news = db.query(models.News).filter(models.News.id == news_id).first()
    if not target_news:
        raise HTTPException(status_code=404, detail="ไม่พบบทความข่าว")

    original_name = os.path.basename(file.filename)
    if not original_name:
        raise HTTPException(status_code=400, detail="ชื่อไฟล์ไม่ถูกต้อง")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    name, ext = os.path.splitext(original_name)
    sanitized_name = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in name).strip("._") or "file"
    unique_name = f"{uuid.uuid4().hex}_{sanitized_name}{ext.lower()}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="บันทึกไฟล์ไม่สำเร็จ") from exc
    finally:
        file.file.close()

    new_file = models.File(news_id=news_id, filename=original_name, filepath=file_path)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file
