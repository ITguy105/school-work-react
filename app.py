from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("assignments.json")

SEED_ASSIGNMENTS = [
    {"id": 1, "subject": "Literature", "title": "The Odyssey reflection", "due_date": "2026-09-05", "priority": "high", "completed": False},
    {"id": 2, "subject": "Physics", "title": "Motion lab report", "due_date": "2026-09-06", "priority": "medium", "completed": False},
    {"id": 3, "subject": "French", "title": "Verb conjugation practice", "due_date": "2026-09-08", "priority": "low", "completed": True},
    {"id": 4, "subject": "World History", "title": "Industrial Revolution slides", "due_date": "2026-09-10", "priority": "medium", "completed": False},
]


def load_assignments() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return [assignment.copy() for assignment in SEED_ASSIGNMENTS]
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [assignment.copy() for assignment in SEED_ASSIGNMENTS]


def save_assignments(assignments: list[dict[str, Any]]) -> None:
    DATA_FILE.write_text(json.dumps(assignments, indent=2), encoding="utf-8")


@app.get("/")
def index():
    assignments = sorted(load_assignments(), key=lambda item: item["due_date"])
    completed = sum(bool(item["completed"]) for item in assignments)
    pending = len(assignments) - completed
    progress = round(completed / len(assignments) * 100) if assignments else 0
    return render_template_string(
        PAGE,
        assignments=assignments,
        completed=completed,
        pending=pending,
        progress=progress,
        today=date.today().strftime("%A, %B %-d"),
    )


@app.post("/assignments")
def create_assignment():
    subject = request.form.get("subject", "").strip()
    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date", "").strip()
    priority = request.form.get("priority", "medium")
    if subject and title and due_date and priority in {"low", "medium", "high"}:
        assignments = load_assignments()
        next_id = max((item["id"] for item in assignments), default=0) + 1
        assignments.append({"id": next_id, "subject": subject, "title": title, "due_date": due_date, "priority": priority, "completed": False})
        save_assignments(assignments)
    return redirect(url_for("index"))


@app.post("/assignments/<int:assignment_id>/toggle")
def toggle_assignment(assignment_id: int):
    assignments = load_assignments()
    for assignment in assignments:
        if assignment["id"] == assignment_id:
            assignment["completed"] = not assignment["completed"]
            break
    save_assignments(assignments)
    return redirect(url_for("index"))


@app.post("/assignments/<int:assignment_id>/delete")
def delete_assignment(assignment_id: int):
    assignments = [item for item in load_assignments() if item["id"] != assignment_id]
    save_assignments(assignments)
    return redirect(url_for("index"))


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Studyday — School Work Planner</title>
  <style>
    :root { --ink:#17232e; --muted:#66717b; --coral:#e47a55; --mint:#ecf8f2; --cream:#f7f7f4; --gold:#f4b860; }
    * { box-sizing:border-box; } body { margin:0; color:var(--ink); background:#eef0ed; font-family:Arial, sans-serif; }
    .shell { max-width:1180px; margin:24px auto; overflow:hidden; border-radius:28px; background:var(--cream); box-shadow:0 18px 60px #17232e14; }
    header { display:flex; justify-content:space-between; align-items:center; padding:22px 34px; border-bottom:1px solid #17232e12; }
    .brand { display:flex; align-items:center; gap:12px; font-weight:800; } .mark { display:grid; place-items:center; width:36px; height:36px; border-radius:12px; color:var(--gold); background:var(--ink); }
    .eyebrow { color:var(--coral); font-size:11px; font-weight:800; letter-spacing:2px; text-transform:uppercase; } .muted { color:var(--muted); }
    main { display:grid; grid-template-columns:minmax(0,1fr) 280px; gap:46px; padding:44px 48px 56px; } h1 { margin:10px 0 0; font-family:Georgia,serif; font-size:clamp(48px,7vw,86px); font-weight:400; letter-spacing:-5px; line-height:.9; } h1 em { color:var(--coral); font-style:normal; } h2 { font-family:Georgia,serif; font-size:30px; font-weight:400; letter-spacing:-1px; }
    .intro { max-width:520px; } .intro p { max-width:420px; line-height:1.6; } .topline { display:flex; align-items:end; justify-content:space-between; gap:20px; } button, input, select { font:inherit; } button { cursor:pointer; }
    .button { border:0; border-radius:12px; padding:13px 17px; color:#fff; background:var(--ink); font-weight:800; box-shadow:0 8px 18px #17232e24; } .button:hover { background:#2b3d4a; }
    .metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:32px 0; } .metric { min-height:130px; padding:18px; border:1px solid #17232e10; border-radius:18px; } .coral { background:#fff4ee; } .mint { background:var(--mint); } .gold { background:#fff8e8; } .metric strong { display:block; margin-top:15px; font-size:34px; } .metric small { color:var(--muted); }
    .list-head { display:flex; align-items:end; justify-content:space-between; gap:12px; } .filters { display:flex; gap:4px; padding:4px; border-radius:12px; background:#e9ebe8; } .filters button { border:0; border-radius:9px; padding:7px 11px; color:var(--muted); background:transparent; font-size:12px; font-weight:800; } .filters button:hover { color:var(--ink); background:#fff; }
    .task { display:flex; align-items:center; gap:14px; margin:12px 0; padding:16px; border:1px solid #17232e10; border-radius:16px; background:#fff; box-shadow:0 6px 20px #17232e09; } .task.done { background:#ecf8f2; } .task.done .task-title { color:#789184; text-decoration:line-through; } .check { width:30px; height:30px; border:2px solid #cbd3d4; border-radius:50%; color:#fff; background:#fff; } .done .check { border-color:#75a48f; background:#75a48f; } .task-title { font-weight:800; } .task-meta { margin-top:5px; color:var(--muted); font-size:12px; } .priority { margin-left:8px; padding:4px 8px; border-radius:99px; font-size:10px; font-weight:800; text-transform:capitalize; } .priority.high { color:#b9471c; background:#fff0e8; } .priority.medium { color:#9a6b00; background:#fff8dd; } .priority.low { color:#267a5a; background:#eaf6f1; } .delete { margin-left:auto; border:0; color:#a0abad; background:transparent; } .delete:hover { color:#b9471c; }
    aside > * { margin-bottom:16px; } .progress-card { padding:24px; border-radius:20px; color:#fff; background:#233744; } .progress-card h2 { margin:8px 0 28px; } .progress-bar { height:8px; overflow:hidden; border-radius:99px; background:#ffffff24; } .progress-bar span { display:block; height:100%; border-radius:99px; background:var(--gold); } .progress-card p { color:#b8c7d1; font-size:12px; line-height:1.6; } .note { padding:24px; border-radius:20px; background:#f4eee6; font-weight:700; line-height:1.6; }
    .form { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:22px 0; padding:20px; border:1px solid #17232e12; border-radius:18px; background:#fff; } .form label { display:grid; gap:7px; color:var(--muted); font-size:12px; font-weight:800; } .form input, .form select { width:100%; padding:11px; border:1px solid #ccd5d6; border-radius:10px; } .form .full { grid-column:1/-1; } .empty { padding:36px; color:var(--muted); text-align:center; border:1px dashed #b8c7c0; border-radius:16px; }
    @media (max-width:800px) { .shell { margin:0; border-radius:0; } header { padding:18px 20px; } main { display:block; padding:30px 20px 44px; } aside { margin-top:30px; } .metrics { grid-template-columns:1fr; } .topline, .list-head { align-items:start; flex-direction:column; } .form { grid-template-columns:1fr; } .form .full { grid-column:auto; } }
  </style>
</head>
<body><div class="shell"><header><div class="brand"><span class="mark">✓</span><span>Studyday<br><small class="eyebrow">School work planner</small></span></div><span class="muted">{{ today }}</span></header>
<main><section><div class="topline"><div class="intro"><div class="eyebrow">Your week at a glance</div><h1>Make room for<br><em>good work.</em></h1><p class="muted">A calm place to see what is due, choose what matters, and keep your momentum going.</p></div><a class="button" href="#new">＋ Add assignment</a></div>
<div class="metrics"><div class="metric coral"><span class="eyebrow">In progress</span><strong>{{ pending }}</strong><small>still on your plate</small></div><div class="metric mint"><span class="eyebrow">Completed</span><strong>{{ completed }}</strong><small>small wins count</small></div><div class="metric gold"><span class="eyebrow">Momentum</span><strong>{{ progress }}%</strong><small>of your list done</small></div></div>
<div class="list-head"><div><div class="eyebrow">Assignments</div><h2>Your task list</h2></div><div class="filters"><button onclick="filterTasks('all')">All</button><button onclick="filterTasks('pending')">To do</button><button onclick="filterTasks('done')">Done</button></div></div>
<div id="tasks">{% for assignment in assignments %}<div class="task {{ 'done' if assignment.completed else '' }}" data-status="{{ 'done' if assignment.completed else 'pending' }}"><form method="post" action="{{ url_for('toggle_assignment', assignment_id=assignment.id) }}"><button class="check" aria-label="Toggle completion">{{ '✓' if assignment.completed else '' }}</button></form><div><div class="task-title">{{ assignment.title }} <span class="priority {{ assignment.priority }}">{{ assignment.priority }}</span></div><div class="task-meta">{{ assignment.subject }} · Due {{ assignment.due_date }}</div></div><form class="delete" method="post" action="{{ url_for('delete_assignment', assignment_id=assignment.id) }}"><button class="delete" aria-label="Delete assignment">✕</button></form></div>{% else %}<div class="empty">Nothing here yet. A clear list is a lovely place to start.</div>{% endfor %}</div>
<form id="new" class="form" method="post" action="{{ url_for('create_assignment') }}"><div class="full"><div class="eyebrow">New assignment</div></div><label>Subject<input name="subject" required placeholder="e.g. Biology"></label><label>Assignment<input name="title" required placeholder="e.g. Cell model notes"></label><label>Due date<input name="due_date" type="date" required></label><label>Priority<select name="priority"><option>low</option><option selected>medium</option><option>high</option></select></label><div class="full"><button class="button" type="submit">Save assignment</button></div></form>
</section><aside><div class="progress-card"><div class="eyebrow" style="color:#b8c7d1">Weekly rhythm</div><h2>Keep going.</h2><div class="progress-bar"><span style="width:{{ progress }}%"></span></div><p>You have completed {{ completed }} of {{ assignments|length }} assignments. One focused session at a time.</p></div><div class="note">“Progress is not about doing everything. It is about doing the next right thing.”<br><small class="eyebrow">A note for today</small></div></aside></main></div>
<script>function filterTasks(status){document.querySelectorAll('.task').forEach(t=>t.style.display=(status==='all'||t.dataset.status===status)?'flex':'none')}</script></body></html>
"""


if __name__ == "__main__":
    app.run(debug=True)
