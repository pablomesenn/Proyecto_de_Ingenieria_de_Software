import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  CalendarClock,
  ArrowRight,
  Loader2,
  AlertCircle,
  Package,
  Clock,
  CheckCircle,
  XCircle,
  Ban,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  getMyReservations,
  type Reservation,
  type ReservationState,
} from "@/api/reservations";
import { format } from "date-fns";
import { es } from "date-fns/locale";

const Reservations = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadReservations();
  }, []);

  const loadReservations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getMyReservations();
      setReservations(data.reservations);
    } catch (err: any) {
      console.error("Error loading reservations:", err);
      setError("No se pudieron cargar las reservas. Intenta nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const getStateConfig = (state: ReservationState) => {
    const configs = {
      Pendiente: {
        label: "Pendiente",
        variant: "secondary" as const,
        icon: Clock,
        color: "text-yellow-600",
        bgColor: "bg-yellow-50 dark:bg-yellow-950",
      },
      Aprobada: {
        label: "Aprobada",
        variant: "success" as const,
        icon: CheckCircle,
        color: "text-success",
        bgColor: "bg-success/10",
      },
      Rechazada: {
        label: "Rechazada",
        variant: "destructive" as const,
        icon: XCircle,
        color: "text-destructive",
        bgColor: "bg-destructive/10",
      },
      Cancelada: {
        label: "Cancelada",
        variant: "outline" as const,
        icon: Ban,
        color: "text-muted-foreground",
        bgColor: "bg-muted",
      },
      Expirada: {
        label: "Expirada",
        variant: "outline" as const,
        icon: AlertCircle,
        color: "text-muted-foreground",
        bgColor: "bg-muted",
      },
    };

    return configs[state] || configs.Pendiente;
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "d 'de' MMMM, yyyy 'a las' HH:mm", {
        locale: es,
      });
    } catch {
      return dateString;
    }
  };

  const formatShortDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "d MMM yyyy", { locale: es });
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <MainLayout>
        <div className="container py-16 flex flex-col items-center justify-center min-h-[60vh]">
          <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
          <p className="text-muted-foreground">Cargando tus reservas...</p>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="container py-8">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-display font-bold flex items-center gap-3">
              <CalendarClock className="h-8 w-8 text-primary" />
              Mis Reservas
            </h1>
          </div>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button variant="outline" size="sm" onClick={loadReservations}>
                Reintentar
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-display font-bold flex items-center gap-3">
            <CalendarClock className="h-8 w-8 text-primary" />
            Mis Reservas
          </h1>
          <p className="text-muted-foreground mt-1">
            {reservations.length === 0
              ? "No tienes reservas"
              : `${reservations.length} reserva(s) en total`}
          </p>
        </div>

        {reservations.length === 0 ? (
          <Card className="py-16">
            <CardContent className="flex flex-col items-center text-center">
              <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
                <CalendarClock className="h-10 w-10 text-muted-foreground" />
              </div>
              <h2 className="text-xl font-display font-semibold mb-2">
                No tienes reservas activas
              </h2>
              <p className="text-muted-foreground max-w-sm mb-6">
                Explora nuestro catálogo y crea tu primera reserva desde tu
                lista de interés.
              </p>
              <div className="flex gap-3">
                <Button variant="outline" asChild>
                  <Link to="/wishlist">Ver mi lista de interés</Link>
                </Button>
                <Button asChild>
                  <Link to="/catalog">
                    Explorar Catálogo
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {reservations.map((reservation) => {
              const stateConfig = getStateConfig(reservation.state);
              const StateIcon = stateConfig.icon;
              const totalItems = reservation.items.length;
              const totalQuantity = reservation.items.reduce(
                (sum, item) => sum + item.quantity,
                0,
              );

              return (
                <Card key={reservation._id} className="overflow-hidden">
                  <CardContent className="p-0">
                    {/* Header */}
                    <div className={`p-4 ${stateConfig.bgColor}`}>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <StateIcon
                            className={`h-5 w-5 ${stateConfig.color}`}
                          />
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="font-semibold">
                                Reserva #{reservation._id.slice(-8)}
                              </h3>
                              <Badge variant={stateConfig.variant}>
                                {stateConfig.label}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              Creada el {formatDate(reservation.created_at)}
                            </p>
                          </div>
                        </div>

                        {reservation.expires_at && (
                          <div className="text-sm">
                            <span className="text-muted-foreground">
                              Expira:{" "}
                            </span>
                            <span className="font-medium">
                              {formatShortDate(reservation.expires_at)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <Separator />

                    {/* Content */}
                    <div className="p-4 space-y-4">
                      {/* Items Summary */}
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Package className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">
                            {totalItems} producto(s)
                          </span>
                        </div>
                        <div className="text-muted-foreground">
                          {totalQuantity} unidades totales
                        </div>
                      </div>

                      {/* Items List */}
                      <div className="space-y-2">
                        {reservation.items.map((item, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                          >
                            <div className="flex-1 min-w-0">
                              <p className="font-medium truncate">
                                {item.product_name}
                              </p>
                              <p className="text-sm text-muted-foreground">
                                {item.variant_name}
                              </p>
                            </div>
                            <div className="flex items-center gap-2 text-sm font-medium">
                              <span className="text-muted-foreground">×</span>
                              <span>{item.quantity}</span>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Notes */}
                      {reservation.notes && (
                        <div className="p-3 rounded-lg bg-muted/30 border border-border">
                          <p className="text-sm font-medium mb-1">Tus notas:</p>
                          <p className="text-sm text-muted-foreground">
                            {reservation.notes}
                          </p>
                        </div>
                      )}

                      {/* Admin Notes */}
                      {reservation.admin_notes && (
                        <div className="p-3 rounded-lg bg-primary/5 border border-primary/20">
                          <p className="text-sm font-medium mb-1 text-primary">
                            Notas del administrador:
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {reservation.admin_notes}
                          </p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex justify-end pt-2">
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/reservations/${reservation._id}`}>
                            Ver detalles
                            <ArrowRight className="h-4 w-4 ml-2" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Reservations;
