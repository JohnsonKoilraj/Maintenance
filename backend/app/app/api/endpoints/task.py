from fastapi import APIRouter, Depends, Form
from app.api import deps
from app.utils import pagination
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import *
from datetime import datetime

router=APIRouter()


# create_task
@router.post("/create_task")
async def create_task(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    task_name:str=Form(...),
    description:str=Form(...)

):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1,2,3,4]:
            existing_task=(db.query(Task)
            .filter(Task.task_name==task_name,
                    Task.status==1)
            .first()   
            )
            if existing_task:
                return {"status": 0,
                        "msg": "Task Already Present."}
            create_task = Task(
                task_name=task_name,
                description=description,
                created_at=datetime.now(settings.tz_IN),
                status=1,
            )

            db.add(create_task)
            db.commit()
            db.refresh(create_task)

            return {"status": 1, "msg": "Successfully Created"}
        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }

@router.post("/list_tasks")
async def list_tasks(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    page: int = 1,
    size: int = 10,
    task_name: str = Form(None),
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        list_tasks = db.query(Task).filter(Task.status == 1)

        if task_name:
            list_tasks = list_tasks.filter(
                Task.task_name.like("%" + task_name + "%")
            )

        list_tasks = list_tasks.order_by(Task.id.asc())

        list_tasks_count = list_tasks.count()

        limit, offset = pagination(list_tasks_count, page, size)

        list_tasks = list_tasks.limit(limit).offset(offset).all()

        task_data = []
        if list_tasks:
            for row in list_tasks:
                task_data.append(
                    {
                        "task_id": row.id,
                        "task_name": row.task_name,
                        "description":row.description,
                        "created_at": row.created_at,   
                    }
                )

        data = {
            "page": page,
            "size": size,
            "total": list_tasks_count,
            "items": task_data,
        }

        return {"status": 1, "msg": "Success", "data": data}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }
    

# update task
@router.put("/update_task")
async def update_task(
    db: Session = Depends(deps.get_db),
    token: str = Form(None),
    task_id: int = Form(...),
    description:str=Form(...)
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1,2,3,4]:
            check_task = (
                db.query(Task)
                .filter(Task.id == task_id, Task.status == 1)
                .first()
            )
            if check_task:
                _serial = (
                    db.query(Task)
                    .filter(
                        Task.status == 1,
                        Task.id != task_id,
                    )
                    .first()
                )

                check_task.description = description
                check_task.updated_at = datetime.now(settings.tz_IN)
                
                db.commit()

                return {"status": 1, "msg": "Successfully Updated"}

            else:
                return {"status": 0, "msg": "Invalid task Id"}

        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


# delete
@router.post("/delete_task")
async def delete_task(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    task_id: int = Form(...),
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1,2,3,4]:
            check_task = (
                db.query(Task)
                .filter(Task.id == task_id, Task.status == 1)
                .first()
            )
            if check_task:
                check_task.status = -1
                db.commit()
                return {"status": 1, "msg": "Successfully Deleted"}
            else:
                return {"status": 0, "msg": "Invalid task Id"}
        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }