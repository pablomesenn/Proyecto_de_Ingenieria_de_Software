import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useWishlist } from "@/contexts/WishlistContext";
import {
  Trash2,
  Plus,
  Minus,
  Package,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";

interface WishlistItemProps {
  item: {
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
  };
}

const WishlistItem = ({ item }: WishlistItemProps) => {
  const { updateQuantity, removeItem } = useWishlist();
  const { toast } = useToast();
  const [quantity, setQuantity] = useState(item.quantity);
  const [isUpdating, setIsUpdating] = useState(false);

  const maxStock = item.stock || 0;
  const isAvailable = item.available && maxStock > 0;
  const hasSufficientStock = isAvailable && maxStock >= quantity;

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity < 1) return;
    if (newQuantity > maxStock) {
      toast({
        title: "Stock insuficiente",
        description: `Solo hay ${maxStock} unidades disponibles`,
        variant: "destructive",
      });
      return;
    }

    setQuantity(newQuantity);
    setIsUpdating(true);

    try {
      await updateQuantity(item.itemId, newQuantity);
      toast({
        title: "Cantidad actualizada",
        description: `Ahora tienes ${newQuantity} unidad(es) en tu lista`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo actualizar la cantidad",
        variant: "destructive",
      });
      setQuantity(item.quantity); // Revert on error
    } finally {
      setIsUpdating(false);
    }
  };

  const handleIncrement = () => {
    handleQuantityChange(quantity + 1);
  };

  const handleDecrement = () => {
    if (quantity > 1) {
      handleQuantityChange(quantity - 1);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value >= 1) {
      setQuantity(value);
    }
  };

  const handleInputBlur = () => {
    if (quantity !== item.quantity) {
      handleQuantityChange(quantity);
    }
  };

  const handleRemove = async () => {
    try {
      await removeItem(item.itemId);
      toast({
        title: "Producto eliminado",
        description: "El producto ha sido removido de tu lista",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo eliminar el producto",
        variant: "destructive",
      });
    }
  };

  // Calculate prices
  const unitPrice = item.variant.price || 0;
  const totalPrice = unitPrice * quantity;

  // Get stock status
  const getStockStatus = () => {
    if (!isAvailable) {
      return {
        text: "Sin stock",
        color: "text-destructive",
        icon: AlertCircle,
        badge: "destructive" as const,
      };
    }

    if (!hasSufficientStock) {
      return {
        text: `Solo ${maxStock} disponibles`,
        color: "text-warning",
        icon: AlertCircle,
        badge: "warning" as const,
      };
    }

    if (maxStock < 10) {
      return {
        text: `Pocas unidades (${maxStock})`,
        color: "text-yellow-600",
        icon: Package,
        badge: "secondary" as const,
      };
    }

    return {
      text: `${maxStock} disponibles`,
      color: "text-success",
      icon: CheckCircle,
      badge: "success" as const,
    };
  };

  const stockStatus = getStockStatus();
  const StatusIcon = stockStatus.icon;

  return (
    <Card className={!isAvailable ? "opacity-60" : ""}>
      <CardContent className="p-4">
        <div className="flex gap-4">
          {/* Product Image */}
          <Link
            to={`/product/${item.productId}`}
            className="flex-shrink-0 group"
          >
            <div className="relative h-24 w-24 rounded-lg overflow-hidden bg-muted">
              <img
                src={item.image}
                alt={item.name}
                className="h-full w-full object-cover group-hover:scale-105 transition-transform"
              />
              {!isAvailable && (
                <div className="absolute inset-0 bg-background/80 flex items-center justify-center">
                  <AlertCircle className="h-8 w-8 text-destructive" />
                </div>
              )}
            </div>
          </Link>

          {/* Product Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex-1 min-w-0">
                <Link
                  to={`/product/${item.productId}`}
                  className="hover:underline"
                >
                  <h3 className="font-semibold truncate">{item.name}</h3>
                </Link>
                <p className="text-sm text-muted-foreground">{item.category}</p>
              </div>

              {/* Remove Button */}
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="flex-shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>¿Eliminar producto?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Se eliminará "{item.name}" de tu lista de interés.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={handleRemove}>
                      Eliminar
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>

            {/* Variant Info */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <Badge variant="outline" className="font-mono">
                {item.variant.size}
              </Badge>

              <div className="flex items-center gap-1">
                <StatusIcon className={`h-4 w-4 ${stockStatus.color}`} />
                <span className={`text-sm font-medium ${stockStatus.color}`}>
                  {stockStatus.text}
                </span>
              </div>
            </div>

            {/* Quantity Controls and Price */}
            <div className="flex flex-wrap items-center gap-4">
              {/* Quantity Controls */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Cantidad:</span>
                <div className="flex items-center border rounded-md">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleDecrement}
                    disabled={quantity <= 1 || isUpdating || !isAvailable}
                  >
                    <Minus className="h-3 w-3" />
                  </Button>

                  <Input
                    type="number"
                    min="1"
                    max={maxStock}
                    value={quantity}
                    onChange={handleInputChange}
                    onBlur={handleInputBlur}
                    disabled={isUpdating || !isAvailable}
                    className="h-8 w-16 text-center border-0 focus-visible:ring-0 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  />

                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleIncrement}
                    disabled={
                      quantity >= maxStock || isUpdating || !isAvailable
                    }
                  >
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Warning Messages */}
            {!hasSufficientStock && isAvailable && (
              <div className="mt-3 p-2 rounded-md bg-warning/10 border border-warning/20">
                <p className="text-xs text-warning-foreground">
                  Solo hay {maxStock} unidad(es) disponible(s). Ajusta la
                  cantidad para poder crear una reserva.
                </p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default WishlistItem;
