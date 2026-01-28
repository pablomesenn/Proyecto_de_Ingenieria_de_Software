import { apiGet, apiPut, apiDelete } from "./http";

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  priority: string;
  read: boolean;
  read_at: string | null;
  created_at: string;
  action_url?: string;
  related_entity_id?: string;
  related_entity_type?: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
  total: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

const notificationService = {
  // Obtener notificaciones del usuario
  getNotifications: async (params?: {
    unread_only?: boolean;
    limit?: number;
    skip?: number;
  }): Promise<NotificationsResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.unread_only) queryParams.append("unread_only", "true");
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.skip) queryParams.append("skip", params.skip.toString());

    return await apiGet<NotificationsResponse>(
      `/notifications/?${queryParams.toString()}`
    );
  },

  // Obtener conteo de no leídas
  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    return await apiGet<UnreadCountResponse>("/notifications/unread-count");
  },

  // Marcar notificación como leída
  markAsRead: async (notificationId: string): Promise<void> => {
    await apiPut<void>(`/notifications/${notificationId}/read`);
  },

  // Marcar todas como leídas
  markAllAsRead: async (): Promise<{ marked_count: number }> => {
    return await apiPut<{ marked_count: number }>("/notifications/mark-all-read");
  },

  // Eliminar notificación
  deleteNotification: async (notificationId: string): Promise<void> => {
    await apiDelete<void>(`/notifications/${notificationId}`);
  },
};

export default notificationService;