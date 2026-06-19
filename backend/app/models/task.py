import enum
from datetime import date

from sqlalchemy import Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskState(str, enum.Enum):
    """Ordered pipeline stages. Order mirrors the frontend ``STATES`` array."""

    code_ready = "code_ready"
    recorded = "recorded"
    editing = "editing"
    uploaded = "uploaded"
    published = "published"


class AssignedRole(str, enum.Enum):
    """Roles a task can be assigned to (mirrors the frontend ``ROLE_CONFIG``)."""

    Admin = "Admin"
    Content = "Content"
    Editor = "Editor"
    Uploader = "Uploader"


class Task(Base):
    """A single video-production card on the Kanban board."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    assigned_role: Mapped[AssignedRole] = mapped_column(
        # values_callable stores the enum *value* ("Content"), not its name.
        Enum(AssignedRole, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    state: Mapped[TaskState] = mapped_column(
        Enum(TaskState, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=TaskState.code_ready,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
