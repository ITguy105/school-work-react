# Studyday — School Work Planner

Studyday is a responsive school-work planner for organizing assignments, due dates, priorities, and completion progress. It combines a React 19 frontend with a Node.js/Express backend, tRPC procedures, and a Drizzle ORM database schema.

## Features

- View assignments in a focused dashboard.
- Add assignments with a subject, title, due date, and priority.
- Filter work by all, pending, or completed assignments.
- Mark assignments complete or return them to the pending list.
- Delete assignments that are no longer needed.
- Track pending work, completed work, and overall momentum.
- Use responsive layouts on desktop and mobile screens.
- Run a dependency-free Python diagnostic script for project health checks.

## Technology

| Area | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| UI | shadcn/ui primitives, Lucide icons, Manrope and DM Serif Display |
| Backend | Node.js, Express, tRPC |
| Data layer | Drizzle ORM with MySQL/TiDB support |
| Testing | Vitest |
| Diagnostics | Python 3.11 standard library |

## Requirements

Install Node.js 22 or a compatible recent Node.js release and pnpm. Python 3.9 or newer is optional and is only needed for the diagnostic utility.

## Local development

Install dependencies and start the development server:

```bash
pnpm install
pnpm dev
```

The development server normally runs at `http://localhost:3000`.

## Validation commands

Run the same checks used before delivery:

```bash
pnpm check
pnpm test
pnpm build
```

The test suite covers the assignment router's input validation and the authentication logout procedure.

## Python debugging utility

`tools/debug_project.py` is a small, dependency-free diagnostic script. It checks required project files, verifies the package configuration, runs TypeScript checks, runs tests, and optionally runs the production build and checks a running preview URL.

From the repository root, run:

```bash
python3 tools/debug_project.py
```

To include a running preview check:

```bash
python3 tools/debug_project.py --url http://localhost:3000
```

To skip the production build during a quick diagnostic pass:

```bash
python3 tools/debug_project.py --skip-build
```

The script exits with status `0` when every requested check passes and status `1` when at least one check fails. This makes it suitable for local debugging or a simple CI step.

## Project structure

```text
client/src/       React pages, components, hooks, and styles
server/           Express, tRPC, authentication, and database helpers
drizzle/          Database schema and migrations
shared/           Shared application constants and types
tools/            Local diagnostics and debugging utilities
```

## Data behavior

The assignment API uses tRPC procedures under `/api/trpc`. When a configured database is available, assignments are stored through Drizzle ORM. Preview mode includes deterministic seed assignments so the dashboard remains useful while the database is unavailable.

## License

This project is provided for school-work and learning purposes. Add a license file if you plan to distribute or reuse it publicly.
