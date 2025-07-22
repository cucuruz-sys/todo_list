from fastapi import FastAPI, HTTPException
import asyncio
import uuid
import aiosqlite
from typing import Dict
from contextlib import asynccontextmanager

from database import init_db, SQLALCHEMY_DATABASE_URL
from models import LongTask
from schemas import TaskResponse, TodoCreate, TodoResponse



# Хранилище задач в памяти (для демонстрации, в продакшене — БД)
tasks: Dict[str, LongTask] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, title="To-Do API")

async def long_running_task(task_id: str):
    try:
        # Имитация длительной операции (например, обработка файла)
        total_steps = 100
        for i in range(1, total_steps + 1):
            # Обновляем прогресс в БД
            async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
                await db.execute(
                    "UPDATE long_tasks SET progress = ?, status = 'in_progress' WHERE id = ?",
                    (i, task_id)
                )
                await db.commit()

            await asyncio.sleep(1)  # Имитация работы (1% за 1 секунду → 100 секунд)

        async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
            await db.execute(
                "UPDATE long_tasks SET status = 'completed', result = 'Операция завершена успешно!' WHERE id = ?",
                (task_id,)
            )
            await db.commit()

    except Exception as e:
        # Обработка ошибок
        async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
            await db.execute(
                "UPDATE long_tasks SET status = 'failed', result = ? WHERE id = ?",
                (str(e), task_id)
            )
            await db.commit()

@app.post("/tasks/", response_model=TaskResponse, status_code=201)
async def start_long_task():
    task_id = str(uuid.uuid4())

    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        await db.execute(
            "INSERT INTO long_tasks (id, status, progress) VALUES (?, 'pending', 0)",
            (task_id,)
        )
        await db.commit()

    # Запускаем задачу в фоне
    asyncio.create_task(long_running_task(task_id))

    return TaskResponse(task_id=task_id, status="pending", progress=0)


# Получение статуса задачи
@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM long_tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return TaskResponse(
        task_id=row["id"],
        status=row["status"],
        progress=row["progress"],
        result=row["result"]
    )


@app.on_event("startup")
def on_startup():
    init_db()

# Получить список всех задач
@app.post("/todos/", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate):
    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        cursor = await db.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (todo.title, todo.description, False)
        )
        todo_id = cursor.lastrowid
        await db.commit()

        cursor = await db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = await cursor.fetchone()

    return TodoResponse(
        id=row[0],
        title=row[1],
        description=row[2],
        completed=bool(row[3])
    )


@app.get("/todos/", response_model=list[TodoResponse])
async def read_todos():
    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM todos")
        rows = await cursor.fetchall()

    return [
        TodoResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=bool(row["completed"])
        ) for row in rows
    ]

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: TodoCreate):
    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        await db.execute(
            "UPDATE todos SET title = ?, description = ? WHERE id = ?",
            (todo.title, todo.description, todo_id)
        )
        await db.commit()

        cursor = await db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = await cursor.fetchone()

    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"])
    )

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int):
    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        await db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        await db.commit()

    return