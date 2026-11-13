"""Windows desktop smoke tests for StudySprint's Tkinter interface."""

import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from study_sprint.gui import StudySprintApp
from study_sprint.planner import StudyPlanner


class StudySprintGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.planner = StudyPlanner(Path(self.temp_dir.name) / "tasks.json")
        self.root = tk.Tk()
        self.root.withdraw()
        self.planner_patch = patch("study_sprint.gui.StudyPlanner", return_value=self.planner)
        self.planner_patch.start()
        self.app = StudySprintApp(self.root)

    def tearDown(self):
        self.planner_patch.stop()
        self.root.destroy()
        self.temp_dir.cleanup()

    def test_add_task_updates_table_and_statistics(self):
        self.app.title_value.set("Practice Python")
        self.app.priority_value.set("High")
        self.app.due_value.set("2026-12-01")
        self.app.add_task()

        self.assertEqual(len(self.planner.list_tasks()), 1)
        self.assertEqual(self.app.tree.get_children(), ("1",))
        self.assertEqual(self.app.stat_labels["total"].cget("text"), "1")
        self.assertEqual(self.app.percent_label.cget("text"), "0%")

    def test_invalid_due_date_is_rejected_without_saving(self):
        self.app.title_value.set("Practice dates")
        self.app.due_value.set("01-12-2026")
        with patch("study_sprint.gui.messagebox.showerror") as show_error:
            self.app.add_task()
        show_error.assert_called_once()
        self.assertEqual(self.planner.list_tasks(), [])

    def test_complete_and_reopen_selected_task(self):
        task = self.planner.add_task("Read chapter")
        self.app.refresh()
        self.app.tree.selection_set(str(task.id))

        self.app.complete_selected()
        self.assertTrue(self.planner.list_tasks()[0].completed)
        self.assertEqual(self.app.percent_label.cget("text"), "100%")

        self.app.tree.selection_set(str(task.id))
        self.app.reopen_selected()
        self.assertFalse(self.planner.list_tasks()[0].completed)
        self.assertEqual(self.app.percent_label.cget("text"), "0%")

    def test_search_and_status_filter(self):
        first = self.planner.add_task("Python loops")
        self.planner.add_task("Discrete mathematics")
        self.planner.complete_task(first.id)
        self.app.search_value.set("python")
        self.app.refresh()
        self.assertEqual(self.app.tree.get_children(), ("1",))

        self.app.search_value.set("")
        self.app.status_filter.set("Completed")
        self.app.refresh()
        self.assertEqual(self.app.tree.get_children(), ("1",))

    def test_delete_requires_confirmation(self):
        task = self.planner.add_task("Delete me")
        self.app.refresh()
        self.app.tree.selection_set(str(task.id))
        with patch("study_sprint.gui.messagebox.askyesno", return_value=False):
            self.app.delete_selected()
        self.assertEqual(len(self.planner.list_tasks()), 1)

        with patch("study_sprint.gui.messagebox.askyesno", return_value=True):
            self.app.delete_selected()
        self.assertEqual(self.planner.list_tasks(), [])


if __name__ == "__main__":
    unittest.main()
