"""Task management and local JSON persistence."""

import json
from pathlib import Path
from typing import Any

from .models import Task, VALID_PRIORITIES


class StudyPlanner:
    """Manage study tasks and save them locally between sessions."""

    def __init__(self, storage_path: str | Path = "tasks.json") -> None:
        self.storage_path = Path(storage_path)
        self.tasks: list[Task] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            self.tasks = []
            return

        try:
            raw: Any = json.loads(self.storage_path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("The tasks file must contain a JSON list.")
            self.tasks = [Task.from_dict(item) for item in raw]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Could not read {self.storage_path.name}: {exc}"
            ) from exc

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.storage_path.with_name(self.storage_path.name + ".tmp")
        payload = [task.to_dict() for task in self.tasks]
        temporary_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(self.storage_path)

    def add_task(
        self, title: str, priority: str = "Medium", due_date: str = ""
    ) -> Task:
        next_id = max((task.id for task in self.tasks), default=0) + 1
        task = Task(next_id, title, priority, due_date)
        self.tasks.append(task)
        self._save()
        return task

    def list_tasks(self) -> list[Task]:
        return list(self.tasks)

    def complete_task(self, task_id: int) -> Task:
        task = self._find_task(task_id)
        if task.completed:
            raise ValueError("This task is already completed.")
        task.completed = True
        self._save()
        return task

    def reopen_task(self, task_id: int) -> Task:
        task = self._find_task(task_id)
        if not task.completed:
            raise ValueError("This task is already active.")
        task.completed = False
        self._save()
        return task

    def delete_task(self, task_id: int) -> Task:
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self._save()
        return task

    def _find_task(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"No task found with ID {task_id}.")

    def get_progress(self) -> dict[str, int | float]:
        total = len(self.tasks)
        completed = sum(task.completed for task in self.tasks)
        remaining = total - completed
        percentage = (completed / total * 100) if total else 0.0
        return {
            "total": total,
            "completed": completed,
            "remaining": remaining,
            "percentage": percentage,
        }
