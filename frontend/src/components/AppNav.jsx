import { useDispatch, useSelector } from "react-redux";
import { useNavigate, Link } from "react-router-dom";
import { LogOut } from "lucide-react";
import { logout } from "../store/authSlice";

export default function AppNav() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { role, fullName } = useSelector((state) => state.auth);

  function handleLogout() {
    dispatch(logout());
    navigate("/login");
  }

  return (
    <header className="border-b border-stone-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link to="/dashboard" className="flex items-center gap-2">
        <img
          src="/km-logo.png"
          alt="KM"
          className="h-8 w-8 rounded-lg object-cover"
        />
          <span className="font-display font-semibold text-stone-900">Kindling</span>
        </Link>
        <div className="flex items-center gap-3">
          {role === "admin" && (
            <Link to="/team" className="text-sm font-semibold text-stone-600 hover:text-amber-700">
              Team
            </Link>
          )}
          <span className="hidden text-sm text-stone-600 sm:inline">
            {fullName} · <span className="font-semibold capitalize text-amber-600">{role}</span>
          </span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 rounded-lg border border-stone-200 px-3 py-1.5 text-xs font-semibold text-stone-600 hover:bg-stone-50"
          >
            <LogOut className="h-3.5 w-3.5" />
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
