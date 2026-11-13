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
        if not isinstance(self.title, str):
            raise ValueError("Task title must be text.")
        if isinstance(self.id, bool) or not isinstance(self.id, int) or self.id < 1:
            raise ValueError("Task ID must be a positive number.")
        self.title = self.title.strip()
        if not isinstance(self.priority, str):
            raise ValueError("Priority must be Low, Medium, or High.")
        self.priority = self.priority.title()
        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError("Priority must be Low, Medium, or High.")
        if not isinstance(self.due_date, str):
            raise ValueError("Due date must be text in YYYY-MM-DD format.")
        if self.due_date:
            try:
                parsed_date = datetime.strptime(self.due_date, "%Y-%m-%d")
                if parsed_date.strftime("%Y-%m-%d") != self.due_date:
                    raise ValueError
            except ValueError as exc:
                raise ValueError("Due date must use YYYY-MM-DD format.") from exc
        if not isinstance(self.completed, bool):
            raise ValueError("Completed status must be true or false.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        if not isinstance(data, dict):
            raise ValueError("Each saved task must be a JSON object.")
        completed = data.get("completed", False)
        if not isinstance(completed, bool):
            raise ValueError("Saved task completion status must be true or false.")
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            priority=str(data.get("priority", "Medium")),
            due_date=str(data.get("due_date", "")),
            completed=completed,
        )
