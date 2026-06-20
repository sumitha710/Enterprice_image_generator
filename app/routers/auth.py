from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.schemas.auth import (
    RegisterSchema,
    LoginSchema
)

from app.models.user import User

from app.core.dependencies import get_db

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(
    request:RegisterSchema,
    db:Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        name=request.name,
        email=request.email,
        password=hash_password(
            request.password
        )
    )

    db.add(new_user)
    db.commit()

    return {
        "message":"User Registered"
    }

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }