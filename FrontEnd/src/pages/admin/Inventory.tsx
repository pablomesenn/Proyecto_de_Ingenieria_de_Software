import { useState, useEffect } from "react";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Filter,
  Warehouse,
  TrendingUp,
  TrendingDown,
  Package,
  AlertTriangle,
  History,
} from "lucide-react";
import { getAllInventory, fetchInventoryMovements } from "@/api/inventory";
import { toast } from "sonner";

// Mock data - se reemplazará con datos reales
const inventoryItems = [
  {
    id: "1",
    productName: "Porcelanato Terrazo Blanco",
    variant: "60x60",
    totalStock: 120,
    reserved: 15,
    available: 105,
    category: "Porcelanato",
  },
];

const movementHistory = [
  {
    id: "1",
    date: "2024-01-15 14:30",
    product: "Porcelanato Terrazo Blanco",
    variant: "60x60",
    type: "entrada" as const,
    quantity: 50,
    reason: "Recepción de proveedor",
    user: "Admin",
  },
];

const Inventory = () => {
  const [loading, setLoading] = useState(true);
  const [inventoryItems, setInventoryItems] = useState<any[]>([]);
  const [movements, setMovements] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [stockFilter, setStockFilter] = useState<string>("all");

  // Cargar datos desde la API
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Cargar inventario
        const inventoryResult = await getAllInventory(0, 100);
        const transformedInventory = (inventoryResult.inventory || []).map((item: any) => {
          const disponibilidad = (item.stock_total || 0) - (item.stock_retenido || 0);
          return {
            id: item._id || item.variant_id,
            productName: item.product_name || "Producto desconocido",
            variant: item.variant_size || "N/A",
            totalStock: item.stock_total || 0,
            reserved: item.stock_retenido || 0,
            available: Math.max(0, disponibilidad),
            category: "General", // Ajustar según tus datos
          };
        });
        setInventoryItems(transformedInventory);

        // Cargar historial de movimientos
        const movementsResult = await fetchInventoryMovements({ limit: 50 });
        const transformedMovements = (movementsResult.movements || []).map((movement: any) => ({
          id: movement._id,
          date: new Date(movement.creado_en).toLocaleString("es-ES"),
          product: movement.product_name || "Producto desconocido",
          variant: movement.variant_name || "N/A",
          type: movement.movement_type === "adjustment" 
            ? "ajuste" 
            : movement.movement_type === "retain" 
            ? "entrada" 
            : movement.movement_type === "release"
            ? "salida"
            : movement.movement_type,
          quantity: movement.quantity,
          reason: movement.reason || "Sin especificar",
          user: movement.actor_name || "Sistema",
        }));
        setMovements(transformedMovements);
      } catch (error) {
        console.error("Error cargando datos de inventario:", error);
        toast.error("Error al cargar los datos de inventario");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const categories = [...new Set(inventoryItems.map((item) => item.category))];

  const filteredItems = inventoryItems.filter((item) => {
    if (searchQuery && !item.productName.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (categoryFilter !== "all" && item.category !== categoryFilter) {
      return false;
    }
    if (stockFilter === "low" && item.available >= 20) {
      return false;
    }
    if (stockFilter === "out" && item.available > 0) {
      return false;
    }
    return true;
  });

  const totalStock = inventoryItems.reduce((sum, item) => sum + item.totalStock, 0);
  const totalReserved = inventoryItems.reduce((sum, item) => sum + item.reserved, 0);
  const lowStockCount = inventoryItems.filter((item) => item.available > 0 && item.available < 20).length;
  const outOfStockCount = inventoryItems.filter((item) => item.available === 0).length;

  return (
    <AdminLayout>
      {loading ? (
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Cargando datos de inventario...</p>
        </div>
      ) : (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-display font-bold">Gestión de Inventario</h1>
            <p className="text-muted-foreground">Control de stock por producto y variante</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link to="/admin/inventory/history">
                <History className="h-4 w-4 mr-2" />
                Ver Historial
              </Link>
            </Button>
            <Button asChild>
              <Link to="/admin/inventory/adjust">
                <TrendingUp className="h-4 w-4 mr-2" />
                Ajustar Inventario
              </Link>
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Warehouse className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{totalStock}</p>
                  <p className="text-xs text-muted-foreground">Stock Total</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/10">
                  <Package className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{totalStock - totalReserved}</p>
                  <p className="text-xs text-muted-foreground">Disponible</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-warning/10">
                  <AlertTriangle className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{lowStockCount}</p>
                  <p className="text-xs text-muted-foreground">Stock Bajo</p>
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
                  <p className="text-2xl font-bold">{outOfStockCount}</p>
                  <p className="text-xs text-muted-foreground">Sin Stock</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="inventory" className="space-y-6">
          <TabsList>
            <TabsTrigger value="inventory" className="gap-2">
              <Warehouse className="h-4 w-4" />
              Inventario
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <History className="h-4 w-4" />
              Historial de Movimientos
            </TabsTrigger>
          </TabsList>

          {/* Inventory Tab */}
          <TabsContent value="inventory">
            <Card>
              <CardHeader>
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar productos..."
                      className="pl-10"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger className="w-full sm:w-[180px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Categoría" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas</SelectItem>
                      {categories.map((cat) => (
                        <SelectItem key={cat} value={cat}>
                          {cat}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={stockFilter} onValueChange={setStockFilter}>
                    <SelectTrigger className="w-full sm:w-[180px]">
                      <SelectValue placeholder="Estado de stock" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos</SelectItem>
                      <SelectItem value="low">Stock Bajo</SelectItem>
                      <SelectItem value="out">Sin Stock</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Producto</TableHead>
                      <TableHead>Variante</TableHead>
                      <TableHead className="text-center">Stock Total</TableHead>
                      <TableHead className="text-center">Reservado</TableHead>
                      <TableHead className="text-center">Disponible</TableHead>
                      <TableHead>Estado</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredItems.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="h-32 text-center">
                          <p className="text-muted-foreground">No se encontraron items</p>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredItems.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{item.productName}</p>
                              <Badge variant="category" className="text-xs mt-1">
                                {item.category}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell className="font-mono">{item.variant} cm</TableCell>
                          <TableCell className="text-center">{item.totalStock}</TableCell>
                          <TableCell className="text-center">{item.reserved}</TableCell>
                          <TableCell className="text-center font-medium">
                            {item.available}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                item.available === 0
                                  ? "destructive"
                                  : item.available < 20
                                  ? "warning"
                                  : "success"
                              }
                            >
                              {item.available === 0
                                ? "Sin Stock"
                                : item.available < 20
                                ? "Stock Bajo"
                                : "Normal"}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>Historial de Movimientos</CardTitle>
                <CardDescription>Registro de todas las transacciones de inventario</CardDescription>
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
                      <TableHead>Razón</TableHead>
                      <TableHead>Usuario</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {movements.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="h-32 text-center">
                          <p className="text-muted-foreground">No hay movimientos registrados</p>
                        </TableCell>
                      </TableRow>
                    ) : (
                      movements.map((movement) => (
                        <TableRow key={movement.id}>
                          <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                            {movement.date}
                          </TableCell>
                          <TableCell className="font-medium">{movement.product}</TableCell>
                          <TableCell className="font-mono">{movement.variant}</TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                movement.type === "entrada"
                                  ? "success"
                                  : movement.type === "salida"
                                  ? "destructive"
                                  : "warning"
                              }
                            >
                              {movement.type === "entrada"
                                ? "Entrada"
                                : movement.type === "salida"
                                ? "Salida"
                                : "Ajuste"}
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
                          <TableCell className="text-sm">{movement.reason}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {movement.user}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      )}
    </AdminLayout>
  );
};

export default Inventory;
