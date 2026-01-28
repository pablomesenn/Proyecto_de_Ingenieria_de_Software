import { useEffect, useState } from "react";
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
import {
  getDashboardStats,
  getPendingReservations,
  getExpiringReservations,
  getLowStockProducts,
  type DashboardStats as DashboardStatsType,
  type PendingReservation,
  type ExpiringReservation,
  type LowStockProduct,
} from "@/api/dashboard";

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStatsType | null>(null);
  const [pendingReservations, setPendingReservations] = useState<PendingReservation[]>([]);
  const [expiringReservations, setExpiringReservations] = useState<ExpiringReservation[]>([]);
  const [lowStockProducts, setLowStockProducts] = useState<LowStockProduct[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, pendingData, expiringData, lowStockData] = await Promise.all([
          getDashboardStats(),
          getPendingReservations(),
          getExpiringReservations(),
          getLowStockProducts(),
        ]);

        setStats(statsData);
        setPendingReservations(pendingData);
        setExpiringReservations(expiringData);
        setLowStockProducts(lowStockData);
      } catch (error) {
        console.error("Error cargando datos del dashboard:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading || !stats) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Cargando...</div>
        </div>
      </AdminLayout>
    );
  }

  const statsCards = [
    {
      name: "Reservas Pendientes",
      value: stats.pending_reservations.value,
      change: stats.pending_reservations.change,
      changeType: "increase" as const,
      icon: CalendarClock,
      href: "/admin/reservations",
      color: "text-warning",
      bgColor: "bg-warning/10",
    },
    {
      name: "Productos Activos",
      value: stats.active_products.value,
      change: `${stats.active_products.low_stock} sin stock`,
      changeType: stats.active_products.low_stock > 0 ? ("warning" as const) : ("increase" as const),
      icon: Package,
      href: "/admin/products",
      color: "text-success",
      bgColor: "bg-success/10",
    },
    {
      name: "Usuarios Registrados",
      value: stats.total_users.value,
      change: `+${stats.total_users.new_this_month} este mes`,
      changeType: "increase" as const,
      icon: Users,
      href: "/admin/users",
      color: "text-primary",
      bgColor: "bg-primary/10",
    },
    {
      name: "Alertas Activas",
      value: stats.alerts.value,
      change: "Requieren atención",
      changeType: "warning" as const,
      icon: AlertTriangle,
      href: "/admin/inventory",
      color: "text-destructive",
      bgColor: "bg-destructive/10",
    },
  ];

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-display font-bold">Panel de Administración</h1>
          <p className="text-muted-foreground">Resumen general del sistema</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statsCards.map((stat) => (
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

        <div className="grid gap-6 lg:grid-cols-2">
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
              {pendingReservations.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No hay reservas pendientes
                </p>
              ) : (
                pendingReservations.map((reservation) => (
                  <div
                    key={reservation._id}
                    className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <CalendarClock className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{reservation.customer_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {reservation.items_count} productos • {reservation.total_units} unidades
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      {reservation.expires_in && (
                        <Badge variant="pending" className="text-xs">
                          <Clock className="h-3 w-3 mr-1" />
                          {reservation.expires_in}
                        </Badge>
                      )}
                      <div className="flex gap-1 mt-2">
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7"
                          asChild
                        >
                          <Link to={`/admin/reservations/${reservation._id}`}>
                            <Eye className="h-4 w-4" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Alertas del Sistema</CardTitle>
              <CardDescription>Situaciones que requieren atención</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {expiringReservations.length > 0 && (
                <div className="p-4 rounded-lg border border-warning/50 bg-warning/5">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-warning" />
                    <span className="font-medium text-sm">Reservas por Expirar</span>
                  </div>
                  <div className="space-y-2">
                    {expiringReservations.map((res) => (
                      <div key={res._id} className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{res.customer_name}</span>
                        <span className="text-warning font-medium">{res.expires_in}</span>
                      </div>
                    ))}
                  </div>
                  <Button variant="outline" size="sm" className="mt-3 w-full" asChild>
                    <Link to="/admin/reservations">Ver reservas</Link>
                  </Button>
                </div>
              )}

              {lowStockProducts.length > 0 && (
                <div className="p-4 rounded-lg border border-destructive/50 bg-destructive/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Package className="h-4 w-4 text-destructive" />
                    <span className="font-medium text-sm">Stock Bajo</span>
                  </div>
                  <div className="space-y-2">
                    {lowStockProducts.map((product) => (
                      <div key={`${product._id}-${product.variant_name}`} className="flex justify-between text-sm">
                        <span className="text-muted-foreground truncate max-w-[200px]">
                          {product.name} ({product.variant_name})
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
              )}

              {expiringReservations.length === 0 && lowStockProducts.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No hay alertas activas
                </p>
              )}
            </CardContent>
          </Card>
        </div>

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
              <Button variant="outline" className="h-auto py-4 flex flex col gap-2" asChild>
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

function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(" ");
}

export default Dashboard;