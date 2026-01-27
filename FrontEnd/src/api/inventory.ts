import { apiGet, apiPost } from "./http";

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

// Get all inventory for admin
export async function getAllInventory(skip: number = 0, limit: number = 20): Promise<any> {
  return apiGet<any>(`/api/inventory/?skip=${skip}&limit=${limit}`);
}

// Adjust inventory (add or subtract)
export async function adjustInventory(
  variantId: string,
  delta: number,
  reason: string,
): Promise<any> {
  return apiPost<any>(`/api/inventory/variant/${variantId}/adjust`, {
    delta,
    reason,
  });
}

// Retain stock
export async function retainStock(
  variantId: string,
  quantity: number,
  reason?: string,
): Promise<any> {
  return apiPost<any>(`/api/inventory/variant/${variantId}/retain`, {
    quantity,
    reason,
  });
}

// Release stock
export async function releaseStock(
  variantId: string,
  quantity: number,
  reason?: string,
): Promise<any> {
  return apiPost<any>(`/api/inventory/variant/${variantId}/release`, {
    quantity,
    reason,
  });
}
