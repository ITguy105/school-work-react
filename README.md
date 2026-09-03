# Studyday — Python School Work Planner

Studyday is a Python-only school-work planner built with Flask. It provides a responsive browser interface for tracking assignment subjects, titles, due dates, priorities, and completion status.

## Features

- View assignments in a focused dashboard.
- Add assignments with a subject, title, due date, and priority.
- Mark work complete or pending.
- Delete assignments.
- See pending work, completed work, and completion progress.
- Persist data in a local `assignments.json` file.
- Use a dependency-light Python diagnostics utility.

## Requirements

- Python 3.9 or newer
- Flask 3.x

## Setup

Create and activate a virtual environment, then install the dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the application:

```bash
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Debugging

Run the included diagnostics utility from the project root:

```bash
python3 tools/debug_project.py
```

To also check a running Flask server:

```bash
python3 tools/debug_project.py --url http://127.0.0.1:5000
```

The utility checks required files, Python syntax, and the Flask dependency. It returns exit status `0` when all checks pass and `1` when a check fails.

## Project structure

```text
app.py                     Flask application and routes
requirements.txt           Python dependency manifest
assignments.json           Local assignment storage, created at runtime
 tools/debug_project.py    Python diagnostics utility
```

## Routes

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/` | Render the planner dashboard |
| POST | `/assignments` | Create an assignment |
| POST | `/assignments/<id>/toggle` | Toggle completion |
| POST | `/assignments/<id>/delete` | Delete an assignment |

## Notes

The app uses a JSON file for simple local persistence. For multi-user production use, replace the JSON storage layer with a database and add authentication, CSRF protection, and deployment-specific configuration.

## License

This project is provided for school-work and learning purposes.
