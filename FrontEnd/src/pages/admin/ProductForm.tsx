import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, Plus, Trash2, Upload, X, Minus } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// Mock data
const categories = [
  { id: "porcelanato", name: "Porcelanato" },
  { id: "ceramica", name: "Cerámica" },
  { id: "marmol", name: "Mármol" },
  { id: "granito", name: "Granito" },
  { id: "madera", name: "Madera" },
];

const availableTags = [
  { id: "interior", name: "Interior" },
  { id: "exterior", name: "Exterior" },
  { id: "antideslizante", name: "Antideslizante" },
  { id: "premium", name: "Premium" },
  { id: "rustico", name: "Rústico" },
  { id: "moderno", name: "Moderno" },
];

interface Variant {
  id: string;
  size: string;
  stock: number;
  reserved: number;
}

const ProductForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  // Form state
  const [name, setName] = useState(isEditing ? "Porcelanato Terrazo Blanco" : "");
  const [description, setDescription] = useState(
    isEditing ? "Elegante porcelanato con efecto terrazo, ideal para espacios modernos." : ""
  );
  const [category, setCategory] = useState(isEditing ? "porcelanato" : "");
  const [selectedTags, setSelectedTags] = useState<string[]>(isEditing ? ["interior", "moderno"] : []);
  const [status, setStatus] = useState<"active" | "inactive">(isEditing ? "active" : "active");
  const [isVisible, setIsVisible] = useState(true);
  const [variants, setVariants] = useState<Variant[]>(
    isEditing
      ? [
          { id: "1", size: "60x60", stock: 120, reserved: 15 },
          { id: "2", size: "80x80", stock: 85, reserved: 8 },
          { id: "3", size: "120x60", stock: 40, reserved: 5 },
        ]
      : []
  );
  const [newVariantSize, setNewVariantSize] = useState("");
  
  // Stock adjustment state
  const [adjustDialogOpen, setAdjustDialogOpen] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState<Variant | null>(null);
  const [adjustmentDelta, setAdjustmentDelta] = useState(0);
  const [adjustmentReason, setAdjustmentReason] = useState("");

  const toggleTag = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId]
    );
  };

  const addVariant = () => {
    if (!newVariantSize.trim()) return;
    setVariants((prev) => [
      ...prev,
      { id: Date.now().toString(), size: newVariantSize, stock: 0, reserved: 0 },
    ]);
    setNewVariantSize("");
  };

  const removeVariant = (variantId: string) => {
    setVariants((prev) => prev.filter((v) => v.id !== variantId));
  };

  const openAdjustDialog = (variant: Variant) => {
    setSelectedVariant(variant);
    setAdjustmentDelta(0);
    setAdjustmentReason("");
    setAdjustDialogOpen(true);
  };

  const handleStockAdjustment = () => {
    if (!selectedVariant || adjustmentDelta === 0) return;
    
    setVariants((prev) =>
      prev.map((v) =>
        v.id === selectedVariant.id
          ? { ...v, stock: Math.max(0, v.stock + adjustmentDelta) }
          : v
      )
    );
    
    toast.success(
      `Stock ${adjustmentDelta > 0 ? "aumentado" : "reducido"} en ${Math.abs(adjustmentDelta)} unidades`
    );
    setAdjustDialogOpen(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would save to the backend
    toast.success(isEditing ? "Producto actualizado correctamente" : "Producto creado correctamente");
    navigate("/admin/products");
  };

  return (
    <AdminLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button type="button" variant="ghost" size="icon" asChild>
            <Link to="/admin/products">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-display font-bold">
              {isEditing ? "Editar Producto" : "Nuevo Producto"}
            </h1>
            <p className="text-muted-foreground">
              {isEditing ? "Modifica los datos del producto" : "Completa el formulario para crear un nuevo producto"}
            </p>
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="outline" asChild>
              <Link to="/admin/products">Cancelar</Link>
            </Button>
            <Button type="submit">
              {isEditing ? "Guardar Cambios" : "Crear Producto"}
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <Card>
              <CardHeader>
                <CardTitle>Información Básica</CardTitle>
                <CardDescription>Datos principales del producto</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nombre del Producto *</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Ej: Porcelanato Terrazo Blanco"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Descripción</Label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe las características del producto..."
                    rows={4}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Image Upload */}
            <Card>
              <CardHeader>
                <CardTitle>Imagen del Producto</CardTitle>
                <CardDescription>Sube una imagen representativa</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer">
                  <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Arrastra una imagen o haz clic para seleccionar
                  </p>
                  <p className="text-xs text-muted-foreground">PNG, JPG hasta 5MB</p>
                  <Input type="file" className="hidden" accept="image/*" />
                </div>
                {isEditing && (
                  <div className="mt-4">
                    <img
                      src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
                      alt="Current product"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Variants */}
            <Card>
              <CardHeader>
                <CardTitle>Variantes de Tamaño</CardTitle>
                <CardDescription>Define las medidas disponibles para este producto</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Add variant */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Ej: 60x60, 80x80"
                    value={newVariantSize}
                    onChange={(e) => setNewVariantSize(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addVariant())}
                  />
                  <Button type="button" onClick={addVariant}>
                    <Plus className="h-4 w-4 mr-2" />
                    Agregar
                  </Button>
                </div>

                {/* Variants table */}
                {variants.length > 0 && (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Tamaño (cm)</TableHead>
                        <TableHead className="text-center">Stock Total</TableHead>
                        <TableHead className="text-center">Reservado</TableHead>
                        <TableHead className="text-center">Disponible</TableHead>
                        <TableHead className="text-center">Ajustar</TableHead>
                        <TableHead className="w-[50px]"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {variants.map((variant) => (
                        <TableRow key={variant.id}>
                          <TableCell className="font-medium">{variant.size}</TableCell>
                          <TableCell className="text-center">{variant.stock}</TableCell>
                          <TableCell className="text-center">{variant.reserved}</TableCell>
                          <TableCell className="text-center">
                            <Badge
                              variant={
                                variant.stock - variant.reserved === 0
                                  ? "destructive"
                                  : variant.stock - variant.reserved < 20
                                  ? "warning"
                                  : "success"
                              }
                            >
                              {variant.stock - variant.reserved}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-center">
                            <div className="flex items-center justify-center gap-1">
                              <Button
                                type="button"
                                variant="outline"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => {
                                  setSelectedVariant(variant);
                                  setAdjustmentDelta(-1);
                                  setAdjustmentReason("");
                                  setAdjustDialogOpen(true);
                                }}
                              >
                                <Minus className="h-3 w-3" />
                              </Button>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                className="h-7 px-2 text-xs"
                                onClick={() => openAdjustDialog(variant)}
                              >
                                Ajustar
                              </Button>
                              <Button
                                type="button"
                                variant="outline"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => {
                                  setSelectedVariant(variant);
                                  setAdjustmentDelta(1);
                                  setAdjustmentReason("");
                                  setAdjustDialogOpen(true);
                                }}
                              >
                                <Plus className="h-3 w-3" />
                              </Button>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => removeVariant(variant.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}

                {variants.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No hay variantes definidas. Agrega al menos una variante.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Status */}
            <Card>
              <CardHeader>
                <CardTitle>Estado y Visibilidad</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Estado del Producto</Label>
                  <Select value={status} onValueChange={(v) => setStatus(v as "active" | "inactive")}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Activo</SelectItem>
                      <SelectItem value="inactive">Inactivo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Visible en Catálogo</Label>
                    <p className="text-xs text-muted-foreground">
                      Mostrar este producto a los clientes
                    </p>
                  </div>
                  <Switch checked={isVisible} onCheckedChange={setIsVisible} />
                </div>
              </CardContent>
            </Card>

            {/* Category */}
            <Card>
              <CardHeader>
                <CardTitle>Categoría</CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona una categoría" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Tags */}
            <Card>
              <CardHeader>
                <CardTitle>Etiquetas</CardTitle>
                <CardDescription>Selecciona las etiquetas aplicables</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {availableTags.map((tag) => (
                    <Badge
                      key={tag.id}
                      variant={selectedTags.includes(tag.id) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleTag(tag.id)}
                    >
                      {tag.name}
                      {selectedTags.includes(tag.id) && <X className="h-3 w-3 ml-1" />}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>

      {/* Stock Adjustment Dialog */}
      <Dialog open={adjustDialogOpen} onOpenChange={setAdjustDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Ajustar Stock</DialogTitle>
            <DialogDescription>
              {selectedVariant && (
                <>Variante: <strong>{selectedVariant.size}</strong> - Stock actual: <strong>{selectedVariant.stock}</strong></>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Cantidad a ajustar</Label>
              <div className="flex items-center gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => setAdjustmentDelta((prev) => prev - 1)}
                >
                  <Minus className="h-4 w-4" />
                </Button>
                <Input
                  type="number"
                  value={adjustmentDelta}
                  onChange={(e) => setAdjustmentDelta(parseInt(e.target.value) || 0)}
                  className="text-center w-24"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => setAdjustmentDelta((prev) => prev + 1)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {selectedVariant && (
                <p className="text-sm text-muted-foreground">
                  Nuevo stock: <strong>{Math.max(0, selectedVariant.stock + adjustmentDelta)}</strong>
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Razón del ajuste</Label>
              <Select value={adjustmentReason} onValueChange={setAdjustmentReason}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona una razón" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="purchase">Compra / Entrada de mercancía</SelectItem>
                  <SelectItem value="sale">Venta directa</SelectItem>
                  <SelectItem value="return">Devolución</SelectItem>
                  <SelectItem value="damage">Daño / Pérdida</SelectItem>
                  <SelectItem value="correction">Corrección de inventario</SelectItem>
                  <SelectItem value="other">Otro</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setAdjustDialogOpen(false)}>
              Cancelar
            </Button>
            <Button
              type="button"
              onClick={handleStockAdjustment}
              disabled={adjustmentDelta === 0}
            >
              Confirmar Ajuste
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
};

export default ProductForm;
