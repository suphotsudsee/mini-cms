from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database, auth
from .routers import news, auth as auth_router
from sqlalchemy.orm import Session
import os

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

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

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
