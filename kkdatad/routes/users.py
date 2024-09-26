from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from kkdatad.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    invalidate_token,
    oauth2_scheme
)
from fastapi.responses import JSONResponse
from kkdatad.utils.database import SessionLocal
import kkdatad.utils.models as models

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
    invite_code: str | None = None



class UserRes(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    email: str | None = None
    isadmin: bool = False

class UpdateUserForm(BaseModel):
    nickname: str | None = None
    email: str | None = None
    # password: str | None = None  # Uncomment if allowing password changes

@user_router.post("/register")
def register(user: RegisterForm, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(models.User).filter_by(username=user.username).first()
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "msg": "用户已存在"},
        )

    # If an invite code is provided, validate it
    if user.invite_code:
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
    # After marking the invite code as used
    if user.invite_code:
        # Grant additional privileges
        db_user.is_premium = True

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return JSONResponse({"code": 0, "msg": "注册成功"})



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
        created_by=current_user.id,
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

@user_router.put("/users/update")
def update_user_info(
    user_update: UpdateUserForm,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.nickname is not None:
        user.nickname = user_update.nickname
    if user_update.email is not None:
        user.email = user_update.email
    # if user_update.password is not None:
    #     user.password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)

    return {
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "isadmin": user.isadmin,
    }

@user_router.get("/users/api-quota")
def get_api_quota(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    api_usage = db.query(models.APIUsage).filter_by(user_id=current_user.id).first()
    if not api_usage:
        # Initialize API usage if not exists
        api_usage = models.APIUsage(user_id=current_user.id)
        db.add(api_usage)
        db.commit()
        db.refresh(api_usage)

    return {
        "totalQuota": api_usage.total_quota,
        "usedQuota": api_usage.used_quota,
    }


@user_router.get("/users/info", response_model=UserRes)
async def read_users_me(current_user: UserRes = Depends(get_current_user)):
    return current_user
