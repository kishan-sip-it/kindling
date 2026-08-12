import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import { apiGet } from "../api/client";
import AppNav from "../components/AppNav";
import StatusBadge from "../components/StatusBadge";
import Footer from "../components/Footer";

const STATUSES = ["new", "contacted", "qualified", "won", "lost"];
const STAGE_LABELS = { new: "Spark", contacted: "Warming", qualified: "Catching", won: "Ablaze", lost: "Ash" };
const PAGE_SIZE = 10;

export default function Dashboard() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
      if (statusFilter) params.set("status", statusFilter);
      if (search) params.set("search", search);
      const result = await apiGet(`/api/leads?${params.toString()}`);
      setLeads(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [page, statusFilter, search]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <AppNav />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-stone-900">Leads</h1>
            <p className="text-sm text-stone-500">{total} total</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-stone-400" />
              <input
                value={search}
                onChange={(e) => {
                  setPage(1);
                  setSearch(e.target.value);
                }}
                placeholder="Search name, email, company…"
                className="w-64 rounded-lg border border-stone-300 py-2 pl-8 pr-3 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => {
                setPage(1);
                setStatusFilter(e.target.value);
              }}
              className="rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
            >
              <option value="">All statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{STAGE_LABELS[s]}</option>
              ))}
            </select>
          </div>
        </div>

        {error && <p className="mb-4 text-sm text-rose-600">{error}</p>}

        <div className="overflow-hidden rounded-xl border border-stone-200 bg-white">
          <table className="w-full text-sm">
            <thead className="border-b border-stone-200 bg-stone-50 text-left text-xs font-bold uppercase tracking-wide text-stone-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Company</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Assigned to</th>
                <th className="px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-stone-400">Loading…</td></tr>
              ) : leads.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-stone-400">No leads found.</td></tr>
              ) : (
                leads.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => navigate(`/leads/${lead.id}`)}
                    className="cursor-pointer border-b border-stone-100 last:border-0 hover:bg-stone-50"
                  >
                    <td className="px-4 py-3">
                      <p className="font-semibold text-stone-800">{lead.name}</p>
                      <p className="text-xs text-stone-400">{lead.email}</p>
                    </td>
                    <td className="px-4 py-3 text-stone-600">{lead.company || "—"}</td>
                    <td className="px-4 py-3"><StatusBadge status={lead.status} /></td>
                    <td className="px-4 py-3 text-stone-600">{lead.assigned_to_name || <span className="text-stone-400">Unassigned</span>}</td>
                    <td className="px-4 py-3 text-stone-500">{new Date(lead.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between text-sm text-stone-500">
          <span>Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="flex items-center gap-1 rounded-lg border border-stone-200 px-3 py-1.5 font-semibold disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" /> Prev
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="flex items-center gap-1 rounded-lg border border-stone-200 px-3 py-1.5 font-semibold disabled:opacity-40"
            >
              Next <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
