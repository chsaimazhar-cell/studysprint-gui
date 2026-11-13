"""Unit tests for task management and persistence."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from study_sprint.planner import StudyPlanner


class StudyPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "tasks.json"
        self.planner = StudyPlanner(self.data_file)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_task_and_persist(self) -> None:
        task = self.planner.add_task(
            "Revise Python loops", "High", "2026-12-01"
        )
        loaded = StudyPlanner(self.data_file)
        self.assertEqual(task.id, 1)
        self.assertEqual(loaded.list_tasks()[0].title, "Revise Python loops")

    def test_empty_title_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.planner.add_task("   ")

    def test_invalid_date_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.planner.add_task("Study", due_date="01-12-2026")

    def test_complete_reopen_and_progress(self) -> None:
        task = self.planner.add_task("Practice functions")
        self.planner.complete_task(task.id)
        self.assertEqual(self.planner.get_progress()["percentage"], 100.0)
        self.planner.reopen_task(task.id)
        self.assertEqual(self.planner.get_progress()["remaining"], 1)

    def test_delete_task(self) -> None:
        task = self.planner.add_task("Read chapter one")
        self.planner.delete_task(task.id)
        self.assertEqual(self.planner.get_progress()["total"], 0)

    def test_ids_do_not_collide_after_delete(self) -> None:
        first = self.planner.add_task("First")
        self.planner.add_task("Second")
        self.planner.delete_task(first.id)
        third = self.planner.add_task("Third")
        self.assertEqual(third.id, 3)

    def test_non_list_storage_file_is_rejected(self) -> None:
        self.data_file.write_text('{"not": "a task list"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            StudyPlanner(self.data_file)

    def test_invalid_saved_completion_type_is_rejected(self) -> None:
        self.data_file.write_text(
            '[{"id": 1, "title": "Task", "completed": "false"}]',
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            StudyPlanner(self.data_file)

    def test_failed_save_rolls_back_new_task(self) -> None:
        with patch.object(self.planner, "_save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.planner.add_task("Unsaved task")
        self.assertEqual(self.planner.list_tasks(), [])

    def test_failed_save_rolls_back_completion_and_reopen(self) -> None:
        task = self.planner.add_task("Keep active")
        with patch.object(self.planner, "_save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.planner.complete_task(task.id)
        self.assertFalse(task.completed)

        self.planner.complete_task(task.id)
        with patch.object(self.planner, "_save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.planner.reopen_task(task.id)
        self.assertTrue(task.completed)

    def test_failed_save_rolls_back_deletion(self) -> None:
        task = self.planner.add_task("Keep stored")
        with patch.object(self.planner, "_save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.planner.delete_task(task.id)
        self.assertEqual(self.planner.list_tasks(), [task])


if __name__ == "__main__":
    unittest.main()
