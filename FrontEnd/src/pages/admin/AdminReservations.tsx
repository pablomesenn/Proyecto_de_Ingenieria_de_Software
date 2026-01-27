import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  CheckCircle2,
  XCircle,
  Ban,
  CalendarClock,
  Clock,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import {
  getAllReservations,
  approveReservation,
  rejectReservation,
  cancelReservation,
  type Reservation,
} from "@/api/reservations";

const statusConfig = {
  Pendiente: { label: "Pendiente", variant: "pending" as const, icon: Clock },
  Aprobada: { label: "Aprobada", variant: "success" as const, icon: CheckCircle2 },
  Rechazada: { label: "Rechazada", variant: "destructive" as const, icon: XCircle },
  Cancelada: { label: "Cancelada", variant: "secondary" as const, icon: Ban },
  Expirada: { label: "Expirada", variant: "secondary" as const, icon: CalendarClock },
};

const AdminReservations = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [actionDialog, setActionDialog] = useState<{
    open: boolean;
    type: "approve" | "reject" | "cancel" | null;
    reservationId: string | null;
  }>({ open: false, type: null, reservationId: null });
  const [adminNotes, setAdminNotes] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // Cargar reservas
  const loadReservations = async () => {
    try {
      setIsLoading(true);
      const data = await getAllReservations();
      console.log("📦 Reservas cargadas:", data.reservations);
      console.log("📦 Primera reserva items:", data.reservations[0]?.items);
      setReservations(data.reservations);
    } catch (error) {
      toast.error("Error al cargar reservas");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadReservations();
  }, []);

  // Filtrar reservas
  const filteredReservations = reservations.filter((reservation) => {
    if (searchQuery && !reservation._id.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (statusFilter !== "all" && reservation.state !== statusFilter) {
      return false;
    }
    return true;
  });

  // Verificar si una reserva está expirada (visualmente)
  const isExpired = (reservation: Reservation) => {
    if (reservation.state === "Expirada") return true;
    if (reservation.state !== "Pendiente") return false;
    if (!reservation.expires_at) return false;
    return new Date(reservation.expires_at) < new Date();
  };

  // Abrir diálogo de confirmación
  const openActionDialog = (type: "approve" | "reject" | "cancel", reservationId: string) => {
    setActionDialog({ open: true, type, reservationId });
    setAdminNotes("");
  };

  // Cerrar diálogo
  const closeActionDialog = () => {
    setActionDialog({ open: false, type: null, reservationId: null });
    setAdminNotes("");
  };

  // Procesar acción
  const handleConfirmAction = async () => {
    if (!actionDialog.reservationId || !actionDialog.type) return;

    try {
      setIsProcessing(true);

      switch (actionDialog.type) {
        case "approve":
          await approveReservation(actionDialog.reservationId, adminNotes || undefined);
          toast.success("Reserva aprobada correctamente");
          break;
        case "reject":
          if (!adminNotes.trim()) {
            toast.error("Debes proporcionar un motivo para rechazar");
            return;
          }
          await rejectReservation(actionDialog.reservationId, adminNotes);
          toast.error("Reserva rechazada");
          break;
        case "cancel":
          await cancelReservation(actionDialog.reservationId);
          toast.info("Reserva cancelada");
          break;
      }

      // Recargar reservas
      await loadReservations();
      closeActionDialog();
    } catch (error) {
      toast.error("Error al procesar la acción");
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  const pendingCount = reservations.filter((r) => r.state === "Pendiente").length;

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

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-display font-bold">Gestión de Reservas</h1>
            <div className="text-muted-foreground flex items-center gap-2">
              <span>Administra las reservas de clientes</span>
              {pendingCount > 0 && (
                <Badge variant="pending">
                  {pendingCount} pendientes
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los estados</SelectItem>
                  <SelectItem value="Pendiente">Pendientes</SelectItem>
                  <SelectItem value="Aprobada">Aprobadas</SelectItem>
                  <SelectItem value="Rechazada">Rechazadas</SelectItem>
                  <SelectItem value="Cancelada">Canceladas</SelectItem>
                  <SelectItem value="Expirada">Expiradas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Reservations Table */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead className="text-center">Items</TableHead>
                    <TableHead>Fecha Creación</TableHead>
                    <TableHead>Expira</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="w-[80px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredReservations.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="h-32 text-center">
                        <div className="flex flex-col items-center gap-2">
                          <CalendarClock className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No se encontraron reservas</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredReservations.map((reservation) => {
                      const StatusIcon = statusConfig[reservation.state].icon;
                      return (
                        <TableRow key={reservation._id}>
                          <TableCell className="font-mono font-medium">
                            <Link
                              to={`/admin/reservations/${reservation._id}`}
                              className="hover:text-primary transition-colors"
                            >
                              {reservation._id.slice(-8)}
                            </Link>
                          </TableCell>
                          <TableCell className="text-center">
                            <div className="flex flex-col items-center">
                              <span className="font-medium">{reservation.items?.length || 0}</span>
                              <span className="text-xs text-muted-foreground">
                                ({reservation.items?.reduce((sum, item) => sum + item.quantity, 0) || 0} unidades)
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                            {formatDate(reservation.created_at)}
                          </TableCell>
                          <TableCell className="text-sm whitespace-nowrap">
                            {reservation.expires_at ? (
                              <span
                                className={
                                  reservation.state === "Pendiente" ? "text-warning" : "text-muted-foreground"
                                }
                              >
                                {formatDate(reservation.expires_at)}
                              </span>
                            ) : (
                              <span className="text-muted-foreground">—</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Badge variant={statusConfig[reservation.state].variant}>
                                <StatusIcon className="h-3 w-3 mr-1" />
                                {statusConfig[reservation.state].label}
                              </Badge>
                              {isExpired(reservation) && reservation.state === "Pendiente" && (
                                <Badge variant="secondary" className="text-xs">
                                  Expiró
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem asChild>
                                  <Link
                                    to={`/admin/reservations/${reservation._id}`}
                                    className="cursor-pointer"
                                  >
                                    <Eye className="h-4 w-4 mr-2" />
                                    Ver Detalles
                                  </Link>
                                </DropdownMenuItem>
                                {reservation.state === "Pendiente" && (
                                  <>
                                    <DropdownMenuItem
                                      onClick={() => openActionDialog("approve", reservation._id)}
                                      className="text-success cursor-pointer"
                                    >
                                      <CheckCircle2 className="h-4 w-4 mr-2" />
                                      Aprobar
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      onClick={() => openActionDialog("reject", reservation._id)}
                                      className="text-destructive cursor-pointer"
                                    >
                                      <XCircle className="h-4 w-4 mr-2" />
                                      Rechazar
                                    </DropdownMenuItem>
                                  </>
                                )}
                                {(reservation.state === "Pendiente" || reservation.state === "Aprobada") && (
                                  <DropdownMenuItem
                                    onClick={() => openActionDialog("cancel", reservation._id)}
                                    className="cursor-pointer"
                                  >
                                    <Ban className="h-4 w-4 mr-2" />
                                    Forzar Cancelación
                                  </DropdownMenuItem>
                                )}
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            )}
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

export default AdminReservations;