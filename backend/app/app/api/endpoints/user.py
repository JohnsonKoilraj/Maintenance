from fastapi import APIRouter, Depends, HTTPException, Form
from app import crud, schemas
from app.models import User
from fastapi.encoders import jsonable_encoder
from app.api import deps
from app.utils import pagination
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import *
from datetime import datetime
from sqlalchemy import or_


router = APIRouter()


@router.post("/create_user")
async def create_user(
    *, db: Session = Depends(deps.get_db),
     create_users: schemas.user.CreateUser
):
    user = deps.get_user_token(db=db, token=create_users.token)
    if user:
        if user.user_type in [1,2,3,4]:
            data = jsonable_encoder(create_users)

            email = (data["email_id"]).strip()
            mobile_no = data["mobile_no"].strip()
            username = data["username"].strip()

            if username:
                existing_username = (
                    db.query(User)
                    .filter(User.username == username, User.status == 1)
                    .first()
                )
                if existing_username:
                    return {"status": 0, "msg": "Username Already Present."}

            if email:
                db_user = crud.user.check_email(email=email, db=db)
                if db_user:
                    return {"status": 0, "msg": "Email Id Already Present."}

            if mobile_no:
                if crud.user.check_mobile(db=db, mobile=mobile_no):
                    return {"status": 0, "msg": "Mobile_no Already Present."}

            user_create = crud.user.create(
                db, new_user=create_users,creator_id=user.id
            )

            if user_create:
                return {"status": 1, "msg": "User Created Successfully"}

            else:
                return {"status": 0, "msg": "Something went worng!"}

        else:
            return {"status": 0, "msg": "Invalid access"}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


# is active
@router.post("/update_status")
async def update_status(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    user_id: int = Form(...),
    active: int = Form(..., description="1->active,0->inactive"),
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1, 2,3,4]:
            check_user = db.query(User).filter(
                User.id == user_id).first()
            
            if check_user.status == 1 and active == 0:
                check_user.status = 0
                db.commit()
                return {"status": 1, "msg": "Successfully Deactivated"}
            elif check_user.status == 0 and active == 1:
                check_user.status = 1
                db.commit()
                return {"status": 1, "msg": "Successfully Activated"}
            else:
                return {"status": 0, "msg": "Failed"}
        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


@router.get("/view_profile/{User_id}")
async def view_profile(*,db:Session=Depends(deps.get_db),
                           token: str , 
                       user_id:int):
    
    user = deps.get_user_token(db=db, token=token)
    
    if user:
        get_user=db.query(User).filter(
            User.id == user_id,User.status == 1).first()
        profile={}
        if get_user:
            profile.update({"user_name":get_user.username
                                if get_user.username else "",
                            "mobile_no":get_user.mobile_no 
                            if get_user.mobile_no else "",
                            "email_id":get_user.email_id 
                            if get_user.email_id else "",
                            "address":get_user.address 
                            if get_user.address else "",
                            "created_at":get_user.created_at
                            })

        
            return {"status": 1, "msg": "Success", "data": profile}
        else:
            raise HTTPException(
                status_code=400,
                detail=[{"msg":"User not found"}])
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


# list_user
@router.post("/list_user")
async def list_user(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    page: int = 1,
    size: int = 10,
    username: str=Form(None),
    usertype:int=Form(None)
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        list_user = db.query(User).filter(User.status != -1)
        if username:
            list_user = list_user.filter(
                    User.username.like("%" + username + "%")
                   )
        if usertype:
            list_user = list_user.filter(
                    User.user_type==usertype
                   )
            
        list_user = list_user.order_by(User.id.desc())
        list_user_count = list_user.count()
        limit, offset = pagination(list_user_count, page, size)
        list_user = list_user.limit(limit).offset(offset).all()

        user_data = []

        for row in list_user:
            user_data.append(
                {
                    "user_id": row.id,
                    "f_name": row.f_name if row.f_name else "",
                    "l_name": row.l_name if row.l_name else "",
                    "username": row.username
                    if row.username
                    else row.f_name + " " + row.l_name,
                    "mobile_no": row.mobile_no,
                    "email": row.email_id if row.email_id else "",
                    "created_by": row.created_by if row.created_by else "",
                    "user_type": row.user_type if row.user_type else "",
                    "city": row.city if row.city else "",
                    "state": row.state if row.state else "",
                    "country": row.country if row.country else "",
                    "address": row.address if row.address else ""
                }
            )

        data = {
            "page": page,
            "size": size,
            "total": list_user_count,
            "items": user_data,
        }

        return {"status": 1, "msg": "Success", "data": data}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }



@router.put("/update_user")
async def update_user(
    *, db: Session = Depends(deps.get_db), 
    request: schemas.UpdateUser
):
    data = jsonable_encoder(request)
    token = data["token"]
    user = deps.get_user_token(db=db, token=token)

    if user:
        if user.user_type in [1,2,3,4]:
            user_id = data["user_id"]

            username = data["username"].strip()

            if username:
                existing_username = (
                    db.query(User)
                    .filter(
                        User.username == username, 
                        User.id != user_id, 
                        User.status == 1
                    )
                    .first()
                )
                if existing_username:
                    return {"status": 0, "msg": "Username Already Present."}

            email = data["email_id"].strip()
            if email:
                db_user_email = (
                    db.query(User)
                    .filter(
                        User.email_id == email,
                        User.id != user_id,
                        User.status == 1,
                        User.email_id != None,
                    )
                    .first()
                )
                if db_user_email:
                    return {"status": 0, "msg": "E-Mail Id Already Present."}

            mobile_no = data["mobile_no"].strip()
            if mobile_no:
                db_user_mobile_no = (
                    db.query(User)
                    .filter(
                        User.mobile_no == mobile_no,
                        User.id != user_id,
                        User.status == 1,
                        User.mobile_no != None,
                    )
                    .first()
                )
                if db_user_mobile_no:
                    return {"status": 0, "msg": "Mobile_no Already Present."}

  
            get_user = (
                db.query(User).filter(User.id == user_id, 
                                      User.status == 1).first()
            )

            if get_user:
                get_user.username = data["username"] if data["username"] else ""
                get_user.email_id = data["email_id"] if data["email_id"] else ""
                get_user.address = data["address"] if data["address"] else None
                get_user.mobile_no = mobile_no if mobile_no else None
                get_user.updated_at = datetime.now(settings.tz_IN)
                get_user.country = data["country"] if data["country"].strip() else None

                get_user.user_type = (
                    data["user_type"] if data["user_type"] else None
                )
                get_user.state = data["state"] if data["state"] else None
                get_user.city = data["city"] if data["city"] else None

                db.commit()
                return {"status": 1, "msg": "Updated Successfully"}
            else:
                return {"status": 0, "msg": "User Not Found"}

        else:
            return {"status": 0, "msg": "Not Authenticated"}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


# Delete


@router.post("/delete_user")
async def delete_user(
    db: Session = Depends(deps.get_db), token: str = Form(...), 
    user_id: int = Form(...)
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1, 2]:
            check_user = (
                db.query(User)
                .filter(User.id == user_id, or_(User.status == 1, 
                                                User.status == 0))
                .first()
            )
            if check_user:
                check_user.status = -1
                db.commit()
                return {"status": 1, "msg": "user account Deleted"}
            else:
                return {"status": 0, "msg": "Invalid User Id"}
        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }

