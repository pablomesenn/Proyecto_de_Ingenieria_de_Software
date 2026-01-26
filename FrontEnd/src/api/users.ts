import { apiGet, apiPut } from "./http";

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
  const data = await apiGet<{ users: BackendUser[]; count: number }>("/api/users/");

  return data.users.map((u) => {
    const role = u.role === "ADMIN" ? "admin" : "customer";
    const isActive = (u.state ?? "activo") === "activo";
    const createdAt = u.created_at ? u.created_at.slice(0, 10) : "â€”";

    return {
      id: u._id,
      name: (u.name ?? "").trim() || u.email,
      email: u.email,
      phone: u.phone ?? null,
      role,
      isActive,
      reservationsCount: 0, // luego lo conectamos real
      createdAt,
    };
  });
}

// Obtener perfil del usuario autenticado
export async function getProfile() {
  const data = await apiGet<BackendUser>("/api/users/profile");
  
  return {
    id: data._id,
    email: data.email,
    name: data.name || "",
    phone: data.phone || "",
    role: data.role === "ADMIN" ? "admin" : "customer",
  };
}

// Actualizar perfil del usuario
export async function updateProfile(profileData: { name?: string; phone?: string }) {
  const data = await apiPut<{ message: string; user: BackendUser }>("/api/users/profile", profileData);
  
  return {
    id: data.user._id,
    email: data.user.email,
    name: data.user.name || "",
    phone: data.user.phone || "",
    role: data.user.role === "ADMIN" ? "admin" : "customer",
  };
}

// Obtener usuario por ID (para admins)
export async function getUserById(userId: string) {
  const data = await apiGet<BackendUser>(`/api/users/${userId}`);
  
  return {
    id: data._id,
    email: data.email,
    name: data.name || "",
    phone: data.phone || "",
    role: data.role === "ADMIN" ? "admin" : "customer",
  };
}