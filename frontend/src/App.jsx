import { Routes, Route } from "react-router-dom";
import PublicCapture from "./pages/PublicCapture";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import LeadDetail from "./pages/LeadDetail";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PublicCapture />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/leads/:id"
        element={
          <ProtectedRoute>
            <LeadDetail />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
