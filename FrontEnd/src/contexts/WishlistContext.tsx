import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import {
  getWishlist,
  addItemToWishlist,
  updateWishlistItem,
  removeWishlistItem,
  clearWishlist as clearWishlistAPI,
  mapWishlistItemToUI,
  type Wishlist,
} from "@/api/wishlist";
import { useAuth } from "./AuthContext";

interface WishlistItem {
  id: string;
  itemId: string;
  productId: string;
  variantId: string;
  name: string;
  category: string;
  image: string;
  variant: {
    id: string;
    size: string;
    price?: number;
    available: boolean;
    stock: number;
  };
  quantity: number;
  available: boolean;
  stock: number;
  addedAt: string;
  updatedAt?: string;
}

interface WishlistContextType {
  items: WishlistItem[];
  isLoading: boolean;
  error: string | null;
  addItem: (variantId: string, quantity?: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearWishlist: () => Promise<void>;
  refreshWishlist: () => Promise<void>;
  getTotalItems: () => number;
  getTotalUnits: () => number;
  getAvailableItems: () => WishlistItem[];
  getUnavailableItems: () => WishlistItem[];
}

const WishlistContext = createContext<WishlistContextType | undefined>(
  undefined,
);

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error("useWishlist must be used within a WishlistProvider");
  }
  return context;
};

interface WishlistProviderProps {
  children: ReactNode;
}

export const WishlistProvider = ({ children }: WishlistProviderProps) => {
  const { user } = useAuth();
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load wishlist when user logs in
  useEffect(() => {
    if (user && user.role === "customer") {
      refreshWishlist();
    } else {
      setItems([]);
    }
  }, [user]);

  const refreshWishlist = async () => {
    if (!user || user.role !== "customer") {
      setItems([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const wishlist = await getWishlist();

      // Map items to UI format
      const mappedItems = wishlist.items.map(mapWishlistItemToUI);
      setItems(mappedItems);
    } catch (err: any) {
      console.error("Error loading wishlist:", err);
      setError(err.message || "Error al cargar la lista de interés");
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const addItem = async (variantId: string, quantity: number = 1) => {
    if (!user || user.role !== "customer") {
      throw new Error("Solo clientes pueden agregar items a la wishlist");
    }

    try {
      await addItemToWishlist({ variant_id: variantId, quantity });
      await refreshWishlist();
    } catch (err: any) {
      console.error("Error adding item to wishlist:", err);
      throw new Error(err.message || "Error al agregar producto a la lista");
    }
  };

  const updateQuantity = async (itemId: string, quantity: number) => {
    if (!user || user.role !== "customer") {
      throw new Error("No autorizado");
    }

    try {
      await updateWishlistItem(itemId, { quantity });
      await refreshWishlist();
    } catch (err: any) {
      console.error("Error updating quantity:", err);
      throw new Error(err.message || "Error al actualizar cantidad");
    }
  };

  const removeItem = async (itemId: string) => {
    if (!user || user.role !== "customer") {
      throw new Error("No autorizado");
    }

    try {
      await removeWishlistItem(itemId);
      await refreshWishlist();
    } catch (err: any) {
      console.error("Error removing item:", err);
      throw new Error(err.message || "Error al eliminar producto");
    }
  };

  const clearWishlist = async () => {
    if (!user || user.role !== "customer") {
      throw new Error("No autorizado");
    }

    try {
      await clearWishlistAPI();
      setItems([]);
    } catch (err: any) {
      console.error("Error clearing wishlist:", err);
      throw new Error(err.message || "Error al limpiar la lista");
    }
  };

  const getTotalItems = () => {
    return items.reduce((sum, item) => sum + item.quantity, 0);
  };

  const getTotalUnits = () => {
    return items.length;
  };

  const getAvailableItems = () => {
    return items.filter(
      (item) => item.available && item.stock >= item.quantity,
    );
  };

  const getUnavailableItems = () => {
    return items.filter(
      (item) => !item.available || item.stock < item.quantity,
    );
  };

  const value: WishlistContextType = {
    items,
    isLoading,
    error,
    addItem,
    updateQuantity,
    removeItem,
    clearWishlist,
    refreshWishlist,
    getTotalItems,
    getTotalUnits,
    getAvailableItems,
    getUnavailableItems,
  };

  return (
    <WishlistContext.Provider value={value}>
      {children}
    </WishlistContext.Provider>
  );
};

export default WishlistContext;
