from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from .. import database, models, auth, schemas

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/token")
def login_form(form: OAuth2PasswordRequestForm = Depends(),
               db: Session = Depends(database.SessionLocal)):
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not auth.verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth.create_access_token(data={"sub": user.username}, expires_delta=expires)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
def login_json(payload: schemas.UserLogin,
               db: Session = Depends(database.SessionLocal)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth.create_access_token(data={"sub": user.username}, expires_delta=expires)
    return {"access_token": token, "token_type": "bearer"}
