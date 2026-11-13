"""Task data model and validation."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


VALID_PRIORITIES = ("Low", "Medium", "High")


@dataclass
class Task:
    """One study task stored by the planner."""

    id: int
    title: str
    priority: str = "Medium"
    due_date: str = ""
    completed: bool = False

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.priority = self.priority.title()

        if self.id < 1:
            raise ValueError("Task ID must be a positive number.")
        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError("Priority must be Low, Medium, or High.")
        if self.due_date:
            try:
                datetime.strptime(self.due_date, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("Due date must use YYYY-MM-DD format.") from exc

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            priority=str(data.get("priority", "Medium")),
            due_date=str(data.get("due_date", "")),
            completed=bool(data.get("completed", False)),
        )
