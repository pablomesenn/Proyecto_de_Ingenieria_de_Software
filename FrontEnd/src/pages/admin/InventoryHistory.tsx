import { useState } from "react";
import { Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ArrowLeft,
  Search,
  Filter,
  History,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Calendar,
  Download,
} from "lucide-react";

// Mock data - extended history
const movementHistory = [
  {
    id: "1",
    date: "2024-01-15 14:30",
    product: "Porcelanato Terrazo Blanco",
    variant: "60x60",
    type: "entrada" as const,
    quantity: 50,
    previousStock: 70,
    newStock: 120,
    reason: "Recepción de proveedor",
    user: "Admin",
  },
  {
    id: "2",
    date: "2024-01-15 10:15",
    product: "Mármol Calacatta Gold",
    variant: "80x160",
    type: "salida" as const,
    quantity: -10,
    previousStock: 12,
    newStock: 2,
    reason: "Venta completada",
    user: "Admin",
  },
  {
    id: "3",
    date: "2024-01-14 16:45",
    product: "Cerámica Subway Blanca",
    variant: "10x20",
    type: "ajuste" as const,
    quantity: -5,
    previousStock: 13,
    newStock: 8,
    reason: "Corrección de inventario",
    user: "Admin",
  },
  {
    id: "4",
    date: "2024-01-14 09:00",
    product: "Granito Negro Galaxy",
    variant: "60x60",
    type: "entrada" as const,
    quantity: 100,
    previousStock: 56,
    newStock: 156,
    reason: "Recepción de proveedor",
    user: "Admin",
  },
  {
    id: "5",
    date: "2024-01-13 15:20",
    product: "Porcelanato Terrazo Blanco",
    variant: "80x80",
    type: "reserva" as const,
    quantity: -8,
    previousStock: 93,
    newStock: 85,
    reason: "Reserva RES-001",
    user: "Sistema",
  },
  {
    id: "6",
    date: "2024-01-13 11:00",
    product: "Mármol Calacatta Gold",
    variant: "60x120",
    type: "entrada" as const,
    quantity: 30,
    previousStock: 15,
    newStock: 45,
    reason: "Recepción de proveedor",
    user: "Admin",
  },
  {
    id: "7",
    date: "2024-01-12 17:30",
    product: "Cerámica Rústica Terracota",
    variant: "30x30",
    type: "salida" as const,
    quantity: -25,
    previousStock: 25,
    newStock: 0,
    reason: "Venta completada",
    user: "Admin",
  },
  {
    id: "8",
    date: "2024-01-12 09:15",
    product: "Porcelanato Terrazo Blanco",
    variant: "120x60",
    type: "ajuste" as const,
    quantity: 5,
    previousStock: 35,
    newStock: 40,
    reason: "Corrección tras conteo físico",
    user: "Admin",
  },
  {
    id: "9",
    date: "2024-01-11 14:00",
    product: "Granito Negro Galaxy",
    variant: "60x60",
    type: "reserva" as const,
    quantity: -20,
    previousStock: 176,
    newStock: 156,
    reason: "Reserva RES-002",
    user: "Sistema",
  },
  {
    id: "10",
    date: "2024-01-10 10:30",
    product: "Cerámica Subway Blanca",
    variant: "10x20",
    type: "entrada" as const,
    quantity: 200,
    previousStock: 0,
    newStock: 200,
    reason: "Recepción inicial de proveedor",
    user: "Admin",
  },
];

const products = [...new Set(movementHistory.map((m) => m.product))];

