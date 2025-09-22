from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
import shutil, os

router = APIRouter(prefix="/news", tags=["News"])
UPLOAD_DIR = "uploads"

@router.get("/", response_model=list[schemas.NewsBase])
def get_news(db: Session = Depends(database.SessionLocal)):
    return db.query(models.News).order_by(models.News.created_at.desc()).all()

@router.post("/", response_model=schemas.NewsBase)
def create_news(news: schemas.NewsCreate, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.get_current_user)):
    new_news = models.News(title=news.title, content=news.content)
    db.add(new_news)
    db.commit()
    db.refresh(new_news)
    return new_news

@router.post("/{news_id}/files", response_model=schemas.FileBase)
def upload_file(news_id: int, file: UploadFile = File(...), db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.get_current_user)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    new_file = models.File(news_id=news_id, filename=file.filename, filepath=file_path)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file
