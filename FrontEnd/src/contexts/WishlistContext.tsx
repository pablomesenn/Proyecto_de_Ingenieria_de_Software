import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useAuth } from "./AuthContext";
import * as wishlistApi from "@/api/wishlist";

export interface WishlistItemVariant {
  id: string;
  size: string;
  available: boolean;
  stock: number;
}

export interface WishlistItem {
  id: string;
  productId: string;
  variantId: string;
  name: string;
  category: string;
  image: string;
  variant: WishlistItemVariant;
  quantity: number;
  addedAt: string;
}

interface WishlistContextType {
  items: WishlistItem[];
  loading: boolean;
  error: string | null;
  addItem: (variantId: string, quantity?: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearWishlist: () => Promise<void>;
  getTotalItems: () => number;
  refreshWishlist: () => Promise<void>;
}

const WishlistContext = createContext<WishlistContextType | undefined>(
  undefined,
);

export function WishlistProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  // Load wishlist when user logs in
  useEffect(() => {
    if (user) {
      refreshWishlist();
    } else {
      // Clear wishlist when user logs out
      setItems([]);
      setError(null);
    }
  }, [user]);

  const refreshWishlist = async () => {
    if (!user) {
      setItems([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const wishlist = await wishlistApi.getWishlist();
      const mappedItems = wishlist.items.map(wishlistApi.mapWishlistItemToUI);
      setItems(mappedItems);
    } catch (err) {
      console.error("Error loading wishlist:", err);

      // Don't show error for 401 (user not logged in)
      if (
        err instanceof Error &&
        !err.message.includes("401") &&
        !err.message.includes("Token")
      ) {
        setError(err.message || "Error cargando lista de interés");
      }
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const addItem = async (variantId: string, quantity: number = 1) => {
    if (!user) {
      throw new Error("Debes iniciar sesión para agregar items a tu lista");
    }

    setLoading(true);
    setError(null);

    try {
      const response = await wishlistApi.addItemToWishlist({
        variant_id: variantId,
        quantity,
      });
      const mappedItems = response.wishlist.items.map(
        wishlistApi.mapWishlistItemToUI,
      );
      setItems(mappedItems);
    } catch (err) {
      console.error("Error adding item to wishlist:", err);
      setError(err instanceof Error ? err.message : "Error agregando item");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId: string, quantity: number) => {
    if (!user) return;

    if (quantity < 1) {
      await removeItem(itemId);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await wishlistApi.updateWishlistItem(itemId, {
        quantity,
      });
      const mappedItems = response.wishlist.items.map(
        wishlistApi.mapWishlistItemToUI,
      );
      setItems(mappedItems);
    } catch (err) {
      console.error("Error updating wishlist item:", err);
      setError(
        err instanceof Error ? err.message : "Error actualizando cantidad",
      );
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (itemId: string) => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const response = await wishlistApi.removeWishlistItem(itemId);
      const mappedItems = response.wishlist.items.map(
        wishlistApi.mapWishlistItemToUI,
      );
      setItems(mappedItems);
    } catch (err) {
      console.error("Error removing wishlist item:", err);
      setError(err instanceof Error ? err.message : "Error eliminando item");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearWishlist = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      await wishlistApi.clearWishlist();
      setItems([]);
    } catch (err) {
      console.error("Error clearing wishlist:", err);
      setError(err instanceof Error ? err.message : "Error limpiando lista");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getTotalItems = () => {
    return items.reduce((total, item) => total + item.quantity, 0);
  };

  return (
    <WishlistContext.Provider
      value={{
        items,
        loading,
        error,
        addItem,
        updateQuantity,
        removeItem,
        clearWishlist,
        getTotalItems,
        refreshWishlist,
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
}

export function useWishlist() {
  const context = useContext(WishlistContext);
  if (context === undefined) {
    throw new Error("useWishlist must be used within a WishlistProvider");
  }
  return context;
}
