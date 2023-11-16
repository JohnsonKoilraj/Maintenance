from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user import CreateUser, UpdateUser
from app import schemas
from typing import Any, TypeVar
from pydantic import BaseModel
import shutil
from fastapi import File, UploadFile
from datetime import datetime
from app.core.security import get_password_hash
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
import random


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    # def get_by_contact_number(self,db:Session,contact_number:int):

    #     return db.query(User).filter(User.mobile_no==contact_number,User.status!=1).first()

    # def get_user_by_email(self,username:str,db:Session):

    #     return db.query(User).filter(User.mobile_no==username).first()

    def check_email(self, email: str, db: Session):
        return db.query(User).filter(User.email_id == email, User.status == 1).first()

    def check_mobile(self, db: Session, mobile: str):
        return db.query(User).filter(User.mobile_no == mobile, User.status == 1).first()

    def create(
        self,
        db: Session,
        *,
        new_user: schemas.user.CreateUser,
        creator_id: str = None
    ):
        obj_in_data = jsonable_encoder(new_user)
        pwd = obj_in_data.pop("password")
        token = obj_in_data.pop("token")
        db_obj = self.model(
            **obj_in_data,
            status=1,
            created_at=datetime.now(settings.tz_IN),
            password=get_password_hash(pwd),
            created_by=creator_id
             
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
