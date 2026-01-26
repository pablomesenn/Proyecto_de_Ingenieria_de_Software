import { useParams, Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Textarea } from "@/components/ui/textarea";
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  Ban,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import {
  getReservationById,
  approveReservation,
  rejectReservation,
  cancelReservation,
  type Reservation,
} from "@/api/reservations";
import { getUserById } from "@/api/users";

const statusConfig = {
  Pendiente: { label: "Pendiente", variant: "pending" as const, icon: Clock },
  Aprobada: { label: "Aprobada", variant: "success" as const, icon: CheckCircle2 },
  Rechazada: { label: "Rechazada", variant: "destructive" as const, icon: XCircle },
  Cancelada: { label: "Cancelada", variant: "secondary" as const, icon: Ban },
  Expirada: { label: "Expirada", variant: "secondary" as const, icon: Clock },
};

const ReservationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [reservation, setReservation] = useState<Reservation | null>(null);
  const [customerInfo, setCustomerInfo] = useState<{ name: string; email: string; phone: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [actionDialog, setActionDialog] = useState<{
    open: boolean;
    type: "approve" | "reject" | "cancel" | null;
  }>({ open: false, type: null });
  const [adminNotes, setAdminNotes] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // Cargar reserva
  const loadReservation = async () => {
    if (!id) return;
    
    try {
      setIsLoading(true);
      const data = await getReservationById(id);
      setReservation(data);
      
      // Cargar información del cliente
      try {
        const user = await getUserById(data.user_id);
        setCustomerInfo({
          name: user.name || user.email,
          email: user.email,
          phone: user.phone || "No proporcionado"
        });
      } catch (error) {
        console.error("Error al cargar usuario:", error);
        setCustomerInfo({
          name: "Usuario no encontrado",
          email: "",
          phone: ""
        });
      }
    } catch (error) {
      toast.error("Error al cargar la reserva");
      console.error(error);
      navigate("/admin/reservations");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadReservation();
  }, [id]);

  // Abrir diálogo
  const openActionDialog = (type: "approve" | "reject" | "cancel") => {
    setActionDialog({ open: true, type });
    setAdminNotes(reservation?.admin_notes || "");
  };

  // Cerrar diálogo
  const closeActionDialog = () => {
    setActionDialog({ open: false, type: null });
    setAdminNotes("");
  };

  // Procesar acción
  const handleConfirmAction = async () => {
    if (!id || !actionDialog.type) return;

    try {
      setIsProcessing(true);

      switch (actionDialog.type) {
        case "approve":
          await approveReservation(id, adminNotes || undefined);
          toast.success("Reserva aprobada correctamente");
          break;
        case "reject":
          if (!adminNotes.trim()) {
            toast.error("Debes proporcionar un motivo para rechazar");
            return;
          }
          await rejectReservation(id, adminNotes);
          toast.error("Reserva rechazada");
          break;
        case "cancel":
          await cancelReservation(id);
          toast.info("Reserva cancelada");
          break;
      }

      // Recargar reserva
      await loadReservation();
      closeActionDialog();
    } catch (error) {
      toast.error("Error al procesar la acción");
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Formatear fecha
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("es-CR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (isLoading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </AdminLayout>
    );
  }

  if (!reservation) {
    return (
      <AdminLayout>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Reserva no encontrada</p>
          <Button asChild className="mt-4">
            <Link to="/admin/reservations">Volver a Reservas</Link>
          </Button>
        </div>
      </AdminLayout>
    );
  }

  const totalUnits = reservation.items.reduce((sum, item) => sum + item.quantity, 0);
  const StatusIcon = statusConfig[reservation.state]?.icon || Clock;

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" asChild>
              <Link to="/admin/reservations">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <div>
              <h1 className="text-2xl font-display font-bold">
                Reserva {reservation._id.slice(-8)}
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={statusConfig[reservation.state]?.variant || "secondary"}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {statusConfig[reservation.state]?.label || reservation.state}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {reservation.items.length} items • {totalUnits} unidades
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          {reservation.state === "Pendiente" && (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => openActionDialog("reject")} className="text-destructive">
                <XCircle className="h-4 w-4 mr-2" />
                Rechazar
              </Button>
              <Button onClick={() => openActionDialog("approve")}>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Aprobar
              </Button>
            </div>
          )}

          {(reservation.state === "Pendiente" || reservation.state === "Aprobada") && (
            <Button variant="outline" onClick={() => openActionDialog("cancel")}>
              <Ban className="h-4 w-4 mr-2" />
              Forzar Cancelación
            </Button>
          )}
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Customer Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Información del Cliente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {customerInfo ? (
                <>
                  <div className="flex items-start gap-3">
                    <User className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Nombre</p>
                      <p className="text-sm text-muted-foreground">{customerInfo.name}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Mail className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Email</p>
                      <p className="text-sm text-muted-foreground">{customerInfo.email}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Phone className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Teléfono</p>
                      <p className="text-sm text-muted-foreground">{customerInfo.phone}</p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Dates */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Fechas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3">
                <Calendar className="h-4 w-4 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Creada</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(reservation.created_at)}
                  </p>
                </div>
              </div>
              {reservation.expires_at && (
                <div className="flex items-start gap-3">
                  <Clock className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Expira</p>
                    <p className="text-sm text-warning">
                      {formatDate(reservation.expires_at)}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Notes */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Notas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {reservation.notes && (
                <div>
                  <p className="text-sm font-medium mb-1">Cliente:</p>
                  <p className="text-sm text-muted-foreground">{reservation.notes}</p>
                </div>
              )}
              {reservation.admin_notes && (
                <div>
                  <p className="text-sm font-medium mb-1">Admin:</p>
                  <p className="text-sm text-muted-foreground">{reservation.admin_notes}</p>
                </div>
              )}
              {!reservation.notes && !reservation.admin_notes && (
                <p className="text-sm text-muted-foreground">Sin notas</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Items */}
        <Card>
          <CardHeader>
            <CardTitle>Productos Reservados</CardTitle>
            <CardDescription>
              {reservation.items.length} productos • {totalUnits} unidades totales
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Producto</TableHead>
                  <TableHead>Variante</TableHead>
                  <TableHead className="text-right">Cantidad</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reservation.items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{item.product_name}</TableCell>
                    <TableCell className="text-muted-foreground">{item.variant_name}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Diálogo de confirmación */}
      <AlertDialog open={actionDialog.open} onOpenChange={closeActionDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {actionDialog.type === "approve" && "¿Aprobar reserva?"}
              {actionDialog.type === "reject" && "¿Rechazar reserva?"}
              {actionDialog.type === "cancel" && "¿Cancelar reserva?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {actionDialog.type === "approve" &&
                "Esta acción aprobará la reserva y liberará el inventario para el cliente."}
              {actionDialog.type === "reject" &&
                "Esta acción rechazará la reserva y devolverá el inventario. Debes proporcionar un motivo."}
              {actionDialog.type === "cancel" &&
                "Esta acción cancelará forzadamente la reserva y devolverá el inventario."}
            </AlertDialogDescription>
          </AlertDialogHeader>

          {(actionDialog.type === "reject" || actionDialog.type === "approve") && (
            <div className="space-y-2">
              <label className="text-sm font-medium">
                {actionDialog.type === "reject" ? "Motivo del rechazo *" : "Notas (opcional)"}
              </label>
              <Textarea
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder={
                  actionDialog.type === "reject"
                    ? "Explica el motivo del rechazo..."
                    : "Agrega notas adicionales..."
                }
                rows={3}
              />
            </div>
          )}

          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmAction} disabled={isProcessing}>
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Procesando...
                </>
              ) : (
                "Confirmar"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </AdminLayout>
  );
};

export default ReservationDetail;