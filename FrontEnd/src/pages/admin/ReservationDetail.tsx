import { useParams, Link } from "react-router-dom";
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
  ArrowLeft,
  User,
  Mail,
  Phone,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  Ban,
} from "lucide-react";
import { toast } from "sonner";

// Mock data
const reservationData = {
  id: "RES-001",
  status: "pending" as const,
  customer: {
    id: "cust-1",
    name: "María García",
    email: "maria@email.com",
    phone: "+506 8888-1234",
  },
  createdAt: "2024-01-15 10:30",
  expiresAt: "2024-01-17 10:30",
  items: [
    {
      id: "1",
      productName: "Porcelanato Terrazo Blanco",
      variant: "60x60",
      quantity: 5,
      image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=100&h=100&fit=crop",
    },
    {
      id: "2",
      productName: "Mármol Calacatta Gold",
      variant: "80x160",
      quantity: 8,
      image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=100&h=100&fit=crop",
    },
    {
      id: "3",
      productName: "Cerámica Subway Blanca",
      variant: "10x20",
      quantity: 2,
      image: "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=100&h=100&fit=crop",
    },
  ],
  notes: "Cliente solicita entrega lo antes posible. Contactar antes de las 5pm.",
};

const statusConfig = {
  pending: { label: "Pendiente", variant: "pending" as const },
  approved: { label: "Aprobada", variant: "success" as const },
  rejected: { label: "Rechazada", variant: "destructive" as const },
  cancelled: { label: "Cancelada", variant: "secondary" as const },
  expired: { label: "Expirada", variant: "secondary" as const },
};

const ReservationDetail = () => {
  const { id } = useParams();

  const handleApprove = () => {
    toast.success(`Reserva ${id} aprobada correctamente`);
  };

  const handleReject = () => {
    toast.error(`Reserva ${id} rechazada`);
  };

  const handleCancel = () => {
    toast.info(`Reserva ${id} cancelada forzosamente`);
  };

  const totalUnits = reservationData.items.reduce((sum, item) => sum + item.quantity, 0);

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
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-display font-bold">{reservationData.id}</h1>
                <Badge variant={statusConfig[reservationData.status].variant}>
                  {statusConfig[reservationData.status].label}
                </Badge>
              </div>
              <p className="text-muted-foreground">Detalles de la reserva</p>
            </div>
          </div>

          {reservationData.status === "pending" && (
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleReject}>
                <XCircle className="h-4 w-4 mr-2" />
                Rechazar
              </Button>
              <Button onClick={handleApprove}>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Aprobar
              </Button>
            </div>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Items */}
            <Card>
              <CardHeader>
                <CardTitle>Productos Reservados</CardTitle>
                <CardDescription>
                  {reservationData.items.length} productos • {totalUnits} unidades totales
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Producto</TableHead>
                      <TableHead>Variante</TableHead>
                      <TableHead className="text-center">Cantidad</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reservationData.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <img
                              src={item.image}
                              alt={item.productName}
                              className="h-12 w-12 rounded-lg object-cover"
                            />
                            <span className="font-medium">{item.productName}</span>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono">{item.variant} cm</TableCell>
                        <TableCell className="text-center font-medium">{item.quantity}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Notes */}
            {reservationData.notes && (
              <Card>
                <CardHeader>
                  <CardTitle>Notas</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{reservationData.notes}</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Customer Info */}
            <Card>
              <CardHeader>
                <CardTitle>Información del Cliente</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">{reservationData.customer.name}</p>
                    <Link
                      to={`/admin/users/${reservationData.customer.id}`}
                      className="text-xs text-primary hover:underline"
                    >
                      Ver perfil
                    </Link>
                  </div>
                </div>
                <Separator />
                <div className="space-y-3">
                  <div className="flex items-center gap-3 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={`mailto:${reservationData.customer.email}`}
                      className="text-primary hover:underline"
                    >
                      {reservationData.customer.email}
                    </a>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={`tel:${reservationData.customer.phone}`}
                      className="hover:underline"
                    >
                      {reservationData.customer.phone}
                    </a>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Dates */}
            <Card>
              <CardHeader>
                <CardTitle>Fechas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-muted-foreground">Creada</p>
                    <p className="font-medium">{reservationData.createdAt}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Clock className="h-4 w-4 text-warning" />
                  <div>
                    <p className="text-muted-foreground">Expira</p>
                    <p className="font-medium text-warning">{reservationData.expiresAt}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            {(reservationData.status === "pending" || reservationData.status === "approved") && (
              <Card>
                <CardHeader>
                  <CardTitle>Acciones</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full text-destructive hover:text-destructive"
                    onClick={handleCancel}
                  >
                    <Ban className="h-4 w-4 mr-2" />
                    Forzar Cancelación
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default ReservationDetail;
