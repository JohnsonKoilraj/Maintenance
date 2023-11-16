from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    token: str
    f_name: Optional[str] = ""
    l_name: Optional[str] = ""
    username: str
    user_type: int
    mobile_no: Optional[str] = ""
    email_id: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""

class CreateUser(User):
    password: str


class UpdateUser(BaseModel):
    user_id: int
    token: str
    username: str
    user_type: Optional[str] = ""
    mobile_no: Optional[str] = ""
    email_id: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""
