from uuid import uuid4
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from kkdatad.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    invalidate_token,
    oauth2_scheme
)
from fastapi.responses import JSONResponse
from kkdatad.database import SessionLocal
import kkdatad.models as models

user_router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RegisterForm(BaseModel):
    username: str
    password: str
    invite_code: str



class UserRes(BaseModel):
    username: str
    nickname: str | None = None
    email: str | None = None
    isadmin: bool = False


@user_router.post("/register")
def register(user: RegisterForm, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(models.User).filter_by(username=user.username).first()
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "msg": "User already exists"},
        )

    # Validate the invite code
    invite_code = db.query(models.InviteCode).filter_by(code=user.invite_code, is_used=False).first()
    if not invite_code:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "msg": "Invalid or used invite code"},
        )

    # Mark the invite code as used
    invite_code.is_used = True
    db.commit()

    # Create the new user
    db_user = models.User(
        username=user.username,
        password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return JSONResponse({"code": 0, "msg": "Register success"})



class LoginForm(BaseModel):
    username: str
    password: str


@user_router.post("/login")
def login(form: LoginForm, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return JSONResponse(
        {"code": 0, "msg": "Login Success", "access_token": access_token}
    )


@user_router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    invalidate_token(token)
    return JSONResponse({"code": 0, "msg": "登出成功"})


@user_router.post("/gen-invite-code")
def generate_invite_code(
    current_user: UserRes = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Generate a unique invite code
    invite_code = str(uuid4())

    # Create a new InviteCode object
    db_invite_code = models.InviteCode(
        code=invite_code,
        created_by=current_user.username,
        is_used=False,
    )

    # Save the invite code to the database
    db.add(db_invite_code)
    db.commit()
    db.refresh(db_invite_code)

    return JSONResponse(
        {
            "code": 0,
            "msg": "Invite code generated successfully",
            "invite_code": invite_code,
        }
    )


@user_router.get("/users/info", response_model=UserRes)
async def read_users_me(current_user: UserRes = Depends(get_current_user)):
    return current_user
