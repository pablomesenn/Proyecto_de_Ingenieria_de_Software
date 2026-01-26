import { apiGet, apiPut, apiPost } from "./http";

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