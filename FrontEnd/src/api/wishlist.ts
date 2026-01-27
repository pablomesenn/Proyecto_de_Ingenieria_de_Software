import { apiGet, apiPost, apiPut, apiDelete } from "./http";

// Types based on backend schemas
export interface WishlistItemVariant {
  _id: string;
  size: string;
  tamano_pieza?: string;
  unidad?: string;
  price?: number;
  precio?: number;
  available: boolean;
  stock: number;
  product_id: string;
}

export interface WishlistItemProduct {
  _id: string;
  name?: string;
  nombre?: string;
  category?: string;
  categoria?: string;
  image_url?: string;
  imagen_url?: string;
  estado?: string;
  tags?: string[];
}

export interface WishlistItemInventory {
  stock_total: number;
  stock_retenido: number;
  disponibilidad: number;
  stock_disponible: number;
}

export interface WishlistItem {
  _id: string;
  item_id: string;
  variant_id: string;
  quantity: number;
  variant: WishlistItemVariant;
  product: WishlistItemProduct;
  inventory: WishlistItemInventory;
  available: boolean;
  stock: number;
  added_at: string;
  updated_at?: string;
}

export interface Wishlist {
  user_id: string;
  items: WishlistItem[];
  total_items: number;
}

export interface WishlistSummary {
  user_id: string;
  total_items: number;
  total_quantity: number;
  total_value: number;
  items_with_stock: number;
  items_out_of_stock: number;
}

export interface AddWishlistItemRequest {
  variant_id: string;
  quantity?: number;
}

export interface UpdateWishlistItemRequest {
  quantity: number;
}

export interface ConvertToReservationRequest {
  items: Array<{
    item_id: string;
    quantity: number;
  }>;
  notes?: string;
}

// API functions
export async function getWishlist(): Promise<Wishlist> {
  return apiGet<Wishlist>("/api/wishlist/");
}

export async function getWishlistSummary(): Promise<WishlistSummary> {
  return apiGet<WishlistSummary>("/api/wishlist/summary");
}

export async function addItemToWishlist(
  data: AddWishlistItemRequest,
): Promise<{ message: string; wishlist: Wishlist }> {
  return apiPost("/api/wishlist/items", data);
}

export async function updateWishlistItem(
  itemId: string,
  data: UpdateWishlistItemRequest,
): Promise<{ message: string; wishlist: Wishlist }> {
  return apiPut(`/api/wishlist/items/${itemId}`, data);
}

export async function removeWishlistItem(
  itemId: string,
): Promise<{ message: string; wishlist: Wishlist }> {
  return apiDelete(`/api/wishlist/items/${itemId}`);
}

export async function clearWishlist(): Promise<{ message: string }> {
  return apiDelete("/api/wishlist/clear");
}

export async function convertWishlistToReservation(
  data: ConvertToReservationRequest,
): Promise<{ message: string; reservation: any }> {
  return apiPost("/api/wishlist/convert-to-reservation", data);
}

// Helper function to map backend wishlist item to UI format
export function mapWishlistItemToUI(item: WishlistItem) {
  // Handle both Spanish and English field names
  const productName =
    item.product.name || item.product.nombre || "Producto sin nombre";
  const productCategory =
    item.product.category || item.product.categoria || "Sin categoría";
  const productImage =
    item.product.image_url ||
    item.product.imagen_url ||
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop";

  const variantSize = item.variant.size || item.variant.tamano_pieza || "";
  const variantPrice = item.variant.price || item.variant.precio || 0;

  // Use the stock and availability from root level (which comes from inventory calculation)
  const available = item.available;
  const stock = item.stock;

  return {
    id: item.item_id || item._id,
    itemId: item.item_id,
    productId: item.product._id,
    variantId: item.variant_id,
    name: productName,
    category: productCategory,
    image: productImage,
    variant: {
      id: item.variant._id,
      size: variantSize,
      price: variantPrice,
      available: available,
      stock: stock,
    },
    quantity: item.quantity,
    available: available,
    stock: stock,
    addedAt: item.added_at,
    updatedAt: item.updated_at,
  };
}

// Helper to check if item has sufficient stock for requested quantity
export function hasSufficientStock(item: WishlistItem): boolean {
  const available = item.stock || 0;
  return available >= item.quantity;
}

// Helper to get max available quantity for an item
export function getMaxAvailableQuantity(item: WishlistItem): number {
  return item.stock || 0;
}

// Helper to get stock status message
export function getStockStatusMessage(item: WishlistItem): string {
  const stock = item.stock || 0;

  if (!item.available || stock === 0) {
    return "Sin stock";
  }

  if (stock < item.quantity) {
    return `Solo ${stock} disponibles (necesitas ${item.quantity})`;
  }

  if (stock < 10) {
    return `Pocas unidades (${stock} disponibles)`;
  }

  return `Disponible (${stock} unidades)`;
}

// Helper to validate wishlist before conversion to reservation
export function validateWishlistForReservation(items: any[]): {
  valid: boolean;
  errors: string[];
  validItems: any[];
} {
  const errors: string[] = [];
  const validItems: any[] = [];

  for (const item of items) {
    // Handle both raw backend format and mapped UI format
    const productName =
      item.product?.name ||
      item.product?.nombre ||
      item.name || // mapped format
      "Producto";

    const variantSize =
      item.variant?.size ||
      item.variant?.tamano_pieza ||
      item.variant?.size || // mapped format
      "";

    const isAvailable =
      item.available !== undefined ? item.available : item.variant?.available;

    const stock =
      item.stock !== undefined ? item.stock : item.variant?.stock || 0;

    if (!isAvailable) {
      errors.push(`${productName} (${variantSize}) no está disponible`);
      continue;
    }

    if (stock < item.quantity) {
      errors.push(
        `${productName} (${variantSize}): stock insuficiente. Disponible: ${stock}, solicitado: ${item.quantity}`,
      );
      continue;
    }

    validItems.push(item);
  }

  return {
    valid: errors.length === 0,
    errors,
    validItems,
  };
}
