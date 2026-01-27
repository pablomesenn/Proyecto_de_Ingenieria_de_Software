import { apiPost } from "./http";
import { apiGet } from "@/api/http";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: {
    _id: string;
    email: string;
    name?: string;
    phone?: string;
    role: "ADMIN" | "CLIENT";
  };
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const data = await apiPost<LoginResponse>("/api/auth/login", { email, password });
  
  // Guardar tokens en localStorage
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  
  return data;
}

export async function logout(): Promise<void> {
  await apiPost("/api/auth/logout");
  
  // Limpiar tokens
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function refreshToken(): Promise<{ access_token: string; refresh_token: string }> {
  const refresh = localStorage.getItem("refresh_token");
  
  if (!refresh) {
    throw new Error("No refresh token available");
  }

  const data = await apiPost<{ access_token: string; refresh_token: string }>(
    "/api/auth/refresh",
    {},
  );
  
  // Actualizar tokens
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  
  return data;
}
