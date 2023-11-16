from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.models import User, ApiTokens
from app.models import ApiTokens, User
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from datetime import datetime
from fastapi import Request

import random


router = APIRouter()
dt = str(int(datetime.utcnow().timestamp()))


# Check Token
@router.post("/check_token")
async def check_token(*, db: Session = Depends(deps.get_db), token: str = Form(...)):
    check_token = (
        db.query(ApiTokens)
        .filter(ApiTokens.token == token, ApiTokens.status == 1)
        .first()
    )
    if check_token:
        return {"status": 1}
    else:
        return {"status": 0}


# 1.Login
@router.post("/login")
async def login(
    *,
    db: Session = Depends(deps.get_db),
    authcode: str = Form(None),
    username: str = Form(...),
    password: str = Form(...),
    device_id: str = Form(None),
    device_type: int = Form(..., description="1-android,2-ios"),
    push_id: str = Form(None),
    request: Request
):
    ip = request.client.host
    if device_id:
        auth_text = device_id + username
    else:
        auth_text = username

    user = deps.authenticate(
        db, username=username, password=password,
          authcode=authcode, auth_text=auth_text
    )

    if not user:
        raise HTTPException(status_code=400, 
                            detail="Invalid username or password")
    elif not deps.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    user_id = user.id
    key = ""
    characters = "0123456789abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    token_text = user_id
    key = ""
    for i in range(0, 30):
        key += characters[random.randint(0, len(characters) - 1)]

    del_token = (
        db.query(ApiTokens).filter(
            ApiTokens.user_id == user.id).update({"status": 0})
    )
    # Update Last Login
    update_login_time = (
        db.query(User)
        .filter(User.id == user.id)
        .update({"last_login_time": datetime.now(settings.tz_IN)})
    )

    db.commit()

    add_token = ApiTokens(
        user_id=user.id,
        token=key,
        created_at=datetime.now(settings.tz_IN),
        renewed_at=datetime.now(settings.tz_IN),
        validity=1,
        device_type=device_type,
        device_id=device_id,
        push_device_id=push_id,
        device_ip=ip,
        status=1,
    )
    db.add(add_token)
    db.commit()
    return {
        "token": key,
        "msg": "Success",
        "name": user.username if user.username else "",
        "user_type": user.user_type,
        "user_id": user.id if user.id else 0,
        "status": 1,
    }


# 2. Logout


@router.post("/logout")
async def logout(db: Session = Depends(deps.get_db), token: str = Form(...)):
    user = deps.get_user_token(db=db, token=token)
    if user:
        check_token = (
            db.query(ApiTokens)
            .filter(ApiTokens.token == token, ApiTokens.status == 1)
            .first()
        )
        if check_token:
            check_token.status = -1
            db.commit()
            return {"status": 1, "msg": "Success"}
        else:
            return {"status": 0, "msg": "Failed"}
    else:
        return {"status": 0, "msg": "Invalid User"}


# 3.Change Password
@router.post("/change_password")
async def change_password(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    user_id: int = Form(None),
    oldpassword: str = Form(None,
                 description="Only required for current user login"),
    newpassword: str = Form(...),
    confirmpassword: str = Form(...),
):
    user = deps.get_user_token(db=db, token=token)

    if newpassword != confirmpassword:
        return {
            "status": 0,
            "msg": "New password and Confirm Password does not match...",
        }

    if user:
        get_user = db.query(User).filter(User.status == 1)
        if user.user_type == 1:
            if user_id:
                get_user = get_user.filter(User.id == user_id)
            else:
                get_user = get_user.filter(User.id == user.id)
        else:
            get_user = get_user.filter(User.id == user.id)

        get_user = get_user.first()

        if get_user:
            if user.user_type == 1 and not user_id and not oldpassword:
                return {"status": 0, "msg": "Old password is Required."}
            if oldpassword:
                if security.verify_password(oldpassword, get_user.password):
                    if newpassword == confirmpassword:
                        get_user.password = get_password_hash(newpassword)
                        db.commit()
                        return {"status": 1,
                                 "msg": "Password Changed Successfully..."}
                else:
                    return {"status": 0,
                             "msg": "The Current Password is Incorrect."}

            else:
                get_user.password = get_password_hash(newpassword)
                db.commit()

                return {"status": 1, "msg": "Password Changed Successfully..."}

        else:
            return {"status": 0, "msg": "User Not Found"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


# 4. FORGOT PASSWORD
# @router.post('/forgot_password')
# async def forgot_password(db: Session = Depends(deps.get_db),
#                                    username: str = Form(...)):
#     user = db.query(User).filter(User.username == username, User.status == 1)
#     check_user = user.first()
#     if check_user:
#         if check_user.mobile_no:
#             otp, reset, created_at, expire_time, expire_at, otp_valid_upto = deps.get_otp()
#             message = f'''Your LCC OTP for Reset Password is : {otp}'''
#             reset_key = f'{reset}{check_user.id}DTEKRNSSHPT'
#             otp2 = random.randint(1111,9999)
#             # otp2=1234
#             user = user.update({'otp': otp2, 'otp_created_at': created_at,'reset_key': reset_key,'otp_expire_at':expire_time})
#             db.commit()

#             mbl_no = f'+91{check_user.mobile}'
#             return ({'status':1,'reset_key': reset_key, 'msg': f'An OTP message has been sent to {mbl_no}','remaining_seconds':otp_valid_upto})

#         else:
#             return({'status':0,'msg':'Sorry. This account does not have mobile number. Please contact administrator'} )

#     else:
#         return({'status':0,'msg':'Sorry. The requested account not found'})

# 5. VERIFY OTP AND RESET PASSWORD

# @router.post('/reset_forgot_password')
# async def reset_forgot_password(db: Session = Depends(deps.get_db), *,
#                                 reset_key : str = Form(...),otp_code : str = Form(...),
#                                 newpassword : str = Form(...),confirmpassword : str = Form(...)
#                                 ):
#     user = db.query(User).filter(User.reset_key == reset_key, User.status == 1)
#     check_user = user.first()

#     if check_user:
#         now = datetime.now(settings.tz_IN)
#         # return check_user.otp_expired_at,now
#         if now <= check_user.otp_expired_at:
#             if otp_code == check_user.otp:
#                 if newpassword == confirmpassword:
#                     user = user.update({'otp': None, 'otp_created_at': None, 'otp_expired_at': None,
#                                         'reset_key': None, 'password': get_password_hash(newpassword)})

#                     db.commit()
#                     return ({'status' : 1, 'msg' : 'Password Changed Successfully...'})
#                 else:
#                     return ({'status' : 0, 'msg' : 'New password and Confirm Paswword does not match...'})
#             else:
#                 return ({'status' : 0, 'msg' : 'Incorrect OTP'})
#         else:
#             return ({'status' : 0, 'msg' : 'Verification Code is invalid'})

#     else:
#         return ({'status' : 0, 'msg' : 'Invalid Request'})
