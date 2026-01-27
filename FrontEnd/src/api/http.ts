// src/api/http.ts
const API_URL = import.meta.env.VITE_API_URL as string;

function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}


function joinUrl(base: string, path: string) {
  const b = base.replace(/\/+$/, "");
  const p = path.replace(/^\/+/, "");
  return `${b}/${p}`;
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = getAccessToken();

  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  return fetch(joinUrl(API_URL, path), {
    ...options,
    headers,
  });
}