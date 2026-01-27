// src/api/users.ts
import { apiGet, apiPost, apiPut, apiDelete } from "./http";

type BackendUser = {
  _id: string;
  email: string;
  name?: string | null;
  phone?: string | null;
  role?: "ADMIN" | "CLIENT";
  state?: "activo" | "inactivo";
  created_at?: string;
  reservationsCount?: number;
};

export type UiUser = {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  role: "admin" | "customer";
  isActive: boolean;
  reservationsCount: number;
  createdAt: string;
};

function mapBackendToUiUser(u: BackendUser): UiUser {
  const role: UiUser["role"] = u.role === "ADMIN" ? "admin" : "customer";
  const isActive = (u.state ?? "activo") === "activo";
  const createdAt = u.created_at ? u.created_at.slice(0, 10) : "—";

  return {
    id: u._id,
    name: (u.name ?? "").trim() || u.email,
    email: u.email,
    phone: u.phone ?? null,
    role,
    isActive,
    reservationsCount: u.reservationsCount ?? 0,
    createdAt,
  };
}

/** ======================
 *  Admin: Users CRUD
 *  ====================== */

export async function fetchUsers(): Promise<UiUser[]> {
  // apiGet ya retorna JSON parseado
  const data = await apiGet<{ users: BackendUser[]; count: number }>("/api/users/");
  return (data.users ?? []).map(mapBackendToUiUser);
}

export type CreateUserInput = {
  name: string;
  email: string;
  phone?: string;
  role: "admin" | "customer";
  password: string;
};

export async function createUser(input: CreateUserInput): Promise<UiUser> {
  const payload = {
    name: input.name,
    email: input.email,
    phone: input.phone,
    role: input.role === "admin" ? "ADMIN" : "CLIENT",
    password: input.password,
  };

  const data = await apiPost<{ message: string; user: BackendUser }>("/api/users/", payload);
  return mapBackendToUiUser(data.user);
}

export async function deleteUser(userId: string): Promise<void> {
  // tu backend responde { message: 'Usuario desactivado exitosamente' }
  await apiDelete<{ message: string }>(`/api/users/${userId}`);
}

export type UpdateUserInput = {
  name?: string;
  email?: string;
  phone?: string | null;
  role?: "admin" | "customer";
  password?: string; // opcional
  isActive?: boolean; // state activo/inactivo
};

export async function updateUser(userId: string, input: UpdateUserInput): Promise<UiUser> {
  const payload: any = {};

  if (input.name !== undefined) payload.name = input.name;
  if (input.email !== undefined) payload.email = input.email;
  if (input.phone !== undefined) payload.phone = input.phone;

  if (input.role !== undefined) {
    payload.role = input.role === "admin" ? "ADMIN" : "CLIENT";
  }

  if (input.password) {
    payload.password = input.password;
  }

  if (input.isActive !== undefined) {
    payload.state = input.isActive ? "activo" : "inactivo";
  }

  const data = await apiPut<{ message: string; user: BackendUser }>(`/api/users/${userId}`, payload);
  return mapBackendToUiUser(data.user);
}

/** ======================
 *  Authenticated user: profile
 *  ====================== */

export type UiProfile = {
  id: string;
  email: string;
  name: string;
  phone: string;
  role: "admin" | "customer";
};

export async function getProfile(): Promise<UiProfile> {
  const data = await apiGet<BackendUser>("/api/users/profile");

  return {
    id: data._id,
    email: data.email,
    name: data.name || "",
    phone: data.phone || "",
    role: data.role === "ADMIN" ? "admin" : "customer",
  };
}

export async function updateProfile(profileData: { name?: string; phone?: string }) {
  const data = await apiPut<{ message: string; user: BackendUser }>(
    "/api/users/profile",
    profileData
  );

  return {
    id: data.user._id,
    email: data.user.email,
    name: data.user.name || "",
    phone: data.user.phone || "",
    role: data.user.role === "ADMIN" ? "admin" : "customer",
  };
}

// Obtener usuario por ID (para admins)
export async function getUserById(userId: string): Promise<UiProfile> {
  const data = await apiGet<BackendUser>(`/api/users/${userId}`);

  return {
    id: data._id,
    email: data.email,
    name: data.name || "",
    phone: data.phone || "",
    role: data.role === "ADMIN" ? "admin" : "customer",
  };
}
