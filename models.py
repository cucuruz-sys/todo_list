from typing import Optional


class LongTask:
    def __init__(self, task_id: str, status: str, progress: int = 0, result: Optional[str] = None):
        self.task_id = task_id
        self.status = status
        self.progress = progress
        self.result = result