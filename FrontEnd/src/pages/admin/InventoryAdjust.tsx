import { useState, useEffect } from "react";
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
import { getProducts, Product, ProductVariant } from "@/api/products";
import { adjustInventory, getInventoryByVariant } from "@/api/inventory";

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
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [selectedVariant, setSelectedVariant] = useState<string>("");
  const [adjustmentType, setAdjustmentType] = useState<"add" | "subtract">("add");
  const [quantity, setQuantity] = useState<number>(0);
  const [reason, setReason] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [variantStock, setVariantStock] = useState<number>(0);
  const [variantSize, setVariantSize] = useState<string>("");
  const [variantStockMap, setVariantStockMap] = useState<Record<string, number>>({}); // Guardar stock de cada variante

  // Cargar productos al montar el componente
  useEffect(() => {
    const loadProducts = async () => {
      try {
        setLoading(true);
        const result = await getProducts(0, 100);
        
        // Transformar productos para que coincidan con la estructura esperada
        const transformedProducts = result.products.map((product: Product) => ({
          id: product._id,
          name: product.nombre || product.name,
          variants: (product.variantes || product.variants || []).map((variant: ProductVariant) => ({
            id: variant._id,
            size: variant.size || (variant as any).tamano_pieza || "",
            currentStock:
              (variant as any).stock_total ??
              (variant as any).stock_disponible ??
              (variant as any).disponibilidad ??
              variant.stock ??
              0,
          })),
        }));
        
        setProducts(transformedProducts);
      } catch (error) {
        console.error("Error cargando productos:", error);
        toast.error("Error al cargar los productos");
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  const product = products.find((p) => p.id === selectedProduct);
  const variant = product?.variants.find((v: any) => v.id === selectedVariant);
  const newStock = adjustmentType === "add"
    ? variantStock + quantity
    : Math.max(0, variantStock - quantity);

  // Cargar stock de todas las variantes cuando se selecciona un producto
  const handleProductChange = async (productId: string) => {
    setSelectedProduct(productId);
    setSelectedVariant("");
    setVariantSize("");
    setVariantStock(0);
    setVariantStockMap({});

    const selectedProd = products.find((p) => p.id === productId);
    if (!selectedProd) return;

    // Cargar stock total para cada variante del producto
    const stockMap: Record<string, number> = {};
    for (const variant of selectedProd.variants) {
      try {
        const inventory = await getInventoryByVariant(variant.id);
        stockMap[variant.id] = inventory.stock_total ?? 0;
      } catch (error) {
        console.error(`Error cargando stock para variante ${variant.id}:`, error);
        stockMap[variant.id] = 0;
      }
    }
    setVariantStockMap(stockMap);
  };

  const handleVariantChange = async (value: string) => {
    setSelectedVariant(value);

    const v = product?.variants.find((item: any) => item.id === value);
    setVariantSize(v?.size || v?.tamano_pieza || "");
    
    // Usar el stock del mapa (ya cargado previamente)
    const stockFromMap = variantStockMap[value];
    if (stockFromMap !== undefined) {
      setVariantStock(stockFromMap);
      console.log("Stock obtenido del mapa para variante:", value, "Stock total:", stockFromMap);
    } else {
      // Si no está en el mapa, cargar de la API
      try {
        const inventory = await getInventoryByVariant(value);
        const resolvedStock = inventory.stock_total ?? 0;
        setVariantStock(resolvedStock);
        setVariantStockMap(prev => ({ ...prev, [value]: resolvedStock }));
        console.log("Stock obtenido de API para variante:", value, "Stock total:", resolvedStock);
      } catch (error) {
        console.error("Error obteniendo inventario de variante:", error);
        toast.error("No se pudo obtener el stock de la variante");
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProduct || !selectedVariant || !quantity || !reason) {
      toast.error("Por favor completa todos los campos requeridos");
      return;
    }

    try {
      setSubmitting(true);
      const delta = adjustmentType === "add" ? quantity : -quantity;
      
      console.log("Ajustando inventario:", {
        variantId: selectedVariant,
        delta,
        reason,
        currentStock: variantStock
      });
      
      const result = await adjustInventory(selectedVariant, delta, reason);
      
      console.log("Ajuste exitoso:", result);
      
      toast.success("Ajuste de inventario registrado correctamente");
      navigate("/admin/inventory");
    } catch (error: any) {
      console.error("Error ajustando inventario:", error);
      const errorMessage = error.response?.data?.error || error.message || "Error al ajustar el inventario";
      toast.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AdminLayout>
      {loading ? (
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Cargando productos...</p>
        </div>
      ) : (
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
                    onValueChange={handleProductChange}
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
                    <Select value={selectedVariant} onValueChange={handleVariantChange}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona una variante" />
                      </SelectTrigger>
                      <SelectContent>
                        {product.variants.map((variant) => {
                          const displayStock = variantStockMap[variant.id] ?? 0;
                          return (
                            <SelectItem key={variant.id} value={variant.id}>
                              {variant.size || variant.tamano_pieza || "Variante"} (Stock total: {displayStock})
                            </SelectItem>
                          );
                        })}
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
                        <span className="font-medium">{variantSize || variant?.size || ""}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Stock Actual:</span>
                        <div className="text-right">
                          <span className="font-medium text-lg">{variantStock}</span>
                          <p className="text-xs text-muted-foreground">(Total incluyendo reservados)</p>
                        </div>
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

                    {adjustmentType === "subtract" && quantity > variantStock && (
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
                disabled={!selectedProduct || !selectedVariant || !quantity || !reason || submitting}
              >
                {submitting ? "Procesando..." : "Confirmar Ajuste"}
              </Button>
            </div>
          </div>
        </div>
        </form>
      )}
    </AdminLayout>
  );
};

export default InventoryAdjust;
