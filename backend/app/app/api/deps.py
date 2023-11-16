from typing import Generator, Any, Optional
from fastapi.security import OAuth2PasswordBearer
import datetime
from sqlalchemy.orm import Session
from app import models
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from datetime import datetime
import hashlib
from app.models import User, ApiTokens
from app.core.config import settings
from app.models import *
from sqlalchemy import or_
import sys, shutil

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_by_user(db: Session, *, username: str) -> Optional[models.User]:
    return (
        db.query(models.User)
        .filter(models.User.username == username, models.User.status != -1)
        .first()
    )


def get_user_token(db: Session, *, token: str) -> Optional[models.User]:
    get_token = (
        db.query(ApiTokens)
        .filter(ApiTokens.token == token, ApiTokens.status == 1)
        .first()
    )
    if get_token:
        return (
            db.query(models.User)
            .filter(models.User.id == get_token.user_id, models.User.status != -1)
            .first()
        )
    else:
        return None




def authenticate(
    db: Session, *, username: str, password: str, authcode: str, auth_text: str
) -> Optional[models.User]:
    user = get_by_user(db, username=username)
    if not user or user.password == None:
        return None

    if not security.check_authcode(authcode, auth_text):

        return None

    if not security.verify_password(password, user.password):
        return None
    return user


def is_active(user: models.User):
    if user.status == 1:
        return user.status
    else:
        return None


def get(db: Session, id: Any) -> Optional[models.User]:
    user = (
        db.query(
            models.User.id,
            models.User.username,
            models.User.user_type,
            models.User.mobile_no,
            models.User.password,
            models.User.email_id,
            models.User.status
        )
        .filter(models.User.id == id, models.User.status != -1)
        .first()
    )
    return user


def get_user(db: Session, user_id: Any):
    if user_id:
        user = (
            db.query(models.User)
            .filter(models.User.id == user_id, models.User.status != -1)
            .first()
        )
        if user:
            return user.username
        else:
            return None
    else:
        return None


import re


def verify_hash(hash_data: str, included_variable: str):
    included_variable = (included_variable + settings.SALT_KEY).encode("utf-8")
    real_hash = hashlib.sha1(included_variable).hexdigest()
    if hash_data == real_hash:
        return True

    return False


def hms_to_s(s):
    t = 0
    for u in s.split(":"):
        t = 60 * t + int(u)
    return t

import os

def upload_file(uploaded_file, custom_filename: str = ""):
    base_dir = settings.BASE_UPLOAD_FOLDER + "/upload_files"

    dt = str(int(datetime.utcnow().timestamp()))

    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=base_dir, err=e))

    output_dir = base_dir + "/"

    org_filename = uploaded_file.filename

    # Split file name and extension
    splitted_name = org_filename.split(".")
    extension = (splitted_name[::-1])[0]
    doc_name = splitted_name[0]

    if len(splitted_name) > 2:
        return {"status": 0, "msg": "File name invalid. It should be like sample.bin"}

    if extension != "bin":
        return {"status": 0, "msg": "Only binary files are allowed"}

    filename = (
        org_filename
        if not custom_filename
        else f"{custom_filename.replace('.bin', '')}.bin"
    )

    file_path = f"{output_dir}{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return {"status": 1, "msg": "success", "file_name": filename}
