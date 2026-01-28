import { apiGet } from "./http";

export interface DashboardStats {
  pending_reservations: {
    value: number;
    change: string;
  };
  active_products: {
    value: number;
    low_stock: number;
  };
  total_users: {
    value: number;
    new_this_month: number;
  };
  alerts: {
    value: number;
  };
}

export interface PendingReservation {
  _id: string;
  customer_name: string;
  items_count: number;
  total_units: number;
  created_at: string;
  expires_in: string | null;
}

export interface ExpiringReservation {
  _id: string;
  customer_name: string;
  expires_in: string;
}

export interface LowStockProduct {
  _id: string;
  name: string;
  variant_name: string;
  stock: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const data = await apiGet<{ stats: DashboardStats }>("/api/dashboard/stats");
  return data.stats;
}

export async function getPendingReservations(): Promise<PendingReservation[]> {
  const data = await apiGet<{ reservations: PendingReservation[] }>(
    "/api/dashboard/pending-reservations"
  );
  return data.reservations;
}

export async function getExpiringReservations(): Promise<ExpiringReservation[]> {
  const data = await apiGet<{ reservations: ExpiringReservation[] }>(
    "/api/dashboard/expiring-reservations"
  );
  return data.reservations;
}

export async function getLowStockProducts(): Promise<LowStockProduct[]> {
  const data = await apiGet<{ products: LowStockProduct[] }>(
    "/api/dashboard/low-stock-products"
  );
  return data.products;
}