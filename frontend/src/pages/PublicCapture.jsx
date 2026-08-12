import { useState } from "react";
import { Link } from "react-router-dom";
import { Flame, CheckCircle2 } from "lucide-react";
import { apiPost } from "../api/client";
import Footer from "../components/Footer";

const EMPTY = { name: "", email: "", phone: "", company: "", company_size: "", message: "" };

export default function PublicCapture() {
  const [form, setForm] = useState(EMPTY);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function setField(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await apiPost("/api/public/leads", form, { auth: false });
      setSubmitted(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <div className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-md rounded-2xl border border-stone-200 bg-white p-8 shadow-sm">
          <div className="mb-6 flex items-center gap-2">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-stone-900 text-amber-400">
              <Flame className="h-4.5 w-4.5" />
            </span>
            <span className="text-lg font-display font-semibold text-stone-900">Kindling</span>
          </div>

          {submitted ? (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center">
              <CheckCircle2 className="mx-auto mb-2 h-8 w-8 text-emerald-600" />
              <p className="font-semibold text-emerald-800">Thanks — we've got it!</p>
              <p className="mt-1 text-sm text-emerald-700">Someone from our team will be in touch shortly.</p>
            </div>
          ) : (
            <>
          <h1 className="text-2xl font-display font-semibold text-stone-900">Talk to our team</h1>
          <p className="mt-1 text-sm italic text-amber-700">Every deal starts as a spark.</p>
          <p className="mt-2 text-sm text-stone-500">Tell us a bit about you and we'll reach out.</p>

              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                <Field label="Full name" required value={form.name} onChange={(v) => setField("name", v)} />
                <Field label="Email" type="email" required value={form.email} onChange={(v) => setField("email", v)} />
                <Field label="Phone" value={form.phone} onChange={(v) => setField("phone", v)} />
                <Field label="Company" value={form.company} onChange={(v) => setField("company", v)} />
                <Field label="Company size" placeholder="e.g. 11-50" value={form.company_size} onChange={(v) => setField("company_size", v)} />
                <label className="block">
                  <span className="text-xs font-semibold text-stone-600">What can we help with?</span>
                  <textarea
                    rows={3}
                    value={form.message}
                    onChange={(e) => setField("message", e.target.value)}
                    className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100"
                  />
                </label>

                {error && <p className="text-sm text-rose-600">{error}</p>}

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full rounded-lg bg-amber-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:opacity-50"
                >
                  {isSubmitting ? "Submitting…" : "Submit"}
                </button>
              </form>
            </>
          )}

          <p className="mt-6 text-center text-xs text-stone-400">
            Team member? <Link to="/login" className="font-semibold text-amber-600 hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
      <Footer />
    </div>
  );
}

function Field({ label, type = "text", required, placeholder, value, onChange }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold text-stone-600">
        {label}
        {required && <span className="ml-0.5 text-rose-500">*</span>}
      </span>
      <input
        type={type}
        required={required}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100"
      />
    </label>
  );
}
