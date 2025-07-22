import aiosqlite
import asyncio

SQLALCHEMY_DATABASE_URL = "todos.db"

async def init_db():
    async with aiosqlite.connect(SQLALCHEMY_DATABASE_URL) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS long_tasks (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,  -- pending, in_progress, completed, failed
                progress INTEGER DEFAULT 0,  -- 0-100
                result TEXT
            )
        ''')
        await db.commit()