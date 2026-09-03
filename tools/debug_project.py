#!/usr/bin/env python3
"""Small, dependency-free diagnostics for the School Work Planner repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


REQUIRED_FILES = (
    "package.json",
    "client/src/App.tsx",
    "client/src/pages/Home.tsx",
    "server/routers.ts",
    "server/db.ts",
    "drizzle/schema.ts",
)


def run(command: list[str], root: Path) -> tuple[bool, str]:
    """Run a project command and return success plus a short output summary."""
    try:
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error)
    output = result.stdout.strip().splitlines()
    summary = output[-1] if output else "No command output"
    return result.returncode == 0, summary


def check_url(url: str) -> tuple[bool, str]:
    try:
        with urlopen(url, timeout=5) as response:
            return 200 <= response.status < 400, f"HTTP {response.status}"
    except (OSError, URLError) as error:
        return False, str(error)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run diagnostics for the School Work Planner.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--url", help="Optional running app URL to check, e.g. http://localhost:3000")
    parser.add_argument("--skip-build", action="store_true", help="Skip the production build to run diagnostics faster")
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[dict[str, object]] = []
    missing = [path for path in REQUIRED_FILES if not (root / path).is_file()]
    checks.append({"name": "required files", "passed": not missing, "detail": "all present" if not missing else ", ".join(missing)})

    package_path = root / "package.json"
    package_ok = False
    if package_path.is_file():
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
            package_ok = package.get("scripts", {}).get("check") == "tsc --noEmit"
        except (OSError, json.JSONDecodeError):
            package_ok = False
    checks.append({"name": "package configuration", "passed": package_ok, "detail": "TypeScript check script found" if package_ok else "package.json is invalid or incomplete"})

    for label, command in (("TypeScript", ["pnpm", "check"]), ("tests", ["pnpm", "test"])):
        passed, detail = run(command, root)
        checks.append({"name": label, "passed": passed, "detail": detail})

    if not args.skip_build:
        passed, detail = run(["pnpm", "build"], root)
        checks.append({"name": "production build", "passed": passed, "detail": detail})

    if args.url:
        passed, detail = check_url(args.url)
        checks.append({"name": f"preview {args.url}", "passed": passed, "detail": detail})

    for check in checks:
        marker = "PASS" if check["passed"] else "FAIL"
        print(f"[{marker}] {check['name']}: {check['detail']}")

    failed = sum(not bool(check["passed"]) for check in checks)
    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
