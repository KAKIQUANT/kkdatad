from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from kkdatad.database import SessionLocal
from sqlalchemy.orm import Session
import kkdatad.models as models
from datetime import datetime, timedelta
import redis

# Constants and configurations
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Redis client for token blacklisting
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password for storing."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default token expiration time
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def invalidate_token(token: str):
    """Invalidate a JWT token by adding it to the blacklist."""
    try:
        # Decode the token to get its expiration time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration = payload.get("exp")
        if expiration:
            # Calculate the time-to-live for the token
            ttl = expiration - int(datetime.utcnow().timestamp())
            # Add the token to the blacklist in Redis
            redis_client.setex(f"blacklist:{token}", ttl, "true")
    except JWTError:
        # If token is invalid, do nothing or log the error
        pass

def is_token_blacklisted(token: str):
    """Check if a token is blacklisted."""
    return redis_client.exists(f"blacklist:{token}")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retrieve the current user based on the JWT token."""
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Retrieve user from the database
    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(username=username).first()
    finally:
        db.close()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def verify_token(token):
    """Verify if a token is valid and not blacklisted."""
    if is_token_blacklisted(token):
        return False
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except JWTError:
        return False

async def get_api_key_user(
    request: Request,
    db: Session = Depends(get_db)
):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing",
            headers={"WWW-Authenticate": "APIKey"},
        )
    hashed_key = get_password_hash(api_key)
    api_key_entry = db.query(models.APIKey).filter_by(key=hashed_key, is_active=True).first()
    if not api_key_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return api_key_entry.user