from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime, date
from app.core.config import settings
import sys
import math
import os
import shutil
import requests
from pyfcm import FCMNotification
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

# from svglib.svglib import svg2rlg
# from barcode import Code39



def common_date(date: datetime, without_time=None):
    datetime = date.strftime("%b %d,%Y %I:%M:%S %p")

    if without_time == 1:
        datetime = date.strftime("%d-%m-%Y")

    return datetime


def get_uom_code(uom_code):
    if uom_code == "NO":
        uom_code_des = "Number"
    elif uom_code == "Mtr":
        uom_code_des = "Meter"

    elif uom_code == "SET":
        uom_code_des = "Set"

    elif uom_code == "KG":
        uom_code_des = "Kilogram"

    elif uom_code == "SM":
        uom_code_des = "Square meter"

    elif uom_code == "RS":
        uom_code_des = "Rupees"

    elif uom_code == "ROL":
        uom_code_des = "Roll"
    else:
        uom_code_des = uom_code

    return uom_code_des


def file_storage(file_name, f_name):
    base_dir = settings.BASE_UPLOAD_FOLDER + "/upload_files"

    dt = str(int(datetime.utcnow().timestamp()))

    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=base_dir, err=e))

    output_dir = base_dir + "/"

    filename = file_name.filename
    # Split file name and extension

    txt = filename[::-1]
    splitted = txt.split(".", 1)
    txt1 = splitted[0][::-1]
    txt2 = splitted[1][::-1]

    files_name = f_name.split(".")

    save_full_path = f"{output_dir}{files_name[0]}{dt}.{txt1}"

    file_exe = f"upload_files/{f_name}{dt}.{txt1}"
    with open(save_full_path, "wb") as buffer:
        shutil.copyfileobj(file_name.file, buffer)

    return save_full_path, file_exe


def store_file(file):
    base_dir = settings.BASE_UPLOAD_FOLDER + "/upload_files/"

    dt = str(int(datetime.utcnow().timestamp()))

    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=base_dir, err=e))

    filename = file.filename

    file_properties = filename.split(".")

    file_extension = file_properties[-1]

    file_properties.pop()
    file_splitted_name = file_properties[0]

    write_path = f"{base_dir}{file_splitted_name}{dt}.{file_extension}"
    db_path = f"/upload_files/{file_splitted_name}{dt}.{file_extension}"

    with open(write_path, "wb") as new_file:
        shutil.copyfileobj(file.file, new_file)

    return db_path


def pagination(row_count=0, page=1, size=10):
    current_page_no = page if page >= 1 else 1

    total_pages = math.ceil(row_count / size)

    if current_page_no > total_pages:
        current_page_no = total_pages

    limit = current_page_no * size
    offset = limit - size

    if limit > row_count:
        limit = offset + (row_count % size)

    limit = limit - offset

    if offset < 0:
        offset = 0

    return [limit, offset]


def get_pagination(row_count=0, current_page_no=1, default_page_size=10):
    current_page_no = current_page_no if current_page_no >= 1 else 1

    total_pages = math.ceil(row_count / default_page_size)

    if current_page_no > total_pages:
        current_page_no = total_pages

    limit = current_page_no * default_page_size
    offset = limit - default_page_size

    if limit > row_count:
        limit = offset + (row_count % default_page_size)

    limit = limit - offset

    if offset < 0:
        offset = 0

    return [total_pages, offset, limit]


def paginate(page, size, data, total):
    reply = {"items": data, "total": total, "page": page, "size": size}
    return reply


def paginate_for_file_count(page, size, data, total, file_count):
    reply = {
        "items": data,
        "total": total,
        "page": page,
        "file_count": file_count,
        "size": size,
    }
    return reply


def common_date(date, without_time=None):
    datetime = date.strftime("%Y-%m-%d %H:%M:%S")
    # datetime = date.strftime("%d-%m-%Y %H:%M:%S")

    if without_time == 1:
        datetime = date.strftime("%Y-%m-%d")
    if without_time == 2:
        datetime = date.strftime("%H:%M:%S")
    if without_time == 3:
        datetime = date.strftime("%d-%b-%Y")
    return datetime


def file_storage_form(file_name):
    base_dir = settings.BASE_UPLOAD_FOLDER + "/upload_files"

    dt = str(int(datetime.utcnow().timestamp()))

    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=base_dir, err=e))

    output_dir = base_dir + "/"

    filename = file_name.filename
    # Split file name and extension

    txt = filename[::-1]
    splitted = txt.split(".", 1)
    txt1 = splitted[0][::-1]
    txt2 = splitted[1][::-1]

    save_full_path = f"{output_dir}{filename}{dt}.{txt1}"

    file_exe = f"{filename}{dt}.{txt1}"
    with open(save_full_path, "wb") as buffer:
        shutil.copyfileobj(file_name.file, buffer)

    return save_full_path, file_exe


def chat_date(date):
    datetime = date.strftime("%d/%m/%Y %I:%M:%S %p")
    return datetime
