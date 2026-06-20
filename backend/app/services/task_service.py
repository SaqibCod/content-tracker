"""Task business logic. Talks to the database; knows nothing about HTTP.

Routes call into these functions and translate the results (including the
``None`` returned for a missing task) into HTTP responses.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def list_tasks(db: AsyncSession) -> list[Task]:
    result = await db.execute(select(Task).order_by(Task.id))
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    return await db.get(Task, task_id)


async def create_task(db: AsyncSession, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    await db.commit()
    return task


async def update_task(db: AsyncSession, task_id: int, payload: TaskUpdate) -> Task | None:
    task = await db.get(Task, task_id)
    if task is None:
        return None
    # exclude_unset → partial (PATCH-like) update: only overwrite fields the
    # client actually sent, leaving the rest untouched.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    task = await db.get(Task, task_id)
    if task is None:
        return False
    await db.delete(task)
    await db.commit()
    return True
