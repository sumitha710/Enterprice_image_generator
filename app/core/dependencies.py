from jose import jwt
from jose import JWTError

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import (
    SECRET_KEY,
    ALGORITHM
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

def get_current_user(
    token:str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user