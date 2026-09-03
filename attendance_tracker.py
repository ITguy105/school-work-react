#!/usr/bin/env python3
"""Attendance tracker with SQLite storage, reports, and CSV export."""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_DATABASE = Path(__file__).with_name("attendance.db")
VALID_STATUSES = {"present", "late", "absent", "excused"}


class AttendanceTracker:
    def __init__(self, database: Path) -> None:
        self.database = database
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def close(self) -> None:
        self.connection.close()

    def _create_tables(self) -> None:
        self.connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_number TEXT NOT NULL UNIQUE,
                class_name TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('present', 'late', 'absent', 'excused')),
                note TEXT NOT NULL DEFAULT '',
                recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(student_id, attendance_date)
            );
            CREATE INDEX IF NOT EXISTS attendance_date_index ON attendance(attendance_date);
            CREATE INDEX IF NOT EXISTS attendance_student_index ON attendance(student_id);
            """
        )
        self.connection.commit()

    def add_student(self, name: str, student_number: str, class_name: str) -> int:
        try:
            cursor = self.connection.execute(
                "INSERT INTO students (name, student_number, class_name) VALUES (?, ?, ?)",
                (name.strip(), student_number.strip(), class_name.strip()),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Student number already exists: {student_number}") from error
        return int(cursor.lastrowid)

    def list_students(self, class_name: str | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM students WHERE active = 1"
        parameters: list[str] = []
        if class_name:
            query += " AND class_name = ?"
            parameters.append(class_name)
        query += " ORDER BY class_name, name"
        return list(self.connection.execute(query, parameters))

    def find_student(self, identifier: str) -> sqlite3.Row:
        row = self.connection.execute(
            "SELECT * FROM students WHERE id = ? OR student_number = ? LIMIT 1",
            (identifier, identifier),
        ).fetchone()
        if row is None:
            raise ValueError(f"Student not found: {identifier}")
        return row

    def record_attendance(self, identifier: str, attendance_date: str, status: str, note: str = "") -> None:
        self._validate_date(attendance_date)
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        student = self.find_student(identifier)
        self.connection.execute(
            """
            INSERT INTO attendance (student_id, attendance_date, status, note)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, attendance_date) DO UPDATE SET
                status = excluded.status,
                note = excluded.note,
                recorded_at = CURRENT_TIMESTAMP
            """,
            (student["id"], attendance_date, status, note.strip()),
        )
        self.connection.commit()

    def daily_report(self, attendance_date: str, class_name: str | None = None) -> list[sqlite3.Row]:
        self._validate_date(attendance_date)
        query = """
            SELECT s.name, s.student_number, s.class_name,
                   COALESCE(a.status, 'not recorded') AS status,
                   COALESCE(a.note, '') AS note
            FROM students AS s
            LEFT JOIN attendance AS a
              ON a.student_id = s.id AND a.attendance_date = ?
            WHERE s.active = 1
        """
        parameters: list[str] = [attendance_date]
        if class_name:
            query += " AND s.class_name = ?"
            parameters.append(class_name)
        query += " ORDER BY s.class_name, s.name"
        return list(self.connection.execute(query, parameters))

    def student_summary(self, identifier: str, start: str | None = None, end: str | None = None) -> dict[str, object]:
        student = self.find_student(identifier)
        query = "SELECT status, COUNT(*) AS total FROM attendance WHERE student_id = ?"
        parameters: list[str | int] = [student["id"]]
        if start:
            self._validate_date(start)
            query += " AND attendance_date >= ?"
            parameters.append(start)
        if end:
            self._validate_date(end)
            query += " AND attendance_date <= ?"
            parameters.append(end)
        query += " GROUP BY status"
        counts = {row["status"]: row["total"] for row in self.connection.execute(query, parameters)}
        recorded = sum(counts.values())
        attended = counts.get("present", 0) + counts.get("late", 0)
        rate = round(attended / recorded * 100, 1) if recorded else 0.0
        return {"student": student, "counts": counts, "recorded": recorded, "rate": rate}

    def export_csv(self, output: Path, start: str | None = None, end: str | None = None) -> int:
        query = """
            SELECT a.attendance_date, s.name, s.student_number, s.class_name,
                   a.status, a.note, a.recorded_at
            FROM attendance AS a
            JOIN students AS s ON s.id = a.student_id
            WHERE 1 = 1
        """
        parameters: list[str] = []
        if start:
            self._validate_date(start)
            query += " AND a.attendance_date >= ?"
            parameters.append(start)
        if end:
            self._validate_date(end)
            query += " AND a.attendance_date <= ?"
            parameters.append(end)
        query += " ORDER BY a.attendance_date, s.class_name, s.name"
        rows = list(self.connection.execute(query, parameters))
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["date", "student", "student_number", "class", "status", "note", "recorded_at"])
            writer.writerows([tuple(row) for row in rows])
        return len(rows)

    @staticmethod
    def _validate_date(value: str) -> None:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError("Dates must use YYYY-MM-DD format") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage student attendance with a local SQLite database.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE, help="SQLite database path")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add-student", help="Add a student")
    add.add_argument("name")
    add.add_argument("student_number")
    add.add_argument("class_name")

    students = commands.add_parser("students", help="List active students")
    students.add_argument("--class-name")

    mark = commands.add_parser("mark", help="Record or update attendance")
    mark.add_argument("student", help="Student ID or student number")
    mark.add_argument("attendance_date", help="YYYY-MM-DD")
    mark.add_argument("status", choices=sorted(VALID_STATUSES))
    mark.add_argument("--note", default="")

    daily = commands.add_parser("daily", help="Show attendance for one day")
    daily.add_argument("attendance_date", help="YYYY-MM-DD")
    daily.add_argument("--class-name")

    summary = commands.add_parser("summary", help="Show one student's attendance summary")
    summary.add_argument("student", help="Student ID or student number")
    summary.add_argument("--start")
    summary.add_argument("--end")

    export = commands.add_parser("export", help="Export attendance records to CSV")
    export.add_argument("output", type=Path)
    export.add_argument("--start")
    export.add_argument("--end")
    return parser


def print_daily(rows: list[sqlite3.Row], attendance_date: str) -> None:
    print(f"Attendance for {attendance_date}")
    print("-" * 72)
    for row in rows:
        note = f" — {row['note']}" if row["note"] else ""
        print(f"{row['class_name']:<16} {row['name']:<24} {row['status']:<14}{note}")
    print(f"\n{len(rows)} student(s)")


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()
    tracker = AttendanceTracker(arguments.database)
    try:
        if arguments.command == "add-student":
            student_id = tracker.add_student(arguments.name, arguments.student_number, arguments.class_name)
            print(f"Added {arguments.name} with ID {student_id}.")
        elif arguments.command == "students":
            for student in tracker.list_students(arguments.class_name):
                print(f"{student['id']:>3}  {student['student_number']:<12} {student['class_name']:<16} {student['name']}")
        elif arguments.command == "mark":
            tracker.record_attendance(arguments.student, arguments.attendance_date, arguments.status, arguments.note)
            print(f"Recorded {arguments.status} attendance for {arguments.student} on {arguments.attendance_date}.")
        elif arguments.command == "daily":
            print_daily(tracker.daily_report(arguments.attendance_date, arguments.class_name), arguments.attendance_date)
        elif arguments.command == "summary":
            result = tracker.student_summary(arguments.student, arguments.start, arguments.end)
            student = result["student"]
            print(f"{student['name']} ({student['student_number']}) — attendance rate: {result['rate']}%")
            for status in sorted(VALID_STATUSES):
                print(f"  {status:<8} {result['counts'].get(status, 0)}")
            print(f"  {'recorded':<8} {result['recorded']}")
        elif arguments.command == "export":
            count = tracker.export_csv(arguments.output, arguments.start, arguments.end)
            print(f"Exported {count} record(s) to {arguments.output}.")
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        tracker.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
