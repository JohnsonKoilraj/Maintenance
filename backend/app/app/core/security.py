from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"

def check_authcode(authcode: str, auth_text: str):
    salt = settings.SALT_KEY
    auth_text = salt + auth_text
    result = hashlib.sha1(auth_text.encode())
    print(result.hexdigest())
    if authcode == result.hexdigest():
        return True
    else:
        return None

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


def verify_password(plain_password: str, hashed_password: str):
    result = hashlib.sha1(plain_password.encode())
    if hashed_password == result.hexdigest():
        return True
    else:
        return None


def get_password_hash(password: str):
    result = hashlib.sha1(password.encode())
    return result.hexdigest()

