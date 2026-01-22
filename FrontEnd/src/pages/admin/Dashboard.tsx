import { Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Package,
  CalendarClock,
  Users,
  AlertTriangle,
  TrendingUp,
  Clock,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Eye,
} from "lucide-react";

// Mock data
const stats = [
  {
    name: "Reservas Pendientes",
    value: 12,
    change: "+3 hoy",
    changeType: "increase" as const,
    icon: CalendarClock,
    href: "/admin/reservations",
    color: "text-warning",
    bgColor: "bg-warning/10",
  },
  {
    name: "Productos Activos",
    value: 156,
    change: "8 sin stock",
    changeType: "warning" as const,
    icon: Package,
    href: "/admin/products",
    color: "text-success",
    bgColor: "bg-success/10",
  },
  {
    name: "Usuarios Registrados",
    value: 324,
    change: "+12 este mes",
    changeType: "increase" as const,
    icon: Users,
    href: "/admin/users",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    name: "Alertas Activas",
    value: 5,
    change: "Requieren atención",
    changeType: "warning" as const,
    icon: AlertTriangle,
    href: "/admin/inventory",
    color: "text-destructive",
    bgColor: "bg-destructive/10",
  },
];

const pendingReservations = [
  {
    id: "RES-001",
    customer: "María García",
    items: 3,
    date: "2024-01-15",
    expiresIn: "2 días",
    total: "15 unidades",
  },
  {
    id: "RES-002",
    customer: "Carlos López",
    items: 5,
    date: "2024-01-14",
    expiresIn: "1 día",
    total: "28 unidades",
  },
  {
    id: "RES-003",
    customer: "Ana Martínez",
    items: 2,
    date: "2024-01-14",
    expiresIn: "3 días",
    total: "8 unidades",
  },
];

const expiringReservations = [
  { id: "RES-005", customer: "Pedro Sánchez", expiresIn: "4 horas" },
  { id: "RES-008", customer: "Laura Fernández", expiresIn: "8 horas" },
];

const lowStockProducts = [
  { id: "1", name: "Porcelanato Terrazo Blanco", variant: "60x60", stock: 5 },
  { id: "2", name: "Mármol Calacatta Gold", variant: "80x160", stock: 2 },
  { id: "3", name: "Cerámica Subway Blanca", variant: "10x20", stock: 8 },
];

const Dashboard = () => {
  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-display font-bold">Panel de Administración</h1>
          <p className="text-muted-foreground">Resumen general del sistema</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Link key={stat.name} to={stat.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className={cn("p-2 rounded-lg", stat.bgColor)}>
                      <stat.icon className={cn("h-5 w-5", stat.color)} />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="mt-4">
                    <p className="text-3xl font-bold">{stat.value}</p>
                    <p className="text-sm text-muted-foreground">{stat.name}</p>
                  </div>
                  <div className="mt-2">
                    <Badge
                      variant={stat.changeType === "increase" ? "success" : "warning"}
                      className="text-xs"
                    >
                      {stat.change}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Main content grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Pending Reservations */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">Reservas Pendientes</CardTitle>
                <CardDescription>Reservas que requieren aprobación</CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link to="/admin/reservations">Ver todas</Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {pendingReservations.map((reservation) => (
                <div
                  key={reservation.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <CalendarClock className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{reservation.customer}</p>
                      <p className="text-xs text-muted-foreground">
                        {reservation.items} productos • {reservation.total}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="pending" className="text-xs">
                      <Clock className="h-3 w-3 mr-1" />
                      {reservation.expiresIn}
                    </Badge>
                    <div className="flex gap-1 mt-2">
                      <Button size="icon" variant="ghost" className="h-7 w-7">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button size="icon" variant="ghost" className="h-7 w-7 text-success">
                        <CheckCircle2 className="h-4 w-4" />
                      </Button>
                      <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive">
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Alertas del Sistema</CardTitle>
              <CardDescription>Situaciones que requieren atención</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Expiring Reservations Alert */}
              <div className="p-4 rounded-lg border border-warning/50 bg-warning/5">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <span className="font-medium text-sm">Reservas por Expirar</span>
                </div>
                <div className="space-y-2">
                  {expiringReservations.map((res) => (
                    <div key={res.id} className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{res.customer}</span>
                      <span className="text-warning font-medium">{res.expiresIn}</span>
                    </div>
                  ))}
                </div>
                <Button variant="outline" size="sm" className="mt-3 w-full">
                  Ver reservas
                </Button>
              </div>

              {/* Low Stock Alert */}
              <div className="p-4 rounded-lg border border-destructive/50 bg-destructive/5">
                <div className="flex items-center gap-2 mb-2">
                  <Package className="h-4 w-4 text-destructive" />
                  <span className="font-medium text-sm">Stock Bajo</span>
                </div>
                <div className="space-y-2">
                  {lowStockProducts.map((product) => (
                    <div key={product.id} className="flex justify-between text-sm">
                      <span className="text-muted-foreground truncate max-w-[200px]">
                        {product.name} ({product.variant})
                      </span>
                      <Badge variant="destructive" className="text-xs">
                        {product.stock} uds
                      </Badge>
                    </div>
                  ))}
                </div>
                <Button variant="outline" size="sm" className="mt-3 w-full" asChild>
                  <Link to="/admin/inventory">Gestionar inventario</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Accesos Rápidos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" asChild>
                <Link to="/admin/products/new">
                  <Package className="h-5 w-5" />
                  <span className="text-sm">Nuevo Producto</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" asChild>
                <Link to="/admin/inventory/adjust">
                  <TrendingUp className="h-5 w-5" />
                  <span className="text-sm">Ajustar Inventario</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" asChild>
                <Link to="/admin/users/new">
                  <Users className="h-5 w-5" />
                  <span className="text-sm">Nuevo Usuario</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" asChild>
                <Link to="/admin/export">
                  <TrendingUp className="h-5 w-5" />
                  <span className="text-sm">Exportar Datos</span>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

// Helper function for className merging
function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(" ");
}

export default Dashboard;
