from fastapi import FastAPI, APIRouter, Depends
from pydantic import BaseModel
from database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users

router = APIRouter()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/auth/")
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    create_user_model = Users(
        username = create_user_request.username,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = create_user_request.password,
        role = create_user_request.role,
        is_active = True
    )
    db.add(create_user_model)
    db.commit()
    # db.refresh(create_user_model)
    return create_user_model
