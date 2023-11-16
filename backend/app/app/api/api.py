from fastapi import APIRouter
from .endpoints import (
    login,user,master,task
)

api_router = APIRouter()

# api_router.include_router(qr.router, tags=["qr"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(master.router, tags=["Machines"])
api_router.include_router(task.router, tags=["Tasks"])



