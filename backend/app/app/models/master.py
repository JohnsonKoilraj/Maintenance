from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Machines(Base):
    id = Column(Integer, primary_key=True)
    machine_name = Column(TINYINT, comment=" 1->MachineA; 2-->MachineB,3->MachineC")
    serial_name=Column(String(50))
    model=Column(String(50))
    # created_by = Column(Integer, comment="ForeignKey('user.id')")
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(TINYINT, comment="0->inactive,1->active,-1->deleted")

class Task(Base):
    id = Column(Integer, primary_key=True)
    task_name=Column(String(50))
    description=Column(String(250))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(TINYINT, comment="0->inactive,1->active,-1->deleted")
