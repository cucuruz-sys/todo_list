from pydantic import BaseModel
from typing import Optional


class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    result: Optional[str] = None


class TodoCreate(BaseModel):
    title: str
    description: str | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool