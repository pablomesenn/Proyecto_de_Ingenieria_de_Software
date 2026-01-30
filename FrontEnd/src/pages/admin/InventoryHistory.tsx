import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { fetchInventoryMovements, type InventoryMovement } from "@/api/inventory";
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
  Loader2,
} from "lucide-react";

/**
 * UI filters ("entrada/salida/ajuste/reserva") -> backend movement_type
 * Ajusta estos arrays si tu backend usa otros valores.
 */
const TYPE_MAP: Record<string, string[] | undefined> = {
  all: undefined,
  entrada: ["initial", "increase", "in"],
  salida: ["decrease", "out", "sale"],
  ajuste: ["adjustment"],
  reserva: ["retain", "release"],
};

const typeConfig: Record<string, { label: string; icon: any; color: any }> = {
  initial: { label: "Inicial", icon: History, color: "secondary" },
  adjustment: { label: "Ajuste", icon: RefreshCw, color: "warning" },
  retain: { label: "Retención", icon: Calendar, color: "secondary" },
  release: { label: "Liberación", icon: Calendar, color: "secondary" },
  increase: { label: "Entrada", icon: TrendingUp, color: "success" },
  in: { label: "Entrada", icon: TrendingUp, color: "success" },
  decrease: { label: "Salida", icon: TrendingDown, color: "destructive" },
  out: { label: "Salida", icon: TrendingDown, color: "destructive" },
  sale: { label: "Salida", icon: TrendingDown, color: "destructive" },
};

function formatDate(value?: string | Date | null) {
  if (!value) return "";
  const d = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString();
}

function toISODateOnly(value?: string | Date | null) {
  if (!value) return "";
  const d = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(d.getTime())) return "";
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

