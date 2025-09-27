import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
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


@router.put("/{news_id}", response_model=schemas.NewsBase)
def update_news(
    news_id: int,
    news: schemas.NewsUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    target_news = db.query(models.News).filter(models.News.id == news_id).first()
    if not target_news:
        raise HTTPException(status_code=404, detail="ไม่พบบทความข่าว")

    has_changes = False

    if news.title is not None:
        cleaned_title = news.title.strip()
        if not cleaned_title:
            raise HTTPException(status_code=400, detail="หัวข้อข่าวต้องไม่ว่าง")
        target_news.title = cleaned_title
        has_changes = True

    if news.content is not None:
        cleaned_content = news.content.strip()
        if not cleaned_content:
            raise HTTPException(status_code=400, detail="เนื้อหาข่าวต้องไม่ว่าง")
        target_news.content = cleaned_content
        has_changes = True

    if not has_changes:
        raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่ต้องการอัปเดต")

    db.commit()
    db.refresh(target_news)
    return target_news

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


@router.delete("/{news_id}", status_code=204)
def delete_news(
    news_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    target_news = db.query(models.News).filter(models.News.id == news_id).first()
    if not target_news:
        raise HTTPException(status_code=404, detail="ไม่พบบทความข่าว")

    file_paths = [file.filepath for file in target_news.files]

    db.delete(target_news)
    db.commit()

    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                continue

    return Response(status_code=204)
