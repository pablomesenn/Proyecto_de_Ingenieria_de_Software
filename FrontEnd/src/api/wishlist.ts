import { apiGet } from "./http";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

// Types based on backend schemas
export interface WishlistItemVariant {
  _id: string;
  size: string;
  available: boolean;
  stock: number;
}

export interface WishlistItemProduct {
  _id: string;
  name: string;
  category: string;
  image_url?: string;
}

export interface WishlistItem {
  _id: string;
  variant_id: string;
  quantity: number;
  variant: WishlistItemVariant;
  product: WishlistItemProduct;
  added_at: string;
}

export interface Wishlist {
  _id: string;
  user_id: string;
  items: WishlistItem[];
  created_at: string;
  updated_at: string;
}

export interface WishlistSummary {
  total_items: number;
  total_units: number;
  available_items: number;
  unavailable_items: number;
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
}

// Helper function for authenticated requests
async function apiRequest<T>(
  path: string,
  method: string = "GET",
  body?: any,
): Promise<T> {
  const token = getAccessToken();

  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_URL}${path}`, options);

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// API functions
export async function getWishlist(): Promise<Wishlist> {
  return apiRequest<Wishlist>("/api/wishlist/");
}

export async function getWishlistSummary(): Promise<WishlistSummary> {
  return apiRequest<WishlistSummary>("/api/wishlist/summary");
}

export async function addItemToWishlist(
  data: AddWishlistItemRequest,
): Promise<{ message: string; wishlist: Wishlist }> {
  return apiRequest("/api/wishlist/items", "POST", data);
}

export async function updateWishlistItem(
  itemId: string,
  data: UpdateWishlistItemRequest,
): Promise<{ message: string; wishlist: Wishlist }> {
  return apiRequest(`/api/wishlist/items/${itemId}`, "PUT", data);
}

export async function removeWishlistItem(
  itemId: string,
): Promise<{ message: string; wishlist: Wishlist }> {
  return apiRequest(`/api/wishlist/items/${itemId}`, "DELETE");
}

export async function clearWishlist(): Promise<{ message: string }> {
  return apiRequest("/api/wishlist/clear", "DELETE");
}

export async function convertWishlistToReservation(
  data: ConvertToReservationRequest,
): Promise<{ message: string; reservation: any }> {
  return apiRequest("/api/wishlist/convert-to-reservation", "POST", data);
}

// Helper function to map backend wishlist item to UI format
export function mapWishlistItemToUI(item: WishlistItem) {
  return {
    id: item._id,
    productId: item.product._id,
    variantId: item.variant_id,
    name: item.product.name,
    category: item.product.category,
    image:
      item.product.image_url ||
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
    variant: {
      id: item.variant._id,
      size: item.variant.size,
      available: item.variant.available,
      stock: item.variant.stock,
    },
    quantity: item.quantity,
    addedAt: item.added_at,
  };
}
