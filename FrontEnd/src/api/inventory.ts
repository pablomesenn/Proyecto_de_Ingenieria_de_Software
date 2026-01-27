import { apiGet } from "./http";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

// Types based on backend inventory service response
export interface VariantInventory {
  _id?: string;
  variant_id: string;
  stock_total: number;
  stock_disponible: number; // This is calculated as stock_total - stock_retenido
  stock_retenido: number;
  disponible: boolean;
  estado?: string;
  actualizado_en?: string;
  creado_en?: string;
  exists?: boolean;
}

// API functions
export async function getInventoryByVariant(
  variantId: string,
): Promise<VariantInventory> {
  const response = await apiGet<any>(`/api/inventory/variant/${variantId}`);

  // Map backend response to frontend format
  // Backend returns 'disponibilidad' but we expect 'stock_disponible'
  return {
    _id: response._id,
    variant_id: response.variant_id,
    stock_total: response.stock_total || 0,
    stock_disponible: response.disponibilidad || response.stock_disponible || 0,
    stock_retenido: response.stock_retenido || 0,
    disponible: (response.disponibilidad || response.stock_disponible || 0) > 0,
    estado: response.estado,
    actualizado_en: response.actualizado_en,
    creado_en: response.creado_en,
    exists: response.exists !== false,
  };
}


export type InventoryMovement = {
  _id: string;
  variant_id: string;
  movement_type: string;
  quantity: number;
  reason?: string;
  creado_en: string;

  stock_before?: number;
  stock_after?: number;

  retained_before?: number;
  retained_after?: number;

  product_name?: string;
  variant_name?: string;
  actor_name?: string;
};

// Helper to check if variant has available stock
export function hasAvailableStock(inventory: VariantInventory): boolean {
  return inventory.disponible && inventory.stock_disponible > 0;
}

// Helper to get stock status message
export function getStockStatusMessage(inventory: VariantInventory): string {
  if (!inventory.disponible || !inventory.exists) {
    return "No disponible";
  }

  if (inventory.stock_disponible === 0) {
    return "Agotado";
  }

  if (inventory.stock_disponible < 10) {
    return `Pocas unidades (${inventory.stock_disponible} disponibles)`;
  }

  return `Disponible (${inventory.stock_disponible} unidades)`;
}

// Helper to get stock status color
export function getStockStatusColor(inventory: VariantInventory): string {
  if (
    !inventory.disponible ||
    !inventory.exists ||
    inventory.stock_disponible === 0
  ) {
    return "text-destructive";
  }

  if (inventory.stock_disponible < 10) {
    return "text-yellow-600";
  }

  return "text-success";
}


export async function fetchInventoryMovements(params?: {
    skip?: number;
    limit?: number;
    movement_type?: string;
    variant_id?: string;
  }) {
    const qs = new URLSearchParams();
    if (params?.skip != null) qs.set("skip", String(params.skip));
    if (params?.limit != null) qs.set("limit", String(params.limit));
    if (params?.movement_type) qs.set("movement_type", params.movement_type);
    if (params?.variant_id) qs.set("variant_id", params.variant_id);

    return apiGet<{ movements: InventoryMovement[] }>(`/api/inventory/movements?${qs.toString()}`);
  }
