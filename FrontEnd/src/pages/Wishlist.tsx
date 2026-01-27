import { useState } from "react";
import { Link } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useWishlist } from "@/contexts/WishlistContext";
import WishlistItem from "@/components/wishlist/WishlistItem";
import CreateReservationDialog from "@/components/wishlist/CreateReservationDialog";
import {
  Heart,
  ShoppingBag,
  Trash2,
  ArrowRight,
  Package,
  AlertCircle,
  Loader2,
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
import { Alert, AlertDescription } from "@/components/ui/alert";

const Wishlist = () => {
  const {
    items,
    isLoading,
    error,
    clearWishlist,
    getTotalItems,
    getAvailableItems,
    getUnavailableItems,
  } = useWishlist();

  const [reservationDialogOpen, setReservationDialogOpen] = useState(false);

  const availableItems = getAvailableItems();
  const unavailableItems = getUnavailableItems();
  const totalUnits = getTotalItems();

  // Calculate total value
  const totalValue = items.reduce((sum, item) => {
    const price = item.variant.price || 0;
    return sum + price * item.quantity;
  }, 0);

  if (isLoading) {
    return (
      <MainLayout>
        <div className="container py-16 flex flex-col items-center justify-center min-h-[60vh]">
          <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
          <p className="text-muted-foreground">
            Cargando tu lista de interés...
          </p>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="container py-16">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-display font-bold flex items-center gap-3">
              <Heart className="h-8 w-8 text-primary fill-primary" />
              Mi Lista de Interés
            </h1>
            <p className="text-muted-foreground mt-1">
              {items.length === 0
                ? "Tu lista está vacía"
                : `${items.length} producto(s) · ${totalUnits} unidades`}
            </p>
          </div>

          {items.length > 0 && (
            <div className="flex gap-2">
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Vaciar lista
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>
                      ¿Vaciar lista de interés?
                    </AlertDialogTitle>
                    <AlertDialogDescription>
                      Esta acción eliminará todos los productos de tu lista.
                      Esta acción no se puede deshacer.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={clearWishlist}>
                      Sí, vaciar lista
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>

              <Button
                onClick={() => setReservationDialogOpen(true)}
                disabled={availableItems.length === 0}
              >
                <ShoppingBag className="h-4 w-4 mr-2" />
                Convertir a Reserva
              </Button>
            </div>
          )}
        </div>

        {/* Empty State */}
        {items.length === 0 ? (
          <Card className="py-16">
            <CardContent className="flex flex-col items-center text-center">
              <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
                <Heart className="h-10 w-10 text-muted-foreground" />
              </div>
              <h2 className="text-xl font-display font-semibold mb-2">
                Tu lista está vacía
              </h2>
              <p className="text-muted-foreground max-w-sm mb-6">
                Explora nuestro catálogo y agrega los productos que te interesen
                para crear una reserva más tarde.
              </p>
              <Button asChild>
                <Link to="/catalog">
                  Explorar Catálogo
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Wishlist Items */}
            <div className="lg:col-span-2 space-y-4">
              {/* Availability Alert */}
              {unavailableItems.length > 0 && (
                <Alert variant="warning">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {unavailableItems.length} producto(s) no tienen stock
                    suficiente o no están disponibles. Estos no podrán incluirse
                    en la reserva.
                  </AlertDescription>
                </Alert>
              )}

              {/* Items List */}
              {items.map((item) => (
                <WishlistItem key={item.itemId} item={item} />
              ))}
            </div>

            {/* Summary Sidebar */}
            <div className="lg:col-span-1">
              <Card className="sticky top-20">
                <CardContent className="p-6 space-y-6">
                  <h3 className="font-display font-semibold text-lg">
                    Resumen de la Lista
                  </h3>

                  {/* Stats */}
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        Productos en la lista
                      </span>
                      <span className="font-medium">{items.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        Unidades totales
                      </span>
                      <span className="font-medium">{totalUnits}</span>
                    </div>

                    <div className="h-px bg-border" />

                    <div className="flex justify-between text-sm">
                      <span className="text-success flex items-center gap-1">
                        <Package className="h-4 w-4" />
                        Disponibles
                      </span>
                      <span className="font-medium text-success">
                        {availableItems.length}
                      </span>
                    </div>

                    {unavailableItems.length > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-destructive flex items-center gap-1">
                          <AlertCircle className="h-4 w-4" />
                          No disponibles
                        </span>
                        <span className="font-medium text-destructive">
                          {unavailableItems.length}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Availability Note */}
                  {unavailableItems.length > 0 && (
                    <div className="p-3 rounded-lg bg-warning/10 border border-warning/20">
                      <p className="text-xs text-warning-foreground">
                        Algunos productos no están disponibles o no tienen stock
                        suficiente. Al crear una reserva, solo se incluirán los
                        productos disponibles.
                      </p>
                    </div>
                  )}

                  {/* CTA */}
                  <Button
                    className="w-full"
                    size="lg"
                    onClick={() => setReservationDialogOpen(true)}
                    disabled={availableItems.length === 0}
                  >
                    <ShoppingBag className="h-5 w-5 mr-2" />
                    Crear Reserva{" "}
                    {availableItems.length > 0 && `(${availableItems.length})`}
                  </Button>

                  <p className="text-xs text-muted-foreground text-center">
                    Las reservas requieren confirmación en 24 horas hábiles y
                    estarán activas por 7 días.
                  </p>

                  {/* Continue Shopping */}
                  <Button variant="outline" asChild className="w-full">
                    <Link to="/catalog">
                      <ArrowRight className="h-4 w-4 mr-2" />
                      Continuar Explorando
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Reservation Dialog */}
        <CreateReservationDialog
          open={reservationDialogOpen}
          onOpenChange={setReservationDialogOpen}
          items={items}
        />
      </div>
    </MainLayout>
  );
};

export default Wishlist;
