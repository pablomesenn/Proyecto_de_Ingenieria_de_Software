import { useState } from "react";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { FileDown, FileSpreadsheet, Table } from "lucide-react";
import { toast } from "sonner";

const Export = () => {
  const [format, setFormat] = useState<"csv" | "excel">("excel");
  const [includeImages, setIncludeImages] = useState(false);
  const [includeStock, setIncludeStock] = useState(true);
  const [includeInactive, setIncludeInactive] = useState(false);

  const handleExport = () => {
    toast.success(`Exportando catálogo en formato ${format.toUpperCase()}...`);
  };

  return (
    <AdminLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-2xl font-display font-bold">Exportar Catálogo</h1>
          <p className="text-muted-foreground">Descarga el catálogo de productos en formato CSV o Excel</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Formato de Exportación</CardTitle>
            <CardDescription>Selecciona el formato del archivo</CardDescription>
          </CardHeader>
          <CardContent>
            <RadioGroup value={format} onValueChange={(v) => setFormat(v as "csv" | "excel")}>
              <div className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-muted/50" onClick={() => setFormat("excel")}>
                <RadioGroupItem value="excel" id="excel" />
                <FileSpreadsheet className="h-5 w-5 text-success" />
                <Label htmlFor="excel" className="cursor-pointer flex-1">
                  <p className="font-medium">Excel (.xlsx)</p>
                  <p className="text-sm text-muted-foreground">Formato completo con múltiples hojas</p>
                </Label>
              </div>
              <div className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-muted/50 mt-2" onClick={() => setFormat("csv")}>
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

        <Card>
          <CardHeader>
            <CardTitle>Opciones de Exportación</CardTitle>
            <CardDescription>Personaliza qué datos incluir</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-3">
              <Checkbox id="stock" checked={includeStock} onCheckedChange={(c) => setIncludeStock(c === true)} />
              <Label htmlFor="stock" className="cursor-pointer">Incluir información de stock</Label>
            </div>
            <div className="flex items-center space-x-3">
              <Checkbox id="images" checked={includeImages} onCheckedChange={(c) => setIncludeImages(c === true)} />
              <Label htmlFor="images" className="cursor-pointer">Incluir URLs de imágenes</Label>
            </div>
            <div className="flex items-center space-x-3">
              <Checkbox id="inactive" checked={includeInactive} onCheckedChange={(c) => setIncludeInactive(c === true)} />
              <Label htmlFor="inactive" className="cursor-pointer">Incluir productos inactivos</Label>
            </div>
          </CardContent>
        </Card>

        <Button size="lg" className="w-full" onClick={handleExport}>
          <FileDown className="h-5 w-5 mr-2" />
          Exportar Catálogo
        </Button>
      </div>
    </AdminLayout>
  );
};

export default Export;