const InventoryHistory = () => {
  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [productFilter, setProductFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  // Data
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [loading, setLoading] = useState(true);

  // Pagination / backend params
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);

  // (Opcional) filtrar por una variante exacta si lo ocupas luego
  const [variantId, setVariantId] = useState<string>("");

  // Cargar movimientos desde backend
  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);

        // Si tu backend soporta filtrar por movement_type exacto,
        // aquí NO enviamos "entrada/salida" porque son grupos.
        // Mandamos undefined y filtramos en frontend con TYPE_MAP.
        const res = await fetchInventoryMovements({
          skip,
          limit,
          variant_id: variantId.trim() ? variantId.trim() : undefined,
        });

        console.log("[InventoryHistory] RAW response:", res);
        console.log("[InventoryHistory] movements length:", res?.movements?.length);

        // Ver primeros 3 movimientos completos
        console.log("[InventoryHistory] first 3 movements:", (res?.movements ?? []).slice(0, 3));

        // Ver SOLO campos clave (stock_before/after y nombres)
        console.table(
          (res?.movements ?? []).slice(0, 10).map((m: any) => ({
            id: m._id,
            type: m.movement_type,
            qty: m.quantity,
            before: m.stock_before,
            after: m.stock_after,
            product: m.product_name,
            variantName: m.variant_name,
            actor: m.actor_name,
            created: m.creado_en,
            reason: m.reason,
          }))
        );

        setMovements(res.movements ?? []);
      } catch (err) {
        console.error(err);
        setMovements([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [skip, limit, variantId]);

  // Lista de productos para el Select
  const products = useMemo(() => {
    const names = (movements ?? [])
      .map((m) => (m.product_name ?? "").trim())
      .filter(Boolean);
    return Array.from(new Set(names)).sort((a, b) => a.localeCompare(b));
  }, [movements]);

  // Filtrado total
  const filteredHistory = useMemo(() => {
    const allowedTypes = TYPE_MAP[typeFilter];

    return (movements ?? []).filter((m) => {
      // tipo
      const matchesType = !allowedTypes ? true : allowedTypes.includes(m.movement_type);

      // producto
      const matchesProduct =
        productFilter === "all" ? true : (m.product_name ?? "") === productFilter;

      // búsqueda
      const q = searchQuery.trim().toLowerCase();
      const matchesSearch = !q
        ? true
        : (
            (m.product_name ?? "").toLowerCase().includes(q) ||
            (m.variant_id ?? "").toLowerCase().includes(q) ||
            (m.reason ?? "").toLowerCase().includes(q) ||
            (m.actor_name ?? "Pisos Kermy").toLowerCase().includes(q)
          );

      // fechas (usa creado_en)
      const mDate = toISODateOnly(m.creado_en);
      const matchesDateFrom = dateFrom ? mDate >= dateFrom : true;
      const matchesDateTo = dateTo ? mDate <= dateTo : true;

      return matchesType && matchesProduct && matchesSearch && matchesDateFrom && matchesDateTo;
    });
  }, [movements, typeFilter, productFilter, searchQuery, dateFrom, dateTo]);

  // Stats (sobre filteredHistory o sobre movements; aquí uso filteredHistory)
  const stats = useMemo(() => {
    const allowedEntrada = TYPE_MAP["entrada"] ?? [];
    const allowedSalida = TYPE_MAP["salida"] ?? [];
    const allowedAjuste = TYPE_MAP["ajuste"] ?? [];
    const allowedReserva = TYPE_MAP["reserva"] ?? [];

    const total = filteredHistory.length;
    const entradas = filteredHistory.filter((m) => allowedEntrada.includes(m.movement_type)).length;
    const salidas = filteredHistory.filter((m) => allowedSalida.includes(m.movement_type)).length;
    const ajustes = filteredHistory.filter((m) => allowedAjuste.includes(m.movement_type)).length;
    const reservas = filteredHistory.filter((m) => allowedReserva.includes(m.movement_type)).length;

    return { total, entradas, salidas, ajustes, reservas };
  }, [filteredHistory]);

  const handleExport = () => {
    const csvRows: string[][] = [
      ["Fecha", "Producto", "Variante", "Tipo", "Cantidad", "Stock Anterior", "Stock Nuevo", "Razón", "Usuario"],
      ...filteredHistory.map((m) => {
        const cfg = typeConfig[m.movement_type] ?? { label: m.movement_type };

        return [
          formatDate(m.creado_en),
          m.product_name ?? "",
          m.variant_name ?? m.variant_id ?? "",
          cfg.label,
          String(m.quantity ?? ""),
          String(m.stock_before ?? ""),
          String(m.stock_after ?? ""),
          m.reason ?? "",
          m.actor_name ?? "Pisos Kermy",
        ];
      }),
    ];

    const csvContent = csvRows.map((row) =>
      row.map((cell) => {
        // Escape simple para CSV
        const v = (cell ?? "").toString();
        if (v.includes(",") || v.includes('"') || v.includes("\n")) {
          return `"${v.replace(/"/g, '""')}"`;
        }
        return v;
      }).join(",")
    ).join("\n");

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

          <Button variant="outline" onClick={handleExport} disabled={filteredHistory.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Exportar CSV
          </Button>
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
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
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
                  {products.map((p) => (
                    <SelectItem key={p} value={p}>
                      {p}
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

              <Input
                type="date"
                placeholder="Hasta"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>

            {/* Extra (opcional): filtrar por variantId exacto */}
            <div className="mt-4">
              <Input
                placeholder="Filtrar por Variant ID (opcional)..."
                value={variantId}
                onChange={(e) => setVariantId(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* History Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Movimientos
              {loading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
            </CardTitle>
            <CardDescription>
              Mostrando {filteredHistory.length} de {movements.length} registros
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
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={9} className="h-32 text-center text-muted-foreground">
                      Cargando movimientos...
                    </TableCell>
                  </TableRow>
                ) : filteredHistory.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="h-32 text-center">
                      <div className="flex flex-col items-center gap-2">
                        <History className="h-8 w-8 text-muted-foreground" />
                        <p className="text-muted-foreground">No se encontraron movimientos</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredHistory.map((m) => {
                    const cfg = typeConfig[m.movement_type] ?? {
                      label: m.movement_type,
                      icon: History,
                      color: "secondary",
                    };

                    const Icon = cfg.icon;

                    const qty = typeof m.quantity === "number" ? m.quantity : 0;

                    return (
                      <TableRow key={m._id}>
                        <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                          {formatDate(m.creado_en)}
                        </TableCell>

                        <TableCell className="font-medium max-w-[200px] truncate">
                          {m.product_name ?? "—"}
                        </TableCell>

                        <TableCell className="font-mono text-sm">
                          {m.variant_name ?? m.variant_id}
                        </TableCell>

                        <TableCell>
                          <Badge variant={cfg.color} className="gap-1">
                            <Icon className="h-3 w-3" />
                            {cfg.label}
                          </Badge>
                        </TableCell>

                        <TableCell className="text-center">
                          <span
                            className={
                              qty > 0
                                ? "text-success font-medium"
                                : qty < 0
                                  ? "text-destructive font-medium"
                                  : "text-muted-foreground font-medium"
                            }
                          >
                            {qty > 0 ? "+" : ""}
                            {qty}
                          </span>
                        </TableCell>

                        <TableCell className="text-center text-muted-foreground">
                          {m.stock_before ?? "—"}
                        </TableCell>

                        <TableCell className="text-center font-medium">
                          {m.stock_after ?? "—"}
                        </TableCell>

                        <TableCell className="text-sm max-w-[200px] truncate">
                          {m.reason ?? "—"}
                        </TableCell>

                        <TableCell className="text-sm text-muted-foreground">
                          {m.actor_name ?? "Pisos Kermy"}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>

            {/* Paginación simple (opcional) */}
            <div className="flex items-center justify-between p-4">
              <Button
                variant="outline"
                disabled={skip === 0 || loading}
                onClick={() => setSkip((s) => Math.max(0, s - limit))}
              >
                Anterior
              </Button>

              <p className="text-sm text-muted-foreground">
                Página {Math.floor(skip / limit) + 1}
              </p>

              <Button
                variant="outline"
                disabled={loading || movements.length < limit}
                onClick={() => setSkip((s) => s + limit)}
              >
                Siguiente
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default InventoryHistory;
