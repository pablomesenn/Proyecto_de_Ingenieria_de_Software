import { apiGet } from "./http";

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
    const createdAt = u.created_at ? u.created_at.slice(0, 10) : "—";

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
