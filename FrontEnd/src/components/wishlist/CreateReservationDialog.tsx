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
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import {
  convertWishlistToReservation,
  validateWishlistForReservation,
  WishlistItem,
} from "@/api/wishlist";
import {
  Package,
  AlertCircle,
  CheckCircle,
  ShoppingBag,
  Calendar,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface CreateReservationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  items: Array<{
    id: string;
    itemId: string;
    name: string;
    category: string;
    image: string;
    variant: {
      size: string;
      price?: number;
      available: boolean;
      stock: number;
    };
    quantity: number;
    available: boolean;
    stock: number;
  }>;
}

const CreateReservationDialog = ({
  open,
  onOpenChange,
  items,
}: CreateReservationDialogProps) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Filter available items
  const availableItems = items.filter((item) => {
    const hasStock = item.stock >= item.quantity;
    return item.available && hasStock;
  });

  const unavailableItems = items.filter((item) => {
    const hasStock = item.stock >= item.quantity;
    return !item.available || !hasStock;
  });

  // Initialize selected items when dialog opens
  const handleOpenChange = (newOpen: boolean) => {
    if (newOpen) {
      // Auto-select all available items
      setSelectedItems(new Set(availableItems.map((item) => item.itemId)));
      setNotes("");
    }
    onOpenChange(newOpen);
  };

  const handleToggleItem = (itemId: string) => {
    setSelectedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const handleToggleAll = () => {
    if (selectedItems.size === availableItems.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(availableItems.map((item) => item.itemId)));
    }
  };

  const handleSubmit = async () => {
    if (selectedItems.size === 0) {
      toast({
        title: "Selecciona productos",
        description:
          "Debes seleccionar al menos un producto para crear la reserva",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare items for reservation
      const itemsToReserve = availableItems
        .filter((item) => selectedItems.has(item.itemId))
        .map((item) => ({
          item_id: item.itemId,
          quantity: item.quantity,
        }));

      // Validate before submitting
      const validation = validateWishlistForReservation(
        items.filter((item) => selectedItems.has(item.itemId)) as unknown as WishlistItem[],
      );

      if (!validation.valid) {
        toast({
          title: "Validación fallida",
          description: validation.errors.join(", "),
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }

      // Create reservation
      const response = await convertWishlistToReservation({
        items: itemsToReserve,
        notes: notes.trim() || undefined,
      });

      toast({
        title: "¡Reserva creada!",
        description: `Se ha creado tu reserva con ${selectedItems.size} producto(s)`,
      });

      // Close dialog and navigate
      onOpenChange(false);
      navigate("/reservations");
    } catch (error: any) {
      console.error("Error creating reservation:", error);

      let errorMessage = "No se pudo crear la reserva";
      if (error.message) {
        try {
          const parsed = JSON.parse(error.message);
          errorMessage = parsed.error || errorMessage;
        } catch {
          errorMessage = error.message;
        }
      }

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate totals
  const selectedItemsList = availableItems.filter((item) =>
    selectedItems.has(item.itemId),
  );
  const totalItems = selectedItemsList.length;
  const totalUnits = selectedItemsList.reduce(
    (sum, item) => sum + item.quantity,
    0,
  );
  const totalValue = selectedItemsList.reduce(
    (sum, item) => sum + (item.variant.price || 0) * item.quantity,
    0,
  );

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingBag className="h-5 w-5 text-primary" />
            Crear Reserva desde Lista de Interés
          </DialogTitle>
          <DialogDescription>
            Selecciona los productos que deseas reservar. Solo se muestran
            productos con stock disponible.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden flex flex-col gap-4">
          {/* Info Alerts */}
          {unavailableItems.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {unavailableItems.length} producto(s) no se pueden reservar por
                falta de stock o disponibilidad
              </AlertDescription>
            </Alert>
          )}

          <Alert variant="default">
            <Calendar className="h-4 w-4" />
            <AlertDescription className="text-xs">
              Las reservas tienen una validez de 7 días y requieren confirmación
              en 24 horas hábiles
            </AlertDescription>
          </Alert>

          {/* Available Items List */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label className="text-sm font-medium">
                Productos disponibles ({availableItems.length})
              </Label>
              {availableItems.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleToggleAll}
                  className="h-8 text-xs"
                >
                  {selectedItems.size === availableItems.length
                    ? "Deseleccionar todos"
                    : "Seleccionar todos"}
                </Button>
              )}
            </div>

            <ScrollArea className="h-[300px] border rounded-lg">
              <div className="p-4 space-y-3">
                {availableItems.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No hay productos disponibles para reservar</p>
                  </div>
                ) : (
                  availableItems.map((item) => (
                    <div
                      key={item.itemId}
                      className="flex items-start gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                    >
                      <Checkbox
                        checked={selectedItems.has(item.itemId)}
                        onCheckedChange={() => handleToggleItem(item.itemId)}
                        className="mt-1"
                      />

                      <div className="flex-shrink-0">
                        <img
                          src={item.image}
                          alt={item.name}
                          className="h-16 w-16 object-cover rounded"
                        />
                      </div>

                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-sm truncate">
                          {item.name}
                        </h4>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {item.variant.size}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {item.category}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 mt-2">
                          <div className="flex items-center gap-1 text-xs text-success">
                            <CheckCircle className="h-3 w-3" />
                            <span>{item.stock} disponibles</span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Cantidad:{" "}
                            <span className="font-medium">{item.quantity}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes" className="text-sm font-medium">
              Notas (opcional)
            </Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Agrega cualquier información adicional para tu reserva..."
              className="mt-2 resize-none"
              rows={3}
              maxLength={500}
            />
            <p className="text-xs text-muted-foreground mt-1">
              {notes.length}/500 caracteres
            </p>
          </div>

          {/* Summary */}
          {selectedItems.size > 0 && (
            <div className="p-4 rounded-lg bg-muted space-y-2">
              <h4 className="font-semibold text-sm">Resumen de la Reserva</h4>
              <Separator />
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Productos seleccionados:
                  </span>
                  <span className="font-medium">{totalItems}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Unidades totales:
                  </span>
                  <span className="font-medium">{totalUnits}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={selectedItems.size === 0 || isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Creando...
              </>
            ) : (
              <>
                <ShoppingBag className="h-4 w-4 mr-2" />
                Crear Reserva ({selectedItems.size})
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateReservationDialog;
