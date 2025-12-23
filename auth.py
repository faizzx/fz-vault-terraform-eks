# auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-for-dev-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup password hashing (Bcrypt is the industry standard)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Checks if the provided password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generates a secure hash of a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a JWT token for a user session."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


from sqlalchemy.orm import Session
import models


def authenticate_user(db: Session, username: str, password: str):
    # 1. Look for the user in the database
    user = db.query(models.User).filter(models.User.username == username).first()

    # 2. If user doesn't exist, return False
    if not user:
        return False

    # 3. Use our verify_password function to check the Argon2 hash
    if not verify_password(password, user.hashed_password):
        return False

    # 4. If everything matches, return the user object
    return user