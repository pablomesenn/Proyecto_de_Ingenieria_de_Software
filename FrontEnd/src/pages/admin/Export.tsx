import { useState } from "react";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FileDown, FileSpreadsheet, Table, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { exportReservations } from "@/api/reservations";

const Export = () => {
  // Formato correcto para backend: "xlsx" | "csv"
  const [format, setFormat] = useState<"xlsx" | "csv">("xlsx");

  // Filtros del CU-19
  const [state, setState] = useState<string>("all"); // "all" = sin filtro
  const [dateFrom, setDateFrom] = useState<string>(""); // YYYY-MM-DD
  const [dateTo, setDateTo] = useState<string>("");     // YYYY-MM-DD

  // Checkboxes (no aplican a reservas, pero los dejamos para no romper la UI)
  const [includeStock, setIncludeStock] = useState(false);
  const [includeImages, setIncludeImages] = useState(false);
  const [includeInactive, setIncludeInactive] = useState(false);

  const [loading, setLoading] = useState(false);

  const onExport = async () => {
    try {
      setLoading(true);

      // Validación simple de fechas
      if (dateFrom && dateTo && dateFrom > dateTo) {
        toast.error("El rango de fechas no es válido: 'Desde' no puede ser mayor que 'Hasta'.");
        return;
      }

      await exportReservations({
        format,
        state: state === "all" ? undefined : state,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      });

      toast.success(`Exportación generada (${format.toUpperCase()}).`);
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message ?? "No se pudo exportar. Revise consola/servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-2xl font-display font-bold">Exportar Reservas</h1>
          <p className="text-muted-foreground">
            Descarga las reservas en formato CSV o Excel (con filtros opcionales)
          </p>
        </div>

        {/* Formato */}
        <Card>
          <CardHeader>
            <CardTitle>Formato de Exportación</CardTitle>
            <CardDescription>Selecciona el formato del archivo</CardDescription>
          </CardHeader>
          <CardContent>
            <RadioGroup
              value={format}
              onValueChange={(v) => setFormat(v as "xlsx" | "csv")}
            >
              <div
                className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-muted/50"
                onClick={() => setFormat("xlsx")}
              >
                <RadioGroupItem value="xlsx" id="xlsx" />
                <FileSpreadsheet className="h-5 w-5 text-success" />
                <Label htmlFor="xlsx" className="cursor-pointer flex-1">
                  <p className="font-medium">Excel (.xlsx)</p>
                  <p className="text-sm text-muted-foreground">Formato completo con múltiples hojas</p>
                </Label>
              </div>

              <div
                className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-muted/50 mt-2"
                onClick={() => setFormat("csv")}
              >
                <RadioGroupItem value="csv" id="csv" />
                <Table className="h-5 w-5 text-primary" />
                <Label htmlFor="csv" className="cursor-pointer flex-1">
                  <p className="font-medium">CSV (.csv)</p>
                  <p className="text-sm text-muted-foreground">Formato simple, compatible con cualquier sistema</p>
                </Label>
              </div>
            </RadioGroup>
          </CardContent>
        </Card>

        {/* Filtros de reservas (CU-19) */}
        <Card>
          <CardHeader>
            <CardTitle>Filtros</CardTitle>
            <CardDescription>Filtra por estado y/o rango de fechas</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label>Estado</Label>
              <Select value={state} onValueChange={setState}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  {/* Ajusta estos valores a los que use tu backend */}
                  <SelectItem value="Pendiente">Pendiente</SelectItem>
                  <SelectItem value="Aprobada">Aprobada</SelectItem>
                  <SelectItem value="Rechazada">Rechazada</SelectItem>
                  <SelectItem value="Cancelada">Cancelada</SelectItem>
                  <SelectItem value="Expirada">Expirada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Desde</Label>
              <Input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Hasta</Label>
              <Input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Button size="lg" className="w-full" onClick={onExport} disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Exportando...
            </>
          ) : (
            <>
              <FileDown className="h-5 w-5 mr-2" />
              Exportar Reservas
            </>
          )}
        </Button>
      </div>
    </AdminLayout>
  );
};

export default Export;
