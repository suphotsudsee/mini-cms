import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, database, auth
from .routers import news, auth as auth_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Mini CMS Backend",
    description="API สำหรับจัดการข่าวและประกาศ พร้อมแนบไฟล์ดาวน์โหลด",
    version="1.0.0",
    contact={
        "name": "Admin",
        "url": "http://localhost:8000",
        "email": "admin@example.com",
    }
)

# รวบรวมรายการ origin ที่อนุญาตให้ frontend เรียกใช้งาน API ได้
# ค่าพื้นฐานจะครอบคลุมการพัฒนาในเครื่องทั่วไป และสามารถปรับเพิ่มได้ผ่าน
# ตัวแปรสภาพแวดล้อม `CORS_ALLOW_ORIGINS` (คั่นด้วยเครื่องหมายจุลภาค)
default_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
}

extra_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
if extra_origins:
    # ตัดช่องว่างและละเว้นค่าเปล่า เพื่อป้องกัน header ที่ไม่ถูกต้อง
    default_origins.update({origin.strip() for origin in extra_origins.split(",") if origin.strip()})

origins = sorted(default_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# รวม router
app.include_router(auth_router.router)
app.include_router(news.router)

upload_dir = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.on_event("startup")
def init_admin():
    db: Session = database.SessionLocal()
    username = os.getenv("ADMIN_USER", "admin")
    password = os.getenv("ADMIN_PASS", "admin123")

    # ถ้าไม่มี user → สร้าง admin
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        hashed_pw = auth.get_password_hash(password)
        new_user = models.User(username=username, password_hash=hashed_pw)
        db.add(new_user)
        db.commit()
        print(f"✅ Created default admin user → {username}:{password}")
    else:
        print(f"ℹ️ Admin user '{username}' already exists.")
    db.close()

@app.get("/", tags=["Root"])
def root():
    return {"message": "Mini CMS Backend Running! ไปที่ /docs เพื่อดู Swagger UI"}
