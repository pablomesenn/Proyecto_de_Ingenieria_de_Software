import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  CalendarClock,
  Check,
  AlertTriangle,
  ShoppingBag,
  Loader2,
} from "lucide-react";
import { WishlistItem, useWishlist } from "@/contexts/WishlistContext";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import * as wishlistApi from "@/api/wishlist";

interface CreateReservationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  items: WishlistItem[];
}

const CreateReservationDialog = ({
  open,
  onOpenChange,
  items,
}: CreateReservationDialogProps) => {
  const navigate = useNavigate();
  const { refreshWishlist } = useWishlist();
  const { toast } = useToast();
  const [selectedItems, setSelectedItems] = useState<string[]>(
    items.filter((item) => item.variant.available).map((item) => item.id),
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const availableItems = items.filter((item) => item.variant.available);
  const unavailableItems = items.filter((item) => !item.variant.available);

  const toggleItem = (id: string) => {
    setSelectedItems((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id],
    );
  };

  const toggleAll = () => {
    if (selectedItems.length === availableItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(availableItems.map((item) => item.id));
    }
  };

  const handleCreateReservation = async () => {
    if (selectedItems.length === 0) return;

    setIsSubmitting(true);

    try {
      // Prepare items for reservation
      const itemsToReserve = items
        .filter((item) => selectedItems.includes(item.id))
        .map((item) => ({
          item_id: item.id,
          quantity: item.quantity,
        }));

      // Call API to convert wishlist to reservation
      const response = await wishlistApi.convertWishlistToReservation({
        items: itemsToReserve,
      });

      toast({
        title: "¡Reserva creada exitosamente!",
        description:
          "Recibirás una confirmación en un plazo de 24 horas hábiles.",
      });

      // Refresh wishlist to reflect removed items
      await refreshWishlist();

      onOpenChange(false);
      navigate("/reservations");
    } catch (error) {
      console.error("Error creating reservation:", error);
      toast({
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : "No se pudo crear la reserva",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedItemsData = items.filter((item) =>
    selectedItems.includes(item.id),
  );
  const totalItems = selectedItemsData.reduce(
    (sum, item) => sum + item.quantity,
    0,
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingBag className="h-5 w-5 text-primary" />
            Crear Reserva
          </DialogTitle>
          <DialogDescription>
            Revisa los productos y confirma tu reserva. Recibirás confirmación
            en 24 horas hábiles.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {/* Select All */}
          {availableItems.length > 1 && (
            <div className="flex items-center gap-2 pb-3 mb-3 border-b">
              <Checkbox
                id="select-all"
                checked={selectedItems.length === availableItems.length}
                onCheckedChange={toggleAll}
              />
              <Label htmlFor="select-all" className="cursor-pointer text-sm">
                Seleccionar todos los disponibles ({availableItems.length})
              </Label>
            </div>
          )}

          <ScrollArea className="max-h-[300px] pr-4">
            <div className="space-y-3">
              {/* Available Items */}
              {availableItems.map((item) => (
                <div
                  key={item.id}
                  className={cn(
                    "flex items-center gap-3 p-3 rounded-lg border transition-colors",
                    selectedItems.includes(item.id)
                      ? "border-primary bg-primary/5"
                      : "border-border",
                  )}
                >
                  <Checkbox
                    id={item.id}
                    checked={selectedItems.includes(item.id)}
                    onCheckedChange={() => toggleItem(item.id)}
                  />
                  <img
                    src={item.image}
                    alt={item.name}
                    className="h-12 w-12 rounded object-cover"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{item.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.variant.size} × {item.quantity} unidades
                    </p>
                  </div>
                  <Badge variant="available" className="flex-shrink-0">
                    <Check className="h-3 w-3 mr-1" />
                    Disponible
                  </Badge>
                </div>
              ))}

              {/* Unavailable Items */}
              {unavailableItems.length > 0 && (
                <div className="pt-2">
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mb-2">
                    <AlertTriangle className="h-3 w-3" />
                    Productos no disponibles (no se incluirán en la reserva)
                  </p>
                  {unavailableItems.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 p-3 rounded-lg border border-border bg-muted/30 opacity-60"
                    >
                      <img
                        src={item.image}
                        alt={item.name}
                        className="h-12 w-12 rounded object-cover grayscale"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">
                          {item.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {item.variant.size} × {item.quantity} unidades
                        </p>
                      </div>
                      <Badge variant="unavailable" className="flex-shrink-0">
                        No disponible
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Summary */}
        <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
          <CalendarClock className="h-5 w-5 text-primary" />
          <div className="text-sm">
            <p className="font-medium">
              {selectedItems.length} producto(s) seleccionado(s) · {totalItems}{" "}
              unidades
            </p>
            <p className="text-muted-foreground">
              La reserva estará activa por 7 días tras aprobación
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleCreateReservation}
            disabled={selectedItems.length === 0 || isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Procesando...
              </>
            ) : (
              <>
                <ShoppingBag className="h-4 w-4 mr-2" />
                Confirmar Reserva
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateReservationDialog;
