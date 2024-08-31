"""
User Registration Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from pydantic import BaseModel
from kkdatad.auth import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi.responses import JSONResponse
from kkdatad.database import SessionLocal
import kkdatad.models as models
from kkdatad.status import status
user_router = APIRouter()

class RegisterForm(BaseModel):
    username: str
    password: str

@user_router.post("/register")
def register(user: RegisterForm):
    if SessionLocal().query(models.User).filter_by(username=user.username).count() > 0:
        return JSONResponse({
            "code": 400,
            "msg": "用户已存在"
        })
    db_user = models.User(username=user.username, password=get_password_hash(user.password))
    with SessionLocal.begin() as session:
        session.add(db_user)
    return JSONResponse({
            "code": 0,
            "msg": "注册成功"
        })

class LoginForm(BaseModel):
    username: str
    password: str

@user_router.post("/login")
def login(form:LoginForm):
    user = SessionLocal().query(models.User).filter_by(username = form.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    response = JSONResponse({
            "code": 0,
            "msg": "登录成功",
            "access_token": access_token
        })
    return response

class UserRes(BaseModel):
    username: str
    nickname: str | None = None
    email: str | None = None
    isadmin: bool | None = False

@user_router.get("/users/info", response_model=UserRes)
async def read_users_me(current_user: UserRes = Depends(get_current_user)):
    return current_user