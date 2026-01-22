import { useState } from "react";
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
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  CheckCircle2,
  XCircle,
  Ban,
  CalendarClock,
  Clock,
} from "lucide-react";
import { toast } from "sonner";

// Mock data
const reservations = [
  {
    id: "RES-001",
    customer: { name: "María García", email: "maria@email.com" },
    items: 3,
    totalUnits: 15,
    status: "pending" as const,
    createdAt: "2024-01-15 10:30",
    expiresAt: "2024-01-17 10:30",
  },
  {
    id: "RES-002",
    customer: { name: "Carlos López", email: "carlos@email.com" },
    items: 5,
    totalUnits: 28,
    status: "pending" as const,
    createdAt: "2024-01-14 14:15",
    expiresAt: "2024-01-16 14:15",
  },
  {
    id: "RES-003",
    customer: { name: "Ana Martínez", email: "ana@email.com" },
    items: 2,
    totalUnits: 8,
    status: "approved" as const,
    createdAt: "2024-01-13 09:00",
    expiresAt: "2024-01-20 09:00",
  },
  {
    id: "RES-004",
    customer: { name: "Pedro Sánchez", email: "pedro@email.com" },
    items: 4,
    totalUnits: 20,
    status: "rejected" as const,
    createdAt: "2024-01-12 16:45",
    expiresAt: null,
  },
  {
    id: "RES-005",
    customer: { name: "Laura Fernández", email: "laura@email.com" },
    items: 1,
    totalUnits: 5,
    status: "cancelled" as const,
    createdAt: "2024-01-11 11:20",
    expiresAt: null,
  },
  {
    id: "RES-006",
    customer: { name: "Diego Ramírez", email: "diego@email.com" },
    items: 6,
    totalUnits: 35,
    status: "expired" as const,
    createdAt: "2024-01-05 08:00",
    expiresAt: "2024-01-07 08:00",
  },
];

const statusConfig = {
  pending: { label: "Pendiente", variant: "pending" as const, icon: Clock },
  approved: { label: "Aprobada", variant: "success" as const, icon: CheckCircle2 },
  rejected: { label: "Rechazada", variant: "destructive" as const, icon: XCircle },
  cancelled: { label: "Cancelada", variant: "secondary" as const, icon: Ban },
  expired: { label: "Expirada", variant: "secondary" as const, icon: CalendarClock },
};

const AdminReservations = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredReservations = reservations.filter((reservation) => {
    if (
      searchQuery &&
      !reservation.customer.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !reservation.id.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    if (statusFilter !== "all" && reservation.status !== statusFilter) {
      return false;
    }
    return true;
  });

  const handleApprove = (id: string) => {
    toast.success(`Reserva ${id} aprobada correctamente`);
  };

  const handleReject = (id: string) => {
    toast.error(`Reserva ${id} rechazada`);
  };

  const handleCancel = (id: string) => {
    toast.info(`Reserva ${id} cancelada`);
  };

  const pendingCount = reservations.filter((r) => r.status === "pending").length;

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-display font-bold">Gestión de Reservas</h1>
            <p className="text-muted-foreground">
              Administra las reservas de clientes
              {pendingCount > 0 && (
                <Badge variant="pending" className="ml-2">
                  {pendingCount} pendientes
                </Badge>
              )}
            </p>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por cliente o ID..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los estados</SelectItem>
                  <SelectItem value="pending">Pendientes</SelectItem>
                  <SelectItem value="approved">Aprobadas</SelectItem>
                  <SelectItem value="rejected">Rechazadas</SelectItem>
                  <SelectItem value="cancelled">Canceladas</SelectItem>
                  <SelectItem value="expired">Expiradas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Reservations Table */}
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead className="text-center">Items</TableHead>
                  <TableHead className="text-center">Unidades</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Expira</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReservations.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="h-32 text-center">
                      <div className="flex flex-col items-center gap-2">
                        <CalendarClock className="h-8 w-8 text-muted-foreground" />
                        <p className="text-muted-foreground">No se encontraron reservas</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredReservations.map((reservation) => {
                    const StatusIcon = statusConfig[reservation.status].icon;
                    return (
                      <TableRow key={reservation.id}>
                        <TableCell className="font-mono font-medium">
                          <Link
                            to={`/admin/reservations/${reservation.id}`}
                            className="hover:text-primary transition-colors"
                          >
                            {reservation.id}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{reservation.customer.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {reservation.customer.email}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell className="text-center">{reservation.items}</TableCell>
                        <TableCell className="text-center">{reservation.totalUnits}</TableCell>
                        <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                          {reservation.createdAt}
                        </TableCell>
                        <TableCell className="text-sm whitespace-nowrap">
                          {reservation.expiresAt ? (
                            <span
                              className={
                                reservation.status === "pending" ? "text-warning" : "text-muted-foreground"
                              }
                            >
                              {reservation.expiresAt}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant={statusConfig[reservation.status].variant}>
                            <StatusIcon className="h-3 w-3 mr-1" />
                            {statusConfig[reservation.status].label}
                          </Badge>
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
                                  to={`/admin/reservations/${reservation.id}`}
                                  className="cursor-pointer"
                                >
                                  <Eye className="h-4 w-4 mr-2" />
                                  Ver Detalles
                                </Link>
                              </DropdownMenuItem>
                              {reservation.status === "pending" && (
                                <>
                                  <DropdownMenuItem
                                    onClick={() => handleApprove(reservation.id)}
                                    className="text-success cursor-pointer"
                                  >
                                    <CheckCircle2 className="h-4 w-4 mr-2" />
                                    Aprobar
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    onClick={() => handleReject(reservation.id)}
                                    className="text-destructive cursor-pointer"
                                  >
                                    <XCircle className="h-4 w-4 mr-2" />
                                    Rechazar
                                  </DropdownMenuItem>
                                </>
                              )}
                              {(reservation.status === "pending" ||
                                reservation.status === "approved") && (
                                <DropdownMenuItem
                                  onClick={() => handleCancel(reservation.id)}
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
          </CardContent>
        </Card>

        {/* Summary */}
        <div className="text-sm text-muted-foreground">
          Mostrando {filteredReservations.length} de {reservations.length} reservas
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminReservations;
