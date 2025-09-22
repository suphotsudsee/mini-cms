from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas

router = APIRouter(prefix="/auth", tags=["Auth"])

def _authenticate_and_issue_token(db: Session, username: str, password: str) -> dict:
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth.create_access_token(data={"sub": user.username}, expires_delta=expires)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token")
async def login_form(request: Request,
                     db: Session = Depends(database.get_db)):
    """Accept login credentials via form data or JSON payloads."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = schemas.UserLogin(**await request.json())
        return _authenticate_and_issue_token(db, payload.username, payload.password)

    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return _authenticate_and_issue_token(db, username, password)


@router.post("/login")
def login_json(payload: schemas.UserLogin,
               db: Session = Depends(database.get_db)):
    return _authenticate_and_issue_token(db, payload.username, payload.password)
