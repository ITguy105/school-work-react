#!/usr/bin/env python3
"""Dependency-light diagnostics for the Python school tools."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def check_required_files(root: Path) -> tuple[bool, str]:
    required = [root / "app.py", root / "attendance_tracker.py", root / "requirements.txt", root / "README.md"]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    return not missing, "all present" if not missing else "missing: " + ", ".join(missing)


def check_python_files(root: Path) -> tuple[bool, str]:
    files = [root / "app.py", root / "attendance_tracker.py", root / "tools" / "debug_project.py"]
    try:
        for file in files:
            compile(file.read_text(encoding="utf-8"), str(file), "exec")
    except (OSError, SyntaxError) as error:
        return False, str(error)
    return True, "Python syntax is valid"


def check_requirements(root: Path) -> tuple[bool, str]:
    try:
        requirements = (root / "requirements.txt").read_text(encoding="utf-8").lower()
    except OSError as error:
        return False, str(error)
    return "flask" in requirements, "Flask dependency found" if "flask" in requirements else "Flask dependency missing"


def check_url(url: str) -> tuple[bool, str]:
    try:
        with urlopen(url, timeout=5) as response:
            return 200 <= response.status < 400, f"HTTP {response.status}"
    except (OSError, URLError) as error:
        return False, str(error)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run diagnostics for the Python school tools.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--url", help="Optional running Flask URL, for example http://localhost:5000")
    args = parser.parse_args()
    root = args.root.resolve()

    checks = [
        ("required files", *check_required_files(root)),
        ("Python syntax", *check_python_files(root)),
        ("requirements", *check_requirements(root)),
    ]
    if args.url:
        checks.append((f"preview {args.url}", *check_url(args.url)))

    for name, passed, detail in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")
    failed = sum(not passed for _, passed, _ in checks)
    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
