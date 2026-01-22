import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Minus, Plus, Trash2 } from "lucide-react";
import { WishlistItem as WishlistItemType, useWishlist } from "@/contexts/WishlistContext";
import { cn } from "@/lib/utils";

interface WishlistItemProps {
  item: WishlistItemType;
}

const WishlistItem = ({ item }: WishlistItemProps) => {
  const { updateQuantity, removeItem } = useWishlist();

  const handleQuantityChange = (delta: number) => {
    updateQuantity(item.id, item.quantity + delta);
  };

  const maxQuantity = item.variant.available ? item.variant.stock : 0;

  return (
    <Card className="flex flex-col sm:flex-row gap-4 p-4 animate-fade-in">
      {/* Product Image */}
      <Link
        to={`/catalog/${item.productId}`}
        className="relative w-full sm:w-32 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-muted group"
      >
        <img
          src={item.image}
          alt={item.name}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </Link>

      {/* Product Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <Badge variant="category" className="mb-1">
              {item.category}
            </Badge>
            <Link
              to={`/catalog/${item.productId}`}
              className="block font-display font-semibold text-lg hover:text-primary transition-colors truncate"
            >
              {item.name}
            </Link>
            <p className="text-sm text-muted-foreground mt-1">
              Tamaño: {item.variant.size}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-destructive flex-shrink-0"
            onClick={() => removeItem(item.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>

        {/* Availability & Quantity */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 mt-4">
          {/* Availability Status */}
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "h-2 w-2 rounded-full",
                item.variant.available ? "bg-success" : "bg-destructive"
              )}
            />
            {item.variant.available ? (
              <span className="text-sm text-success">
                Disponible ({item.variant.stock} unidades)
              </span>
            ) : (
              <span className="text-sm text-destructive">No disponible</span>
            )}
          </div>

          {/* Quantity Controls */}
          {item.variant.available && (
            <div className="flex items-center gap-2 sm:ml-auto">
              <span className="text-sm text-muted-foreground">Cantidad:</span>
              <div className="flex items-center border rounded-md">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-r-none"
                  onClick={() => handleQuantityChange(-1)}
                  disabled={item.quantity <= 1}
                >
                  <Minus className="h-3 w-3" />
                </Button>
                <span className="w-10 text-center text-sm font-medium">
                  {item.quantity}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-l-none"
                  onClick={() => handleQuantityChange(1)}
                  disabled={item.quantity >= maxQuantity}
                >
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default WishlistItem;
