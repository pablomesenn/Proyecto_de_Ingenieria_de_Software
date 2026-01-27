import { apiFetch } from "./http";

type BackendUser = {
  _id: string;
  email: string;
  name?: string | null;
  phone?: string | null;
  role?: "ADMIN" | "CLIENT";
  state?: "activo" | "inactivo";
  created_at?: string;
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

export async function fetchUsers(): Promise<UiUser[]> {
   const res = await apiFetch("/users/", { method: "GET" });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`GET /users/ -> ${res.status}: ${txt}`);
  }

  const data = await res.json();
  return data.users.map((u) => {
    const role = u.role === "ADMIN" ? "admin" : "customer";
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
  });
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

  const res = await apiFetch("/users/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`POST /users/ -> ${res.status}: ${txt}`);
  }

  const data = await res.json();
  const u: BackendUser = data.user;

  const role = u.role === "ADMIN" ? "admin" : "customer";
  const isActive = (u.state ?? "activo") === "activo";
  const createdAt = u.created_at ? u.created_at.slice(0, 10) : "—";

  return {
    id: u._id,
    name: (u.name ?? "").trim() || u.email,
    email: u.email,
    phone: u.phone ?? null,
    role,
    isActive,
    reservationsCount: 0,
    createdAt,
  };
}

export async function deleteUser(userId: string): Promise<void> {
  const res = await apiFetch(`/users/${userId}`, { method: "DELETE" });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`DELETE /users/${userId} -> ${res.status}: ${txt}`);
  }
}

// Additional function updateUserStatus.

export type UpdateUserInput = {
  name?: string;
  email?: string;
  phone?: string | null;
  role?: "admin" | "customer";
  password?: string; // opcional, solo si quieres cambiarla
  isActive?: boolean; // para state activo/inactivo
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

  const res = await apiFetch(`/users/${userId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`PUT /users/${userId} -> ${res.status}: ${txt}`);
  }

  const data = await res.json();
  const u: BackendUser = data.user;

  const role = u.role === "ADMIN" ? "admin" : "customer";
  const isActive = (u.state ?? "activo") === "activo";
  const createdAt = u.created_at ? u.created_at.slice(0, 10) : "—";

  return {
    id: u._id,
    name: (u.name ?? "").trim() || u.email,
    email: u.email,
    phone: u.phone ?? null,
    role,
    isActive,
    reservationsCount: 0,
    createdAt,
  };
}
