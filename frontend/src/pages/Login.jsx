import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, Link } from "react-router-dom";
import { Flame } from "lucide-react";
import { apiPost } from "../api/client";
import { setSession } from "../store/authSlice";
import Footer from "../components/Footer";

export default function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiPost("/api/auth/login", { email, password }, { auth: false });
      dispatch(setSession(result));
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <div className="flex flex-1 items-center justify-center px-4">
        <div className="w-full max-w-sm rounded-2xl border border-stone-200 bg-white p-8 shadow-sm">
          <div className="mb-6 flex items-center gap-2">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-stone-900 text-amber-400">
              <Flame className="h-4.5 w-4.5" />
            </span>
            <span className="text-lg font-display font-semibold text-stone-900">Kindling</span>
          </div>
          <h1 className="text-2xl font-display font-semibold text-stone-900">Sign in</h1>
          <p className="mt-1 text-sm text-stone-500">Admin and team member access.</p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className="text-xs font-semibold text-stone-600">Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100"
              />
            </label>
            <label className="block">
              <span className="text-xs font-semibold text-stone-600">Password</span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100"
              />
            </label>

            {error && <p className="text-sm text-rose-600">{error}</p>}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-amber-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:opacity-50"
            >
              {isLoading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-stone-400">
            <Link to="/" className="font-semibold text-amber-600 hover:underline">← Back to lead form</Link>
          </p>
        </div>
      </div>
      <Footer />
    </div>
  );
}
