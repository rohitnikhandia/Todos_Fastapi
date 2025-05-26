from fastapi import FastAPI, Depends, status, Path
from fastapi.exceptions import HTTPException

import models
from models import Todos

from database import engine
from database import SessionLocal

from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency, update_request: TodoRequest, todo_id: int = Path(gt=0)
):
    update_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if update_model:
        update_model.title = update_request.title
        update_model.description = update_request.description
        update_model.priority = update_request.priority
        update_model.complete = update_request.complete
        db.add(update_model)
        db.commit()
    return HTTPException(404, detail="Todo not found.")



@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    delete_model = db.query(Todos).filter(Todos.id==todo_id).first()
    print(delete_model)
    # print(dict(delete_model))
    if not delete_model:
        raise HTTPException(status_code=404, detail="Todo not found.")
    db.delete(delete_model)
    db.commit()
