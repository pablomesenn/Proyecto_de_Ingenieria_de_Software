// src/api/http.ts
const API_URL = import.meta.env.VITE_API_URL as string;

// Flag para evitar loops infinitos de refresh
let isRefreshing = false;
let failedQueue: Array<{ resolve: (value?: unknown) => void; reject: (reason?: any) => void }> = [];

function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

function getRefreshToken(): string | null {
  return localStorage.getItem("refresh_token");
}

function setTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

const processQueue = (error: any = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  
  if (!refreshToken) {
    return false;
  }

  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${refreshToken}`,
      },
    });

    if (!res.ok) {
      throw new Error("Failed to refresh token");
    }

    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch (error) {
    clearTokens();
    return false;
  }
}

async function fetchWithAuth(url: string, options: RequestInit): Promise<Response> {
  const token = getAccessToken();

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  // Si no es 401, retornar respuesta normal
  if (response.status !== 401) {
    return response;
  }

  // Si ya estamos refrescando, esperar
  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      failedQueue.push({ resolve, reject });
    }).then(() => {
      // Reintentar con el nuevo token
      const newToken = getAccessToken();
      return fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...(newToken ? { Authorization: `Bearer ${newToken}` } : {}),
          ...options.headers,
        },
      });
    });
  }

  // Intentar refrescar el token
  isRefreshing = true;

  try {
    const refreshed = await refreshAccessToken();
    
    if (refreshed) {
      processQueue();
      isRefreshing = false;

      // Reintentar la petición original con el nuevo token
      const newToken = getAccessToken();
      return fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...(newToken ? { Authorization: `Bearer ${newToken}` } : {}),
          ...options.headers,
        },
      });
    } else {
      // Refresh falló, limpiar y redirigir al login
      processQueue(new Error("Session expired"));
      isRefreshing = false;
      
      // Redirigir al login
      window.location.href = "/login";
      throw new Error("Session expired");
    }
  } catch (error) {
    processQueue(error);
    isRefreshing = false;
    throw error;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetchWithAuth(`${API_URL}${path}`, {
    method: "GET",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function apiPut<T>(path: string, body?: any): Promise<T> {
  const res = await fetchWithAuth(`${API_URL}${path}`, {
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body?: any): Promise<T> {
  const res = await fetchWithAuth(`${API_URL}${path}`, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetchWithAuth(`${API_URL}${path}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// src/api/http.ts
export async function apiDownload(path: string): Promise<{ blob: Blob; filename: string | null }> {
  const res = await fetchWithAuth(`${API_URL}${path}`, { method: "GET" });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  const blob = await res.blob();

  const cd = res.headers.get("content-disposition") || res.headers.get("Content-Disposition");
  let filename: string | null = null;

  if (cd) {
    // Content-Disposition: attachment; filename="reservas-2026-01-27.xlsx"
    const match = cd.match(/filename\*?=(?:UTF-8''|")?([^\";]+)\"?/i);
    if (match?.[1]) filename = decodeURIComponent(match[1]);
  }

  return { blob, filename };
}
