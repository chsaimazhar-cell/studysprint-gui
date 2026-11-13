"""Tkinter desktop interface for StudySprint."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from .models import VALID_PRIORITIES
from .planner import StudyPlanner


class StudySprintApp:
    """A clean, keyboard-friendly desktop interface."""

    BG = "#F4F7FB"
    NAVY = "#172554"
    BLUE = "#2563EB"
    MUTED = "#64748B"
    WHITE = "#FFFFFF"
    GREEN = "#15803D"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.planner = StudyPlanner()
        self.status_filter = tk.StringVar(value="All tasks")
        self.title_value = tk.StringVar()
        self.priority_value = tk.StringVar(value="Medium")
        self.due_value = tk.StringVar()
        self.search_value = tk.StringVar()
        self._build_window()
        self._build_styles()
        self._build_layout()
        self.refresh()

    def _build_window(self) -> None:
        self.root.title("StudySprint | Your Study Planner")
        self.root.geometry("1080x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=self.BG)

    def _build_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.WHITE)
        style.configure(
            "TLabel", background=self.BG, foreground=self.NAVY,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Title.TLabel", font=("Segoe UI", 25, "bold"),
            foreground=self.NAVY, background=self.BG
        )
        style.configure(
            "Subtitle.TLabel", font=("Segoe UI", 10),
            foreground=self.MUTED, background=self.BG
        )
        style.configure(
            "CardTitle.TLabel", font=("Segoe UI", 9, "bold"),
            foreground=self.MUTED, background=self.WHITE
        )
        style.configure(
            "CardValue.TLabel", font=("Segoe UI", 22, "bold"),
            foreground=self.NAVY, background=self.WHITE
        )
        style.configure(
            "TButton", font=("Segoe UI", 10, "bold"), padding=(13, 9)
        )
        style.configure(
            "Accent.TButton", background=self.BLUE, foreground=self.WHITE
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#1D4ED8"), ("disabled", "#93C5FD")],
        )
        style.configure(
            "Treeview", rowheight=36, font=("Segoe UI", 10),
            background=self.WHITE, fieldbackground=self.WHITE,
            foreground=self.NAVY, borderwidth=0
        )
        style.configure(
            "Treeview.Heading", font=("Segoe UI", 9, "bold"),
            background="#E8EEF8", foreground=self.NAVY, padding=9
        )
        style.map("Treeview", background=[("selected", "#DBEAFE")],
                  foreground=[("selected", self.NAVY)])
        style.configure(
            "Horizontal.TProgressbar", troughcolor="#E2E8F0",
            background=self.BLUE, thickness=10
        )

    def _build_layout(self) -> None:
        outer = ttk.Frame(self.root, padding=(30, 24))
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 20))
        heading = ttk.Frame(header)
        heading.pack(side="left", fill="x", expand=True)
        ttk.Label(heading, text="StudySprint", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            heading, text="Plan your study sessions. Track your progress.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(3, 0))
        ttk.Label(
            header, text="STUDY SMART  •  STAY CONSISTENT",
            foreground=self.BLUE, background=self.BG,
            font=("Segoe UI", 9, "bold")
        ).pack(side="right", anchor="center")

        stats = ttk.Frame(outer)
        stats.pack(fill="x", pady=(0, 18))
        self.stat_labels: dict[str, ttk.Label] = {}
        for key, label in (
            ("total", "TOTAL TASKS"),
            ("completed", "COMPLETED"),
            ("remaining", "REMAINING"),
        ):
            card = ttk.Frame(stats, style="Card.TFrame", padding=(17, 13))
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="CardValue.TLabel")
            value.pack(anchor="w", pady=(5, 0))
            self.stat_labels[key] = value

        progress_card = ttk.Frame(stats, style="Card.TFrame", padding=(17, 13))
        progress_card.pack(side="left", fill="both", expand=True)
        progress_top = ttk.Frame(progress_card, style="Card.TFrame")
        progress_top.pack(fill="x")
        ttk.Label(
            progress_top, text="OVERALL PROGRESS", style="CardTitle.TLabel"
        ).pack(side="left")
        self.percent_label = ttk.Label(
            progress_top, text="0%", background=self.WHITE,
            foreground=self.BLUE, font=("Segoe UI", 12, "bold")
        )
        self.percent_label.pack(side="right")
        self.progress_bar = ttk.Progressbar(
            progress_card, maximum=100, style="Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(15, 5))

        content = ttk.Frame(outer)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=0, minsize=280)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        form = ttk.Frame(content, style="Card.TFrame", padding=20)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        ttk.Label(
            form, text="Add a study task",
            background=self.WHITE, foreground=self.NAVY,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")
        ttk.Label(
            form, text="Keep your next learning goal clear and manageable.",
            background=self.WHITE, foreground=self.MUTED,
            wraplength=235
        ).pack(anchor="w", pady=(5, 18))

        self._field_label(form, "TASK TITLE")
        title_entry = ttk.Entry(form, textvariable=self.title_value, width=28)
        title_entry.pack(fill="x", pady=(6, 14), ipady=5)
        title_entry.bind("<Return>", lambda _event: self.add_task())

        self._field_label(form, "PRIORITY")
        priority_box = ttk.Combobox(
            form, textvariable=self.priority_value,
            values=VALID_PRIORITIES, state="readonly"
        )
        priority_box.pack(fill="x", pady=(6, 14), ipady=4)

        self._field_label(form, "DUE DATE  (OPTIONAL)")
        due_entry = ttk.Entry(form, textvariable=self.due_value)
        due_entry.pack(fill="x", pady=(6, 4), ipady=5)
        ttk.Label(
            form, text="Use YYYY-MM-DD, for example 2026-12-01.",
            background=self.WHITE, foreground=self.MUTED,
            wraplength=235, font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 16))

        ttk.Button(
            form, text="+  Add task", style="Accent.TButton",
            command=self.add_task
        ).pack(fill="x", pady=(2, 18))

        ttk.Separator(form).pack(fill="x", pady=(0, 15))
        ttk.Label(
            form, text="QUICK TIP", background=self.WHITE,
            foreground=self.BLUE, font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        ttk.Label(
            form, text="Break a big subject into small tasks. Complete one at a time.",
            background=self.WHITE, foreground=self.MUTED,
            wraplength=235, justify="left"
        ).pack(anchor="w", pady=(6, 0))

        task_panel = ttk.Frame(content, style="Card.TFrame", padding=18)
        task_panel.grid(row=0, column=1, sticky="nsew")
        task_panel.rowconfigure(2, weight=1)
        task_panel.columnconfigure(0, weight=1)

        top = ttk.Frame(task_panel, style="Card.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            top, text="Your tasks", background=self.WHITE,
            foreground=self.NAVY, font=("Segoe UI", 15, "bold")
        ).pack(side="left")
        filter_box = ttk.Combobox(
            top, textvariable=self.status_filter,
            values=("All tasks", "Active", "Completed"),
            state="readonly", width=13
        )
        filter_box.pack(side="right")
        filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh())

        search_row = ttk.Frame(task_panel, style="Card.TFrame")
        search_row.grid(row=1, column=0, sticky="ew", pady=(14, 10))
        search_row.columnconfigure(0, weight=1)
        search = ttk.Entry(search_row, textvariable=self.search_value)
        search.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=5)
        search.insert(0, "")
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        ttk.Button(
            search_row, text="Clear search", command=self._clear_search
        ).grid(row=0, column=1)

        table_wrap = ttk.Frame(task_panel, style="Card.TFrame")
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.rowconfigure(0, weight=1)
        table_wrap.columnconfigure(0, weight=1)
        columns = ("title", "priority", "due", "status")
        self.tree = ttk.Treeview(
            table_wrap, columns=columns, show="headings", selectmode="browse"
        )
        for column, label, width in (
            ("title", "TASK", 240),
            ("priority", "PRIORITY", 90),
            ("due", "DUE DATE", 105),
            ("status", "STATUS", 100),
        ):
            self.tree.heading(column, text=label)
            self.tree.column(
                column, width=width, minwidth=70,
                anchor="w" if column == "title" else "center"
            )
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            table_wrap, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.tag_configure("completed", foreground="#94A3B8")
        self.tree.tag_configure("high", foreground="#B91C1C")
        self.tree.tag_configure("medium", foreground=self.NAVY)
        self.tree.tag_configure("low", foreground="#0F766E")

        actions = ttk.Frame(task_panel, style="Card.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        ttk.Button(
            actions, text="Mark complete", command=self.complete_selected
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            actions, text="Reopen", command=self.reopen_selected
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            actions, text="Delete", command=self.delete_selected
        ).pack(side="left")
        ttk.Button(
            actions, text="Refresh", command=self.refresh
        ).pack(side="right")

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(12, 0))
        ttk.Label(
            footer, text="Your tasks are saved locally on this computer.",
            style="Subtitle.TLabel"
        ).pack(side="left")
        ttk.Label(
            footer, text="STUDYSPRINT  •  v1.0.0",
            style="Subtitle.TLabel"
        ).pack(side="right")

    @staticmethod
    def _field_label(parent: ttk.Frame, text: str) -> None:
        ttk.Label(
            parent, text=text, background=StudySprintApp.WHITE,
            foreground=StudySprintApp.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

    def _clear_search(self) -> None:
        self.search_value.set("")
        self.refresh()

    def add_task(self) -> None:
        title = self.title_value.get().strip()
        due_date = self.due_value.get().strip()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Invalid date", "Enter the due date as YYYY-MM-DD."
                )
                return
        try:
            self.planner.add_task(
                title, self.priority_value.get(), due_date
            )
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not add task", str(exc))
            return
        self.title_value.set("")
        self.due_value.set("")
        self.priority_value.set("Medium")
        self.refresh()
        self.root.focus_set()

    def _selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Select a task", "Choose a task from the list first."
            )
            return None
        return int(selection[0])

    def complete_selected(self) -> None:
        task_id = self._selected_id()
        if task_id is None:
            return
        try:
            self.planner.complete_task(task_id)
            self.refresh()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not update task", str(exc))

    def reopen_selected(self) -> None:
        task_id = self._selected_id()
        if task_id is None:
            return
        try:
            self.planner.reopen_task(task_id)
            self.refresh()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not reopen task", str(exc))

    def delete_selected(self) -> None:
        task_id = self._selected_id()
        if task_id is None:
            return
        if not messagebox.askyesno(
            "Delete task", "Are you sure you want to delete this task?"
        ):
            return
        try:
            self.planner.delete_task(task_id)
            self.refresh()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not delete task", str(exc))

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_value.get().strip().casefold()
        selected_filter = self.status_filter.get()
        for task in self.planner.list_tasks():
            if selected_filter == "Active" and task.completed:
                continue
            if selected_filter == "Completed" and not task.completed:
                continue
            if query and query not in task.title.casefold():
                continue

            status = "Completed" if task.completed else "Active"
            tag = "completed" if task.completed else task.priority.casefold()
            title = f"✓  {task.title}" if task.completed else task.title
            self.tree.insert(
                "", "end", iid=str(task.id),
                values=(title, task.priority, task.due_date or "—", status),
                tags=(tag,),
            )

        progress = self.planner.get_progress()
        for key in ("total", "completed", "remaining"):
            self.stat_labels[key].configure(text=str(progress[key]))
        percentage = float(progress["percentage"])
        self.percent_label.configure(text=f"{percentage:.0f}%")
        self.progress_bar["value"] = percentage


def run_app() -> None:
    root = tk.Tk()
    try:
        StudySprintApp(root)
    except (ValueError, OSError) as exc:
        messagebox.showerror(
            "StudySprint could not start",
            f"Your saved task data could not be loaded.\n\n{exc}",
            parent=root,
        )
        root.destroy()
        return
    root.mainloop()
