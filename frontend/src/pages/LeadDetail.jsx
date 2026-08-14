import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { useSelector } from "react-redux";
import { ArrowLeft, UserPlus, Clock } from "lucide-react";
import { apiGet, apiPatch, apiPost } from "../api/client";
import AppNav from "../components/AppNav";
import StatusBadge from "../components/StatusBadge";
import Footer from "../components/Footer";

const STATUSES = ["new", "contacted", "qualified", "won", "lost"];
const STAGE_LABELS = { new: "Spark", contacted: "Warming", qualified: "Catching", won: "Ablaze", lost: "Ash" };

export default function LeadDetail() {
  const { id } = useParams();
  const { role, fullName } = useSelector((state) => state.auth);
  const [lead, setLead] = useState(null);
  const [users, setUsers] = useState([]);
  const [noteText, setNoteText] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const [leadData, usersData] = await Promise.all([apiGet(`/api/leads/${id}`), apiGet("/api/users")]);
      setLead(leadData);
      setUsers(usersData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleStatusChange(newStatus) {
    setError(null);
    try {
      await apiPatch(`/api/leads/${id}/status`, { status: newStatus });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAssign(userId) {
    setError(null);
    try {
      await apiPatch(`/api/leads/${id}/assign`, { assigned_to_id: userId || null });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAddNote(e) {
    e.preventDefault();
    if (!noteText.trim()) return;
    setError(null);
    try {
      await apiPost(`/api/leads/${id}/notes`, { content: noteText.trim() });
      setNoteText("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  if (isLoading) return <PageShell><p className="text-stone-400">Loading…</p></PageShell>;
  if (!lead) return <PageShell><p className="text-rose-600">{error || "Lead not found."}</p></PageShell>;

  const currentUser = users.find((u) => u.full_name === fullName);
  const isAssignedToMe = currentUser && lead.assigned_to_id === currentUser.id;
  const canModify = role === "admin" || isAssignedToMe;

  return (
    <PageShell>
      <Link to="/dashboard" className="mb-4 inline-flex items-center gap-1.5 text-sm font-semibold text-stone-500 hover:text-stone-800">
        <ArrowLeft className="h-4 w-4" /> Back to leads
      </Link>

      {error && <p className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-xl font-bold text-stone-900">{lead.name}</h1>
                <p className="text-sm text-stone-500">{lead.email} {lead.phone && `· ${lead.phone}`}</p>
              </div>
              <StatusBadge status={lead.status} />
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div><dt className="text-xs text-stone-400">Company</dt><dd className="text-stone-700">{lead.company || "—"}</dd></div>
              <div><dt className="text-xs text-stone-400">Company size</dt><dd className="text-stone-700">{lead.company_size || "—"}</dd></div>
              <div><dt className="text-xs text-stone-400">Source</dt><dd className="text-stone-700">{lead.source}</dd></div>
              <div><dt className="text-xs text-stone-400">Created</dt><dd className="text-stone-700">{new Date(lead.created_at).toLocaleString()}</dd></div>
            </dl>
            {lead.message && (
              <div className="mt-4 rounded-lg bg-stone-50 p-3 text-sm text-stone-600">"{lead.message}"</div>
            )}
          </div>

          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <h2 className="mb-3 text-sm font-bold text-stone-800">Notes</h2>
            {canModify ? (
              <form onSubmit={handleAddNote} className="mb-4 flex gap-2">
                <input
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Add a note…"
                  className="flex-1 rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
                />
                <button type="submit" className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700">
                  Add
                </button>
              </form>
            ) : (
              <p className="mb-4 text-xs text-stone-400">Only the assigned member (or an admin) can add notes.</p>
            )}
            <div className="space-y-3">
              {lead.notes.length === 0 && <p className="text-sm text-stone-400">No notes yet.</p>}
              {lead.notes.map((note) => (
                <div key={note.id} className="rounded-lg border border-stone-100 bg-stone-50 p-3 text-sm">
                  <p className="text-stone-700">{note.content}</p>
                  <p className="mt-1 text-xs text-stone-400">{note.author_name} · {new Date(note.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <h2 className="mb-3 text-sm font-bold text-stone-800">Status</h2>
            <select
              value={lead.status}
              disabled={!canModify}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:bg-stone-100"
            >
              {STATUSES.map((s) => <option key={s} value={s}>{STAGE_LABELS[s]}</option>)}
            </select>
            {!canModify && <p className="mt-2 text-xs text-stone-400">Only the assigned member (or an admin) can change status.</p>}
          </div>

          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <h2 className="mb-3 flex items-center gap-1.5 text-sm font-bold text-stone-800">
              <UserPlus className="h-4 w-4" /> Assignment
            </h2>
            {role === "admin" ? (
              <select
                value={lead.assigned_to_id || ""}
                onChange={(e) => handleAssign(e.target.value || null)}
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
              >
                <option value="">Unassigned</option>
                {users.filter((u) => u.is_active).map((u) => <option key={u.id} value={u.id}>{u.full_name} ({u.role})</option>)}
              </select>
            ) : lead.assigned_to_id ? (
              <p className="text-sm text-stone-600">Assigned to <strong>{lead.assigned_to_name}</strong></p>
            ) : (
              <button
                onClick={() => currentUser && handleAssign(currentUser.id)}
                className="w-full rounded-lg bg-amber-600 px-3 py-2 text-sm font-semibold text-white hover:bg-amber-700"
              >
                Claim this lead
              </button>
            )}
          </div>

          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <h2 className="mb-3 flex items-center gap-1.5 text-sm font-bold text-stone-800">
              <Clock className="h-4 w-4" /> Activity trail
            </h2>
            <div className="space-y-3">
              {lead.activity.map((a) => (
                <div key={a.id} className="text-xs">
                  <p className="font-semibold text-stone-700">
                    {a.action.replace("_", " ")} {a.actor_name && <span className="text-stone-400">by {a.actor_name}</span>}
                  </p>
                  {a.detail && <p className="text-stone-500">{a.detail}</p>}
                  <p className="text-stone-400">{new Date(a.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </PageShell>
  );
}

function PageShell({ children }) {
  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <AppNav />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">{children}</main>
      <Footer />
    </div>
  );
}
