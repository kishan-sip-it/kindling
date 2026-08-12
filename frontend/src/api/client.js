const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function handle(response) {
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function authHeaders() {
  const token = localStorage.getItem("leadflow_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`, { headers: { ...authHeaders() } });
  return handle(res);
}

export async function apiPost(path, body, { auth = true } = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(auth ? authHeaders() : {}) },
    body: JSON.stringify(body),
  });
  return handle(res);
}

export async function apiPatch(path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body),
  });
  return handle(res);
}