const InventoryHistory = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [productFilter, setProductFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const filteredHistory = movementHistory.filter((movement) => {
    if (
      searchQuery &&
      !movement.product.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !movement.reason.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !movement.user.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    if (productFilter !== "all" && movement.product !== productFilter) {
      return false;
    }
    if (typeFilter !== "all" && movement.type !== typeFilter) {
      return false;
    }
    // Date filtering would be implemented with actual date comparison
    return true;
  });

  const typeConfig = {
    entrada: { label: "Entrada", icon: TrendingUp, color: "success" as const },
    salida: { label: "Salida", icon: TrendingDown, color: "destructive" as const },
    ajuste: { label: "Ajuste", icon: RefreshCw, color: "warning" as const },
    reserva: { label: "Reserva", icon: Calendar, color: "secondary" as const },
  };

  const handleExport = () => {
    // In a real app, this would generate a CSV/Excel file
    const csvContent = [
      ["Fecha", "Producto", "Variante", "Tipo", "Cantidad", "Stock Anterior", "Stock Nuevo", "Razón", "Usuario"],
      ...filteredHistory.map((m) => [
        m.date,
        m.product,
        m.variant,
        typeConfig[m.type].label,
        m.quantity.toString(),
        m.previousStock.toString(),
        m.newStock.toString(),
        m.reason,
        m.user,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `historial-inventario-${new Date().toISOString().split("T")[0]}.csv`;
    link.click();
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button type="button" variant="ghost" size="icon" asChild>
            <Link to="/admin/inventory">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-display font-bold">Historial de Inventario</h1>
            <p className="text-muted-foreground">Registro completo de movimientos de stock</p>
          </div>
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Exportar CSV
          </Button>
        </div>

        {/* Stats Summary */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/10">
                  <TrendingUp className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {movementHistory.filter((m) => m.type === "entrada").length}
                  </p>
                  <p className="text-xs text-muted-foreground">Entradas</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-destructive/10">
                  <TrendingDown className="h-5 w-5 text-destructive" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {movementHistory.filter((m) => m.type === "salida").length}
                  </p>
                  <p className="text-xs text-muted-foreground">Salidas</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-warning/10">
                  <RefreshCw className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {movementHistory.filter((m) => m.type === "ajuste").length}
                  </p>
                  <p className="text-xs text-muted-foreground">Ajustes</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <History className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{movementHistory.length}</p>
                  <p className="text-xs text-muted-foreground">Total Movimientos</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
              <div className="lg:col-span-2 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por producto, razón o usuario..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={productFilter} onValueChange={setProductFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Producto" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los productos</SelectItem>
                  {products.map((product) => (
                    <SelectItem key={product} value={product}>
                      {product}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  <SelectItem value="entrada">Entrada</SelectItem>
                  <SelectItem value="salida">Salida</SelectItem>
                  <SelectItem value="ajuste">Ajuste</SelectItem>
                  <SelectItem value="reserva">Reserva</SelectItem>
                </SelectContent>
              </Select>
              <Input
                type="date"
                placeholder="Desde"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* History Table */}
        <Card>
          <CardHeader>
            <CardTitle>Movimientos</CardTitle>
            <CardDescription>
              Mostrando {filteredHistory.length} de {movementHistory.length} registros
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Producto</TableHead>
                  <TableHead>Variante</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead className="text-center">Cantidad</TableHead>
                  <TableHead className="text-center">Stock Anterior</TableHead>
                  <TableHead className="text-center">Stock Nuevo</TableHead>
                  <TableHead>Razón</TableHead>
                  <TableHead>Usuario</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredHistory.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="h-32 text-center">
                      <div className="flex flex-col items-center gap-2">
                        <History className="h-8 w-8 text-muted-foreground" />
                        <p className="text-muted-foreground">No se encontraron movimientos</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredHistory.map((movement) => {
                    const config = typeConfig[movement.type];
                    const Icon = config.icon;
                    return (
                      <TableRow key={movement.id}>
                        <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                          {movement.date}
                        </TableCell>
                        <TableCell className="font-medium max-w-[200px] truncate">
                          {movement.product}
                        </TableCell>
                        <TableCell className="font-mono text-sm">{movement.variant}</TableCell>
                        <TableCell>
                          <Badge variant={config.color} className="gap-1">
                            <Icon className="h-3 w-3" />
                            {config.label}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <span
                            className={
                              movement.quantity > 0
                                ? "text-success font-medium"
                                : "text-destructive font-medium"
                            }
                          >
                            {movement.quantity > 0 ? "+" : ""}
                            {movement.quantity}
                          </span>
                        </TableCell>
                        <TableCell className="text-center text-muted-foreground">
                          {movement.previousStock}
                        </TableCell>
                        <TableCell className="text-center font-medium">
                          {movement.newStock}
                        </TableCell>
                        <TableCell className="text-sm max-w-[200px] truncate">
                          {movement.reason}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {movement.user}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default InventoryHistory;