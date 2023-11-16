from fastapi import APIRouter, Depends, Form
from app.api import deps
from app.utils import pagination
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import *
from datetime import datetime

router=APIRouter()

# create_machine
@router.post("/create_machine")
async def create_machine(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    machine_name: int = Form(..., description="1->MachineA,2->MachineB,3->MachineC"),
    serial_name:str=Form(...),
    model:str=Form(...)
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1,2,3,4]:
            existing_serial=(db.query(Machines)
            .filter(Machines.serial_name==serial_name,
                    Machines.status==1)
            .first()   
            )
            if existing_serial:
                return {"status": 0,
                        "msg": "Serial Name Already Present."}
            create_machine = Machines(
                machine_name=machine_name,
                serial_name=serial_name,
                model=model,
                created_at=datetime.now(settings.tz_IN),
                status=1,
            )

            db.add(create_machine)
            db.commit()
            db.refresh(create_machine)

            return {"status": 1, "msg": "Successfully Created"}
        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }

@router.post("/list_machines")
async def list_machines(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    page: int = 1,
    size: int = 10,
    machine_name: str = Form(None),
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        list_machines = db.query(Machines).filter(Machines.status == 1)

        if machine_name:
            list_machines = list_machines.filter(
                Machines.machine_name.like("%" + machine_name + "%")
            )

        list_machines = list_machines.order_by(Machines.id.asc())

        list_machines_count = list_machines.count()

        limit, offset = pagination(list_machines_count, page, size)

        list_machines = list_machines.limit(limit).offset(offset).all()

        machine_data = []
        if list_machines:
            for row in list_machines:
                machine_data.append(
                    {
                        "machine_id": row.id,
                        "machine_name": row.machine_name,
                        "serial_name":row.serial_name,
                        "model":row.model,
                        "created_at": row.created_at,
                        
                    }
                )

        data = {
            "page": page,
            "size": size,
            "total": list_machines_count,
            "items": machine_data,
        }

        return {"status": 1, "msg": "Success", "data": data}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }
    

# update machine
@router.put("/update_machine")
async def update_machine(
    db: Session = Depends(deps.get_db),
    token: str = Form(None),
    machine_id: int = Form(...),
    serial_name: str = Form(...),
    model:str=Form(...)
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1,2,3,4]:
            check_machine = (
                db.query(Machines)
                .filter(Machines.id == machine_id, Machines.status == 1)
                .first()
            )
            if check_machine:
                check_serial = (
                    db.query(Machines)
                    .filter(
                        Machines.status == 1,
                        Machines.serial_name == serial_name,
                        Machines.id != machine_id,
                    )
                    .first()
                )

                if check_serial:
                    return {"status": 0, "msg": "Serial name already exists"}
                
                check_machine.serial_name = serial_name
                check_machine.model = model
                check_machine.updated_at = datetime.now(settings.tz_IN)
                
                db.commit()

                return {"status": 1, "msg": "Successfully Updated"}

            else:
                return {"status": 0, "msg": "Invalid machine Id"}

        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }


# delete
@router.post("/delete_machine")
async def delete_machine(
    db: Session = Depends(deps.get_db),
    token: str = Form(...),
    machine_id: int = Form(...),
):
    user = deps.get_user_token(db=db, token=token)
    if user:
        if user.user_type in [1,2,3,4]:
            check_machine = (
                db.query(Machines)
                .filter(Machines.id == machine_id, Machines.status == 1)
                .first()
            )
            if check_machine:
                check_machine.status = -1
                db.commit()
                return {"status": 1, "msg": "Successfully Deleted"}
            else:
                return {"status": 0, "msg": "Invalid Machine Id"}
        else:
            return {"status": 0, "msg": "Not Authenticated"}
    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }