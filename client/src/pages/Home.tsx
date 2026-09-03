import DashboardLayout from "@/components/DashboardLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { CalendarDays, Check, CheckCircle2, ChevronRight, Circle, Clock3, Flame, ListTodo, Plus, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import { trpc } from "@/lib/trpc";

type Priority = "low" | "medium" | "high";

const priorityStyles: Record<Priority, string> = {
  high: "bg-[#fff0e8] text-[#b9471c] border-[#ffd8c6]",
  medium: "bg-[#fff8dd] text-[#9a6b00] border-[#f4df9a]",
  low: "bg-[#eaf6f1] text-[#267a5a] border-[#bfe8d5]",
};

const formatDueDate = (date: string) => new Date(`${date}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });

export default function Home() {
  const utils = trpc.useUtils();
  const { data: assignments = [], isLoading, isError } = trpc.assignments.list.useQuery();
  const createMutation = trpc.assignments.create.useMutation({
    onSuccess: async () => { await utils.assignments.list.invalidate(); toast.success("Assignment added to your plan"); setFormOpen(false); },
    onError: () => toast.error("Could not add that assignment"),
  });
  const toggleMutation = trpc.assignments.toggle.useMutation({
    onSuccess: () => utils.assignments.list.invalidate(),
    onError: () => toast.error("Could not update that assignment"),
  });
  const deleteMutation = trpc.assignments.remove.useMutation({
    onSuccess: async () => { await utils.assignments.list.invalidate(); toast.success("Assignment removed"); },
    onError: () => toast.error("Could not remove that assignment"),
  });
  const [formOpen, setFormOpen] = useState(false);
  const [filter, setFilter] = useState<"all" | "pending" | "done">("all");
  const [subject, setSubject] = useState("");
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState("2026-09-12");
  const [priority, setPriority] = useState<Priority>("medium");

  const completed = assignments.filter((assignment) => Boolean(assignment.completed)).length;
  const pending = assignments.length - completed;
  const completion = assignments.length ? Math.round((completed / assignments.length) * 100) : 0;
  const visibleAssignments = useMemo(() => assignments.filter((assignment) => filter === "all" || (filter === "done" ? Boolean(assignment.completed) : !assignment.completed)), [assignments, filter]);
  const upcoming = assignments.filter((assignment) => !assignment.completed).slice(0, 3);

  const submitAssignment = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!subject.trim() || !title.trim() || !dueDate) { toast.error("Add a subject, title, and due date"); return; }
    createMutation.mutate({ subject, title, dueDate, priority });
  };

  return (
    <DashboardLayout>
      <div className="planner-shell min-h-[calc(100vh-2rem)] overflow-hidden rounded-[2rem] bg-[#f7f7f4] text-[#17232e] shadow-[0_18px_60px_rgba(23,35,46,0.08)]">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-[#17232e]/[0.08] px-6 py-5 md:px-10">
          <div className="flex items-center gap-3">
            <div className="brand-mark"><ListTodo className="h-5 w-5" strokeWidth={2.5} /></div>
            <div><p className="font-extrabold tracking-[-0.03em]">Studyday</p><p className="text-[10px] font-bold uppercase tracking-[0.22em] text-[#66717b]">School work planner</p></div>
          </div>
          <div className="flex items-center gap-3"><span className="hidden text-sm font-semibold text-[#66717b] sm:inline">Thursday, September 3</span><div className="avatar">AM</div></div>
        </header>

        <main className="grid gap-8 px-6 py-8 md:px-10 lg:grid-cols-[minmax(0,1fr)_280px] lg:gap-12 lg:py-10">
          <section>
            <div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
              <div><p className="eyebrow">Your week at a glance</p><h1 className="display-title">Make room for<br /><em>good work.</em></h1><p className="mt-4 max-w-md text-sm leading-6 text-[#66717b]">A calm place to see what is due, choose what matters, and keep your momentum going.</p></div>
              <Button onClick={() => setFormOpen((open) => !open)} className="primary-button w-fit"><Plus className="mr-2 h-4 w-4" /> Add assignment</Button>
            </div>

            {formOpen && <form onSubmit={submitAssignment} className="mb-8 grid gap-4 rounded-2xl border border-[#17232e]/10 bg-white p-5 shadow-[0_12px_30px_rgba(23,35,46,0.06)] animate-in fade-in slide-in-from-top-2 duration-200 sm:grid-cols-2">
              <div className="sm:col-span-2"><p className="text-sm font-extrabold">New assignment</p><p className="mt-1 text-xs text-[#66717b]">Keep it specific. Future you will be grateful.</p></div>
              <div><Label htmlFor="subject">Subject</Label><Input id="subject" value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="e.g. Biology" className="mt-2" /></div>
              <div><Label htmlFor="title">Assignment</Label><Input id="title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Cell model notes" className="mt-2" /></div>
              <div><Label htmlFor="due-date">Due date</Label><Input id="due-date" type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} className="mt-2" /></div>
              <div><Label>Priority</Label><Select value={priority} onValueChange={(value) => setPriority(value as Priority)}><SelectTrigger className="mt-2"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="low">Low priority</SelectItem><SelectItem value="medium">Medium priority</SelectItem><SelectItem value="high">High priority</SelectItem></SelectContent></Select></div>
              <div className="flex justify-end gap-2 sm:col-span-2"><Button type="button" variant="ghost" onClick={() => setFormOpen(false)}>Cancel</Button><Button type="submit" className="primary-button" disabled={createMutation.isPending}>{createMutation.isPending ? "Adding…" : "Save assignment"}</Button></div>
            </form>}

            <div className="mb-6 grid gap-3 sm:grid-cols-3">
              <MetricCard label="In progress" value={pending} detail="still on your plate" icon={<Clock3 />} tone="coral" />
              <MetricCard label="Completed" value={completed} detail="small wins count" icon={<CheckCircle2 />} tone="mint" />
              <MetricCard label="Momentum" value={`${completion}%`} detail="of your list done" icon={<Flame />} tone="gold" />
            </div>

            <div className="mb-4 flex flex-wrap items-center justify-between gap-3"><div><p className="eyebrow">Assignments</p><h2 className="section-title">Your task list</h2></div><div className="filter-pills">{(["all", "pending", "done"] as const).map((item) => <button key={item} onClick={() => setFilter(item)} className={filter === item ? "active" : ""}>{item === "all" ? "All" : item === "pending" ? "To do" : "Done"}</button>)}</div></div>
            <div className="space-y-3">
              {isLoading && <div className="rounded-2xl bg-white p-8 text-center text-sm text-[#66717b]">Loading your assignments…</div>}
              {isError && <div className="rounded-2xl border border-[#ffd8c6] bg-[#fff0e8] p-5 text-sm text-[#b9471c]">The planner could not reach its data service. Refresh to try again.</div>}
              {!isLoading && !isError && visibleAssignments.map((assignment) => <AssignmentRow key={assignment.id} assignment={assignment} onToggle={() => toggleMutation.mutate({ id: assignment.id })} onDelete={() => deleteMutation.mutate({ id: assignment.id })} />)}
              {!isLoading && !isError && visibleAssignments.length === 0 && <div className="empty-state"><CheckCircle2 className="mx-auto mb-3 h-8 w-8 text-[#a7cdbd]" /><p className="font-extrabold">Nothing here yet</p><p className="mt-1 text-sm text-[#66717b]">A clear list is a lovely place to start.</p></div>}
            </div>
          </section>

          <aside className="space-y-5">
            <div className="progress-card"><div className="flex items-start justify-between"><div><p className="eyebrow text-[#b8c7d1]">Weekly rhythm</p><h2 className="mt-2 font-serif text-3xl text-white">Keep going.</h2></div><div className="progress-orb"><span>{completion}%</span></div></div><div className="mt-8 h-2 overflow-hidden rounded-full bg-white/15"><div className="h-full rounded-full bg-[#f4b860] transition-all duration-500" style={{ width: `${Math.max(completion, 8)}%` }} /></div><p className="mt-3 text-xs leading-5 text-[#b8c7d1]">You have completed {completed} of {assignments.length || 0} assignments. One focused session at a time.</p></div>
            <div className="rounded-2xl border border-[#17232e]/[0.08] bg-white p-5"><div className="flex items-center justify-between"><div><p className="eyebrow">Next up</p><h2 className="section-title">Coming soon</h2></div><CalendarDays className="h-5 w-5 text-[#e47a55]" /></div><div className="mt-5 space-y-4">{upcoming.map((assignment) => <div key={assignment.id} className="flex items-start gap-3"><div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-[#e47a55]" /><div className="min-w-0"><p className="truncate text-sm font-extrabold">{assignment.title}</p><p className="mt-1 text-xs text-[#66717b]">{assignment.subject} · due {formatDueDate(assignment.dueDate)}</p></div></div>)}{upcoming.length === 0 && <p className="text-sm text-[#66717b]">You are all caught up.</p>}</div><button onClick={() => setFilter("pending")} className="mt-5 flex items-center text-xs font-extrabold text-[#e47a55] transition-transform hover:translate-x-1">View all to-dos <ChevronRight className="ml-1 h-3.5 w-3.5" /></button></div>
            <div className="quote-card"><div className="quote-mark">“</div><p className="relative text-sm font-bold leading-6 text-[#3a454e]">Progress is not about doing everything. It is about doing the next right thing.</p><p className="mt-3 text-[10px] font-extrabold uppercase tracking-[0.18em] text-[#8a7667]">A note for today</p></div>
          </aside>
        </main>
      </div>
    </DashboardLayout>
  );
}

function MetricCard({ label, value, detail, icon, tone }: { label: string; value: number | string; detail: string; icon: React.ReactNode; tone: "coral" | "mint" | "gold" }) {
  return <div className={`metric-card ${tone}`}><div className="flex items-center justify-between"><span className="text-xs font-extrabold uppercase tracking-[0.14em] text-[#66717b]">{label}</span><span className="metric-icon">{icon}</span></div><p className="mt-3 text-3xl font-extrabold tracking-[-0.06em]">{value}</p><p className="mt-1 text-xs text-[#66717b]">{detail}</p></div>;
}

function AssignmentRow({ assignment, onToggle, onDelete }: { assignment: { id: number; subject: string; title: string; dueDate: string; priority: "low" | "medium" | "high"; completed: number }; onToggle: () => void; onDelete: () => void }) {
  const complete = Boolean(assignment.completed);
  return <div className={`assignment-row group ${complete ? "is-complete" : ""}`}><button onClick={onToggle} className="check-button" aria-label={complete ? `Mark ${assignment.title} incomplete` : `Mark ${assignment.title} complete`}>{complete ? <Check className="h-4 w-4" /> : <Circle className="h-4 w-4" />}</button><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><p className="truncate text-sm font-extrabold">{assignment.title}</p><Badge variant="outline" className={`text-[10px] font-extrabold capitalize ${priorityStyles[assignment.priority]}`}>{assignment.priority}</Badge></div><p className="mt-1 text-xs text-[#66717b]">{assignment.subject} <span className="mx-1 text-[#ccd1d3]">•</span> Due {formatDueDate(assignment.dueDate)}</p></div><button onClick={onDelete} className="delete-button" aria-label={`Delete ${assignment.title}`}><Trash2 className="h-4 w-4" /></button></div>;
}
