import { createContext, useContext, useState, ReactNode } from "react";

export interface WishlistVariant {
  id: string;
  size: string;
  available: boolean;
  stock: number;
}

export interface WishlistItem {
  id: string;
  productId: string;
  name: string;
  category: string;
  image: string;
  variant: WishlistVariant;
  quantity: number;
  addedAt: Date;
}

interface WishlistContextType {
  items: WishlistItem[];
  addItem: (item: Omit<WishlistItem, "id" | "addedAt">) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearWishlist: () => void;
  getTotalItems: () => number;
  isInWishlist: (productId: string, variantId: string) => boolean;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

// Mock initial items for demonstration
const mockItems: WishlistItem[] = [
  {
    id: "w1",
    productId: "1",
    name: "Porcelanato Terrazo Blanco",
    category: "Porcelanato",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
    variant: { id: "v1", size: "60x60 cm", available: true, stock: 150 },
    quantity: 10,
    addedAt: new Date(Date.now() - 86400000), // 1 day ago
  },
  {
    id: "w2",
    productId: "2",
    name: "Mármol Calacatta Gold",
    category: "Mármol",
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600&h=600&fit=crop",
    variant: { id: "v1", size: "60x120 cm", available: true, stock: 45 },
    quantity: 5,
    addedAt: new Date(Date.now() - 43200000), // 12 hours ago
  },
  {
    id: "w3",
    productId: "3",
    name: "Cerámica Rústica Terracota",
    category: "Cerámica",
    image: "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&h=600&fit=crop",
    variant: { id: "v1", size: "45x45 cm", available: false, stock: 0 },
    quantity: 8,
    addedAt: new Date(Date.now() - 172800000), // 2 days ago
  },
  {
    id: "w4",
    productId: "5",
    name: "Porcelanato Madera Natural",
    category: "Porcelanato",
    image: "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=600&h=600&fit=crop",
    variant: { id: "v2", size: "25x150 cm", available: true, stock: 80 },
    quantity: 15,
    addedAt: new Date(),
  },
];

export const WishlistProvider = ({ children }: { children: ReactNode }) => {
  const [items, setItems] = useState<WishlistItem[]>(mockItems);

  const addItem = (newItem: Omit<WishlistItem, "id" | "addedAt">) => {
    // Check if item with same product and variant exists
    const existingIndex = items.findIndex(
      (item) => item.productId === newItem.productId && item.variant.id === newItem.variant.id
    );

    if (existingIndex !== -1) {
      // Consolidate: add quantities
      setItems((prev) =>
        prev.map((item, index) =>
          index === existingIndex
            ? { ...item, quantity: Math.min(item.quantity + newItem.quantity, item.variant.stock) }
            : item
        )
      );
    } else {
      setItems((prev) => [
        ...prev,
        {
          ...newItem,
          id: `w${Date.now()}`,
          addedAt: new Date(),
        },
      ]);
    }
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const updateQuantity = (id: string, quantity: number) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id
          ? { ...item, quantity: Math.max(1, Math.min(quantity, item.variant.stock || 1)) }
          : item
      )
    );
  };

  const clearWishlist = () => {
    setItems([]);
  };

  const getTotalItems = () => {
    return items.reduce((total, item) => total + item.quantity, 0);
  };

  const isInWishlist = (productId: string, variantId: string) => {
    return items.some((item) => item.productId === productId && item.variant.id === variantId);
  };

  return (
    <WishlistContext.Provider
      value={{
        items,
        addItem,
        removeItem,
        updateQuantity,
        clearWishlist,
        getTotalItems,
        isInWishlist,
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (context === undefined) {
    throw new Error("useWishlist must be used within a WishlistProvider");
  }
  return context;
};
