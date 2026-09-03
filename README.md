# Python School Tools

This repository contains two standalone Python school tools:

- `app.py` is a Flask-based school-work planner with a browser interface.
- `attendance_tracker.py` is an advanced command-line attendance tracker with SQLite storage, reports, summaries, and CSV export.

## Attendance tracker

The attendance tracker creates a local SQLite database automatically. It stores students and one attendance record per student per date. Supported statuses are `present`, `late`, `absent`, and `excused`.

### Commands

```bash
python3 attendance_tracker.py add-student "Sam Taylor" ST104 "Year 10"
python3 attendance_tracker.py students
python3 attendance_tracker.py mark ST104 2026-09-03 present
python3 attendance_tracker.py mark ST104 2026-09-04 late --note "Arrived after registration"
python3 attendance_tracker.py daily 2026-09-03
python3 attendance_tracker.py summary ST104 --start 2026-09-01 --end 2026-09-30
python3 attendance_tracker.py export september-attendance.csv --start 2026-09-01 --end 2026-09-30
```

Use `--database another-file.db` to select a different SQLite database. Student IDs and student numbers can both be used when recording attendance or requesting a summary.

## Flask school-work planner

`app.py` provides a responsive browser interface for assignment subjects, titles, due dates, priorities, and completion status. Assignment data is stored in `assignments.json`, which is created when the first change is saved.

### Setup

Create a virtual environment and install Flask:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the planner:

```bash
python3 app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Debugging

Run the dependency-light diagnostics script:

```bash
python3 tools/debug_project.py
```

To check a running Flask server as well:

```bash
python3 tools/debug_project.py --url http://127.0.0.1:5000
```

The diagnostic script checks required files, Python syntax, the Flask dependency declaration, and an optional HTTP preview. It returns exit status `0` when all checks pass and `1` when a check fails.

## Project structure

```text
app.py                     Flask assignment planner
attendance_tracker.py      SQLite attendance tracker and reporting CLI
requirements.txt            Flask dependency manifest
README.md                   Setup and usage documentation
tools/debug_project.py      Python diagnostics utility
```

## Attendance data model

| Table | Purpose |
| --- | --- |
| `students` | Stores the student name, student number, class, and active state. |
| `attendance` | Stores the date, status, note, and recording time for each student. |

The database enforces unique student numbers, valid attendance statuses, foreign-key relationships, and one record per student per date. Re-running `mark` for an existing student/date updates the existing record instead of creating a duplicate.

## Notes

This project is intended for learning and school-work practice. The Flask app uses local JSON storage and the attendance tracker uses a local SQLite database. For production or multi-user use, add authentication, CSRF protection, backups, role-based access, and a hosted database.

## License

This project is provided for educational purposes.
