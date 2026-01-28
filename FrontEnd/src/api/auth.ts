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

export async function forgotPassword(email: string): Promise<{ message: string }> {
  const data = await apiPost<{ message: string }>("/api/auth/forgot-password", { email });
  return data;
}

export interface RegisterData {
  name: string;
  email: string;
  phone?: string;
  password: string;
  confirm_password: string;
}

export interface RegisterResponse {
  message: string;
  user: {
    id: string;
    email: string;
    name: string;
    phone?: string;
    role: string;
    state: string;
  };
}

export async function register(data: RegisterData): Promise<RegisterResponse> {
  const response = await apiPost<RegisterResponse>("/api/auth/register", data);
  return response;
}
