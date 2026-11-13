# StudySprint GUI

A simple, polished desktop study planner built with **Python and Tkinter**. Create study tasks, set priorities and due dates, track completion, and keep your progress visible.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Interface](https://img.shields.io/badge/Interface-Tkinter-2563EB)
![Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library-15803D)
![License](https://img.shields.io/badge/License-MIT-blue)

## Features

- Add tasks with a title, priority, and optional due date.
- Mark tasks complete or reopen them later.
- Delete tasks with a confirmation prompt.
- Search tasks by title and filter active/completed tasks.
- See total, completed, remaining, and percentage progress.
- Save tasks automatically in a local `tasks.json` file.
- No third-party Python packages or account required.

## Requirements

- Python 3.10 or newer.
- Tkinter, which is included with most standard Python installations. On some Linux distributions it must be installed separately (for example, the `python3-tk` package).

## Run the application

1. Download or clone this repository.
2. Open the project folder in a terminal.
3. Run:

```bash
python main.py
```

On some Linux systems, use `python3 main.py`.

## Run the tests

```bash
python -m unittest discover -v
```

The tests use temporary files, so they do not change your personal task list.

## How your data is stored

StudySprint writes your tasks to `tasks.json` in the folder where you launch the app. The file stays on your computer; this project does not upload task data to a server. Back up that file if your task list is important.

Due dates are optional and use the `YYYY-MM-DD` format, for example `2026-12-01`.

## Project structure

```text
studysprint-gui/
├── main.py
├── study_sprint/
│   ├── __init__.py
│   ├── models.py
│   ├── planner.py
│   └── gui.py
├── tests/
│   ├── __init__.py
│   └── test_planner.py
├── .gitignore
├── LICENSE
└── README.md
```

## Learning goals

This project is designed to be readable for Python learners. It demonstrates classes and dataclasses, input validation, separation of application logic from the user interface, JSON file handling, exception handling, Tkinter widgets, and automated unit tests.

## License

Released under the MIT License. See [LICENSE](LICENSE).
