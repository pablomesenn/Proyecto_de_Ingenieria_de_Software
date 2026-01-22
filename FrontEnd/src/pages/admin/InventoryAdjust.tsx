import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft, Plus, Minus, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

// Mock data
const products = [
  {
    id: "1",
    name: "Porcelanato Terrazo Blanco",
    variants: [
      { id: "1a", size: "60x60", currentStock: 120 },
      { id: "1b", size: "80x80", currentStock: 85 },
      { id: "1c", size: "120x60", currentStock: 40 },
    ],
  },
  {
    id: "2",
    name: "Mármol Calacatta Gold",
    variants: [
      { id: "2a", size: "60x120", currentStock: 45 },
      { id: "2b", size: "80x160", currentStock: 2 },
    ],
  },
  {
    id: "3",
    name: "Cerámica Rústica Terracota",
    variants: [
      { id: "3a", size: "30x30", currentStock: 0 },
      { id: "3b", size: "45x45", currentStock: 0 },
    ],
  },
  {
    id: "4",
    name: "Granito Negro Galaxy",
    variants: [
      { id: "4a", size: "60x60", currentStock: 156 },
      { id: "4b", size: "80x80", currentStock: 89 },
    ],
  },
  {
    id: "5",
    name: "Cerámica Subway Blanca",
    variants: [
      { id: "5a", size: "7.5x15", currentStock: 320 },
      { id: "5b", size: "10x20", currentStock: 8 },
    ],
  },
];

const adjustmentReasons = [
  { id: "reception", label: "Recepción de proveedor" },
  { id: "sale", label: "Venta completada" },
  { id: "return", label: "Devolución de cliente" },
  { id: "damage", label: "Producto dañado" },
  { id: "correction", label: "Corrección de inventario" },
  { id: "loss", label: "Pérdida/Robo" },
  { id: "other", label: "Otro" },
];

const InventoryAdjust = () => {
  const navigate = useNavigate();
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [selectedVariant, setSelectedVariant] = useState<string>("");
  const [adjustmentType, setAdjustmentType] = useState<"add" | "subtract">("add");
  const [quantity, setQuantity] = useState<number>(0);
  const [reason, setReason] = useState<string>("");
  const [notes, setNotes] = useState<string>("");

  const product = products.find((p) => p.id === selectedProduct);
  const variant = product?.variants.find((v) => v.id === selectedVariant);
  const newStock = variant
    ? adjustmentType === "add"
      ? variant.currentStock + quantity
      : Math.max(0, variant.currentStock - quantity)
    : 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProduct || !selectedVariant || !quantity || !reason) {
      toast.error("Por favor completa todos los campos requeridos");
      return;
    }

    // In a real app, this would save to the backend
    toast.success("Ajuste de inventario registrado correctamente");
    navigate("/admin/inventory");
  };

  return (
    <AdminLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button type="button" variant="ghost" size="icon" asChild>
            <Link to="/admin/inventory">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-display font-bold">Ajustar Inventario</h1>
            <p className="text-muted-foreground">Registra entradas, salidas o correcciones de stock</p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Form */}
          <div className="space-y-6">
            {/* Product Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Seleccionar Producto</CardTitle>
                <CardDescription>Elige el producto y la variante a ajustar</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Producto *</Label>
                  <Select
                    value={selectedProduct}
                    onValueChange={(value) => {
                      setSelectedProduct(value);
                      setSelectedVariant("");
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona un producto" />
                    </SelectTrigger>
                    <SelectContent>
                      {products.map((product) => (
                        <SelectItem key={product.id} value={product.id}>
                          {product.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {product && (
                  <div className="space-y-2">
                    <Label>Variante (Tamaño) *</Label>
                    <Select value={selectedVariant} onValueChange={setSelectedVariant}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona una variante" />
                      </SelectTrigger>
                      <SelectContent>
                        {product.variants.map((variant) => (
                          <SelectItem key={variant.id} value={variant.id}>
                            {variant.size} cm (Stock actual: {variant.currentStock})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Adjustment Details */}
            <Card>
              <CardHeader>
                <CardTitle>Detalles del Ajuste</CardTitle>
                <CardDescription>Especifica el tipo y cantidad del ajuste</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Tipo de Ajuste</Label>
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      type="button"
                      variant={adjustmentType === "add" ? "default" : "outline"}
                      className="h-auto py-4"
                      onClick={() => setAdjustmentType("add")}
                    >
                      <Plus className="h-5 w-5 mr-2" />
                      <div className="text-left">
                        <p className="font-medium">Entrada</p>
                        <p className="text-xs opacity-70">Agregar stock</p>
                      </div>
                    </Button>
                    <Button
                      type="button"
                      variant={adjustmentType === "subtract" ? "destructive" : "outline"}
                      className="h-auto py-4"
                      onClick={() => setAdjustmentType("subtract")}
                    >
                      <Minus className="h-5 w-5 mr-2" />
                      <div className="text-left">
                        <p className="font-medium">Salida</p>
                        <p className="text-xs opacity-70">Reducir stock</p>
                      </div>
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="quantity">Cantidad *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    min="1"
                    value={quantity || ""}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
                    placeholder="0"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Razón del Ajuste *</Label>
                  <Select value={reason} onValueChange={setReason}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona una razón" />
                    </SelectTrigger>
                    <SelectContent>
                      {adjustmentReasons.map((r) => (
                        <SelectItem key={r.id} value={r.id}>
                          {r.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Notas Adicionales</Label>
                  <Textarea
                    id="notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Información adicional sobre el ajuste..."
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Summary */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Resumen del Ajuste</CardTitle>
                <CardDescription>Confirma los detalles antes de guardar</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {variant ? (
                  <>
                    <div className="p-4 rounded-lg bg-muted space-y-3">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Producto:</span>
                        <span className="font-medium">{product?.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Variante:</span>
                        <span className="font-medium">{variant.size} cm</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Stock Actual:</span>
                        <span className="font-medium">{variant.currentStock}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Ajuste:</span>
                        <span
                          className={`font-medium ${
                            adjustmentType === "add" ? "text-success" : "text-destructive"
                          }`}
                        >
                          {adjustmentType === "add" ? "+" : "-"}
                          {quantity}
                        </span>
                      </div>
                      <div className="border-t pt-3 flex justify-between">
                        <span className="font-medium">Nuevo Stock:</span>
                        <span className="text-xl font-bold">{newStock}</span>
                      </div>
                    </div>

                    {adjustmentType === "subtract" && quantity > variant.currentStock && (
                      <div className="p-4 rounded-lg border border-warning/50 bg-warning/5 flex gap-3">
                        <AlertTriangle className="h-5 w-5 text-warning flex-shrink-0" />
                        <div className="text-sm">
                          <p className="font-medium text-warning">Advertencia</p>
                          <p className="text-muted-foreground">
                            La cantidad a reducir es mayor al stock actual. El stock quedará en 0.
                          </p>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    Selecciona un producto y variante para ver el resumen
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="flex gap-2">
              <Button type="button" variant="outline" className="flex-1" asChild>
                <Link to="/admin/inventory">Cancelar</Link>
              </Button>
              <Button
                type="submit"
                className="flex-1"
                disabled={!selectedProduct || !selectedVariant || !quantity || !reason}
              >
                Confirmar Ajuste
              </Button>
            </div>
          </div>
        </div>
      </form>
    </AdminLayout>
  );
};

export default InventoryAdjust;
