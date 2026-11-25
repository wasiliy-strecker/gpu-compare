import Benchmarks from "./Benchmarks";

const csrfKey = "gpu_compare_csrf";

async function request(path: string, options: RequestInit = {}) {
  const load = () =>
    fetch("/api" + path, { ...options, credentials: "same-origin" });
  const deadline = Date.now() + 45_000;
  let response = await load();
  while ((options.method ?? "GET") === "GET" && response.status === 503) {
    const delay = Number(response.headers.get("Retry-After")) * 1000;
    if (!Number.isFinite(delay) || delay <= 0 || Date.now() + delay > deadline)
      break;
    await new Promise((resolve) => setTimeout(resolve, delay));
    response = await load();
  }
  return response;
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  const token = sessionStorage.getItem(csrfKey);
  if (token) headers.set("X-CSRF-Token", token);
  const response = await request(path, { ...options, headers });
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
  const current = await request("/demo-sessions/current");
  if (!current.ok && current.status !== 401)
    throw new Error("Sitzung gerade nicht erreichbar.");
  // Aurora may be paused. Wait on a public read before the single session write.
  if (!current.ok) await api("/benchmarks/results");
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
