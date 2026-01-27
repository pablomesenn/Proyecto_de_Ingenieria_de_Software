import { apiGet, apiPut, apiPost, apiDownload } from "./http";

// Tipos
export type ReservationState = "Pendiente" | "Aprobada" | "Rechazada" | "Cancelada" | "Expirada";

export interface ReservationItem {
  variant_id: string;
  product_name: string;
  variant_name: string;
  quantity: number;
  reserved_at?: string;
}

export interface Reservation {
  _id: string;
  user_id: string;
  items: ReservationItem[];
  state: ReservationState;
  notes?: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

export interface ReservationResponse {
  reservation: Reservation;
  message: string;
}

// Obtener todas las reservas (ADMIN)
export async function getAllReservations(): Promise<{ reservations: Reservation[]; count: number }> {
  return apiGet<{ reservations: Reservation[]; count: number }>("/api/reservations/");
}

// Obtener reservas del usuario autenticado
export async function getMyReservations(): Promise<{ reservations: Reservation[]; count: number }> {
  return apiGet<{ reservations: Reservation[]; count: number }>("/api/reservations/my");
}

// Obtener detalle de una reserva
export async function getReservationById(id: string): Promise<Reservation> {
  // El backend devuelve la reserva directamente, no envuelta en { reservation: ... }
  return apiGet<Reservation>(`/api/reservations/${id}`);
}

// Crear nueva reserva
export async function createReservation(data: {
  items: { variant_id: string; quantity: number }[];
  notes?: string;
}): Promise<ReservationResponse> {
  return apiPost<ReservationResponse>("/api/reservations/", data);
}

// Aprobar reserva (ADMIN)
export async function approveReservation(id: string, adminNotes?: string): Promise<ReservationResponse> {
  return apiPut<ReservationResponse>(`/api/reservations/${id}/approve`, {
    admin_notes: adminNotes,
  });
}

// Rechazar reserva (ADMIN)
export async function rejectReservation(id: string, adminNotes: string): Promise<ReservationResponse> {
  return apiPut<ReservationResponse>(`/api/reservations/${id}/reject`, {
    admin_notes: adminNotes,
  });
}

// Cancelar reserva
export async function cancelReservation(id: string): Promise<ReservationResponse> {
  return apiPut<ReservationResponse>(`/api/reservations/${id}/cancel`);
}

export type ExportReservationsParams = {
  format: "csv" | "xlsx";
  state?: string;
  date_from?: string; // YYYY-MM-DD
  date_to?: string;   // YYYY-MM-DD
};

export async function exportReservations(params: ExportReservationsParams) {
  const qs = new URLSearchParams();
  qs.set("format", params.format);

  if (params.state) qs.set("state", params.state);
  if (params.date_from) qs.set("date_from", params.date_from);
  if (params.date_to) qs.set("date_to", params.date_to);

  const { blob, filename } = await apiDownload(`/api/reservations/export?${qs.toString()}`);

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || `reservas.${params.format}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}