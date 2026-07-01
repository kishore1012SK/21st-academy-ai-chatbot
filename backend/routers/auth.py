from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from limiter import limiter

from database.db import get_db
from database.models import User
from schemas import LoginRequest, LoginResponse
from auth_utils import verify_password, create_access_token
from config import settings

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id, "email": user.email, "is_admin": user.is_admin})
    return LoginResponse(success=True, access_token=token)
