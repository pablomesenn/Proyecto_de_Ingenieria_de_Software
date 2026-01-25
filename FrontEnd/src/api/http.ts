const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

function getAccessToken(): string | null {
  return localStorage.getItem("access_token"); // ajusta si usas otro nombre
}

export async function apiGet<T>(path: string): Promise<T> {
  const token = getAccessToken();

  const res = await fetch(`${API_URL}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}
