import { useEffect, useState, useCallback } from "react";
import { UserPlus, ShieldCheck, User as UserIcon } from "lucide-react";
import { apiGet, apiPost } from "../api/client";
import AppNav from "../components/AppNav";
import Footer from "../components/Footer";

const EMPTY = { email: "", full_name: "", password: "", role: "member" };

export default function Team() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      setUsers(await apiGet("/api/users"));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function setField(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleCreate(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const created = await apiPost("/api/users", form);
      setSuccess(`Created ${created.full_name} (${created.role}) — share the password you set with them directly.`);
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <AppNav />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8">
        <h1 className="text-2xl font-display font-semibold text-stone-900">Team</h1>
        <p className="mt-1 text-sm text-stone-500">Create admin or member accounts. Only admins can see this page.</p>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <h2 className="mb-4 flex items-center gap-1.5 text-sm font-bold text-stone-800">
              <UserPlus className="h-4 w-4" /> Add a team member
            </h2>
            <form onSubmit={handleCreate} className="space-y-3">
              <Field label="Full name" required value={form.full_name} onChange={(v) => setField("full_name", v)} />
              <Field label="Email" type="email" required value={form.email} onChange={(v) => setField("email", v)} />
              <Field label="Temporary password" type="text" required minLength={8} value={form.password} onChange={(v) => setField("password", v)} />
              <label className="block">
                <span className="text-xs font-semibold text-stone-600">Role</span>
                <select
                  value={form.role}
                  onChange={(e) => setField("role", e.target.value)}
                  className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                </select>
              </label>

              {error && <p className="text-sm text-rose-600">{error}</p>}
              {success && <p className="text-sm text-emerald-600">{success}</p>}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full rounded-lg bg-stone-900 px-4 py-2.5 text-sm font-semibold text-amber-400 transition hover:bg-stone-800 disabled:opacity-50"
              >
                {isSubmitting ? "Creating…" : "Create account"}
              </button>
            </form>
          </div>

          <div className="rounded-2xl border border-stone-200 bg-white p-6">
            <h2 className="mb-4 text-sm font-bold text-stone-800">Current team ({users.length})</h2>
            {isLoading ? (
              <p className="text-sm text-stone-400">Loading…</p>
            ) : (
              <div className="space-y-2">
                {users.map((u) => (
                  <div key={u.id} className="flex items-center gap-3 rounded-lg border border-stone-100 bg-stone-50 px-3 py-2">
                    <span className={`grid h-8 w-8 place-items-center rounded-full ${u.role === "admin" ? "bg-amber-100 text-amber-700" : "bg-stone-200 text-stone-600"}`}>
                      {u.role === "admin" ? <ShieldCheck className="h-4 w-4" /> : <UserIcon className="h-4 w-4" />}
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-stone-800">{u.full_name}</p>
                      <p className="text-xs text-stone-400">{u.email} · {u.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

function Field({ label, type = "text", required, minLength, value, onChange }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold text-stone-600">{label}</span>
      <input
        type={type}
        required={required}
        minLength={minLength}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
      />
    </label>
  );
}
