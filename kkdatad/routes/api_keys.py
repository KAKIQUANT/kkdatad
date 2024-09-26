# In your routes file, e.g., kkdatad/routes/api_keys.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4
from kkdatad.auth import get_current_user, get_password_hash
from kkdatad.database import SessionLocal
import kkdatad.models as models

api_keys_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class APIKeyCreateResponse(BaseModel):
    api_key: str

@api_keys_router.post("/api-keys", response_model=APIKeyCreateResponse)
def create_api_key(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Generate raw API key
    raw_key = str(uuid4())
    hashed_key = get_password_hash(raw_key)

    # Save hashed API key
    db_api_key = models.APIKey(
        key=hashed_key,
        user_id=current_user.id
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)

    return {"api_key": raw_key}

@api_keys_router.get("/api-keys")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    api_keys = db.query(models.APIKey).filter_by(user_id=current_user.id, is_active=True).all()
    return [
        {"id": key.id, "created_at": key.created_at}
        for key in api_keys
    ]

@api_keys_router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    api_key = db.query(models.APIKey).filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key or not api_key.is_active:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.is_active = False
    db.commit()
    return {"detail": "API key revoked"}

