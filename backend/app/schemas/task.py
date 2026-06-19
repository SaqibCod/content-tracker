from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from app.models.task import AssignedRole, TaskState


class _CamelModel(BaseModel):
    """Base config: accept/emit camelCase aliases, read from ORM attributes.

    The frontend speaks camelCase (``assignedRole``, ``createdAt``); the ORM
    and Python code use snake_case. ``populate_by_name`` lets either form be
    accepted on input.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class TaskCreate(_CamelModel):
    """Request body for ``POST /api/tasks``. ``id``/``createdAt`` are server-set."""

    title: str = Field(min_length=1)
    description: str = ""
    assigned_role: AssignedRole
    state: TaskState = TaskState.code_ready

    @field_validator("title")
    @classmethod
    def _strip_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must not be empty")
        return stripped


class TaskUpdate(_CamelModel):
    """Request body for ``PUT /api/tasks/{id}`` — every field optional (partial)."""

    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    assigned_role: AssignedRole | None = None
    state: TaskState | None = None

    @field_validator("title")
    @classmethod
    def _strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must not be empty")
        return stripped


class TaskResponse(_CamelModel):
    """Response body for all endpoints — serialized with camelCase aliases."""

    id: int
    title: str
    assigned_role: AssignedRole
    state: TaskState
    description: str
    created_at: date
