"""Task HTTP endpoints. Knows about FastAPI/HTTP only — no SQLAlchemy.

All persistence is delegated to ``app.services.task_service``. These handlers
just bind the request, call the service, and map results to status codes per
``specs/api-contract.md``.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[TaskResponse]:
    return await task_service.list_tasks(db)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    return await task_service.create_task(db, payload)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    task = await task_service.update_task(db, task_id, payload)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    deleted = await task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Task not found")
