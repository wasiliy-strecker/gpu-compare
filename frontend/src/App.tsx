import Benchmarks from "./Benchmarks";

const csrfKey = "gpu_compare_csrf";

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  const token = sessionStorage.getItem(csrfKey);
  if (token) headers.set("X-CSRF-Token", token);
  const response = await fetch("/api" + path, {
    ...options,
    headers,
    credentials: "same-origin",
  });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) sessionStorage.removeItem(csrfKey);
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Anfrage fehlgeschlagen.",
    );
  }
  return data;
}

async function ensureSession() {
  const current = await fetch("/api/demo-sessions/current", {
    credentials: "same-origin",
  });
  if (!current.ok && current.status !== 401)
    throw new Error("Sitzung gerade nicht erreichbar.");
  const data = current.ok
    ? await current.json()
    : await api<{ csrf_token: string }>("/demo-sessions", { method: "POST" });
  sessionStorage.setItem(csrfKey, data.csrf_token);
}

export default function App() {
  return (
    <main>
      <Benchmarks api={api} ensureSession={ensureSession} />
    </main>
  );
}
