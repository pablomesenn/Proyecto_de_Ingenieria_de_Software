import { useState, useEffect } from "react";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, Plus, Trash2, X } from "lucide-react";
import { toast } from "sonner";
import {
  createProduct,
  updateProduct,
  getProductDetail,
  getCategories,
  getTags,
  type CreateProductRequest,
  type UpdateProductRequest,
} from "@/api/products";

interface Variant {
  _id?: string;
  tamano_pieza: string;
  unidad: string;
  precio?: number;
  stock_inicial?: number;
}

const ProductForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(isEditing);

  // Opciones
  const [categories, setCategories] = useState<string[]>([]);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // Form state
  const [nombre, setNombre] = useState("");
  const [descripcionEmbalaje, setDescripcionEmbalaje] = useState("");
  const [imagenUrl, setImagenUrl] = useState("");
  const [categoria, setCategoria] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [estado, setEstado] = useState<"activo" | "inactivo" | "agotado">("activo");
  const [variantes, setVariantes] = useState<Variant[]>([]);

  // Variante nueva
  const [newVariantSize, setNewVariantSize] = useState("");
  const [newVariantUnit, setNewVariantUnit] = useState("m²");
  const [newVariantPrice, setNewVariantPrice] = useState("");
  const [newVariantStock, setNewVariantStock] = useState("");

  useEffect(() => {
    loadOptions();
    if (isEditing && id) {
      loadProduct(id);
    }
  }, [id, isEditing]);

  const loadOptions = async () => {
    try {
      const [categoriesData, tagsData] = await Promise.all([
        getCategories(),
        getTags(),
      ]);
      setCategories(categoriesData.categories);
      setAvailableTags(tagsData.tags);
    } catch (error) {
      console.error("Error cargando opciones:", error);
    }
  };

  const loadProduct = async (productId: string) => {
    try {
      setLoadingData(true);
      const product = await getProductDetail(productId);
      
      setNombre(product.nombre || product.name || "");
      setDescripcionEmbalaje(product.descripcion_embalaje || "");
      setImagenUrl(product.imagen_url || product.image_url || "");
      setCategoria(product.categoria || product.category || "");
      setSelectedTags(product.tags || []);
      setEstado((product.estado as any) || "activo");

      // Cargar variantes
      const variants = (product.variantes || product.variants || []).map((v: any) => ({
        _id: v._id,
        tamano_pieza: v.tamano_pieza || v.size || "",
        unidad: v.unidad || "m²",
        precio: v.precio || 0,
        stock_inicial: 0, // No mostramos stock en edición
      }));
      setVariantes(variants);
    } catch (error) {
      toast.error("Error al cargar el producto");
      console.error(error);
    } finally {
      setLoadingData(false);
    }
  };

  const toggleTag = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId]
    );
  };

  const addVariant = () => {
    if (!newVariantSize.trim()) {
      toast.error("Ingresa el tamaño de la variante");
      return;
    }

    const newVariant: Variant = {
      tamano_pieza: newVariantSize,
      unidad: newVariantUnit,
      precio: newVariantPrice ? parseFloat(newVariantPrice) : undefined,
      stock_inicial: newVariantStock ? parseInt(newVariantStock) : 0,
    };

    setVariantes((prev) => [...prev, newVariant]);
    
    // Limpiar campos
    setNewVariantSize("");
    setNewVariantUnit("m²");
    setNewVariantPrice("");
    setNewVariantStock("");
    
    toast.success("Variante agregada");
  };

  const removeVariant = (index: number) => {
    setVariantes((prev) => prev.filter((_, i) => i !== index));
    toast.success("Variante eliminada");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    if (!nombre.trim()) {
      toast.error("El nombre es requerido");
      return;
    }

    if (!imagenUrl.trim()) {
      toast.error("La imagen es requerida");
      return;
    }

    if (!categoria) {
      toast.error("La categoría es requerida");
      return;
    }

    if (variantes.length === 0) {
      toast.error("Debes agregar al menos una variante");
      return;
    }

    try {
      setLoading(true);

      if (isEditing && id) {
        // Actualizar producto
        const updateData: UpdateProductRequest = {
          nombre,
          imagen_url: imagenUrl,
          categoria,
          tags: selectedTags,
          estado,
          descripcion_embalaje: descripcionEmbalaje || undefined,
          variantes: variantes.map(v => ({
            _id: v._id,
            tamano_pieza: v.tamano_pieza,
            unidad: v.unidad,
            precio: v.precio,
          })),
        };

        console.log("Actualizando producto:", updateData);
        const result = await updateProduct(id, updateData);
        console.log("Resultado actualización:", result);
        toast.success("Producto actualizado correctamente");
      } else {
        // Crear producto
        const createData: CreateProductRequest = {
          nombre,
          imagen_url: imagenUrl,
          categoria,
          tags: selectedTags,
          estado,
          descripcion_embalaje: descripcionEmbalaje || undefined,
          variantes: variantes.map(v => ({
            tamano_pieza: v.tamano_pieza,
            unidad: v.unidad,
            precio: v.precio,
            stock_inicial: v.stock_inicial || 0,
          })),
        };

        console.log("Creando producto:", createData);
        const result = await createProduct(createData);
        console.log("Resultado creación:", result);
        toast.success("Producto creado correctamente");
      }

      navigate("/admin/products");
    } catch (error: any) {
      console.error("Error en handleSubmit:", error);
      toast.error(error.message || "Error al guardar el producto");
    } finally {
      setLoading(false);
    }
  };

  if (loadingData) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <p>Cargando producto...</p>
        </div>
      </AdminLayout>
    );
  }

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
            <Button type="submit" disabled={loading}>
              {loading ? "Guardando..." : isEditing ? "Guardar Cambios" : "Crear Producto"}
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
                  <Label htmlFor="nombre">Nombre del Producto *</Label>
                  <Input
                    id="nombre"
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                    placeholder="Ej: Porcelanato Terrazo Blanco"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="descripcion">Descripción / Embalaje</Label>
                  <Textarea
                    id="descripcion"
                    value={descripcionEmbalaje}
                    onChange={(e) => setDescripcionEmbalaje(e.target.value)}
                    placeholder="Describe las características del producto o información del embalaje..."
                    rows={4}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="imagen">URL de Imagen *</Label>
                  <Input
                    id="imagen"
                    value={imagenUrl}
                    onChange={(e) => setImagenUrl(e.target.value)}
                    placeholder="https://ejemplo.com/imagen.jpg"
                    required
                  />
                  {imagenUrl && (
                    <img 
                      src={imagenUrl} 
                      alt="Preview" 
                      className="w-32 h-32 object-cover rounded mt-2"
                      onError={(e) => {
                        e.currentTarget.src = "https://placehold.co/150x150/e2e8f0/64748b?text=Sin+Imagen";
                      }}
                    />
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Variants */}
            <Card>
              <CardHeader>
                <CardTitle>Variantes</CardTitle>
                <CardDescription>Define los tamaños y precios disponibles</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Add variant form */}
                <div className="grid grid-cols-12 gap-2">
                  <div className="col-span-4">
                    <Input
                      placeholder="Tamaño (ej: 60x60)"
                      value={newVariantSize}
                      onChange={(e) => setNewVariantSize(e.target.value)}
                    />
                  </div>
                  <div className="col-span-2">
                    <Select value={newVariantUnit} onValueChange={setNewVariantUnit}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="m²">m²</SelectItem>
                        <SelectItem value="cm">cm</SelectItem>
                        <SelectItem value="pz">pz</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      placeholder="Precio"
                      value={newVariantPrice}
                      onChange={(e) => setNewVariantPrice(e.target.value)}
                    />
                  </div>
                  {!isEditing && (
                    <div className="col-span-2">
                      <Input
                        type="number"
                        placeholder="Stock"
                        value={newVariantStock}
                        onChange={(e) => setNewVariantStock(e.target.value)}
                      />
                    </div>
                  )}
                  <div className={isEditing ? "col-span-4" : "col-span-2"}>
                    <Button type="button" onClick={addVariant} className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Agregar
                    </Button>
                  </div>
                </div>

                {/* Variants table */}
                {variantes.length > 0 && (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Tamaño</TableHead>
                        <TableHead>Unidad</TableHead>
                        <TableHead>Precio</TableHead>
                        {!isEditing && <TableHead>Stock Inicial</TableHead>}
                        <TableHead className="w-[50px]"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {variantes.map((variant, index) => (
                        <TableRow key={index}>
                          <TableCell>{variant.tamano_pieza}</TableCell>
                          <TableCell>{variant.unidad}</TableCell>
                          <TableCell>${variant.precio?.toFixed(2) || "0.00"}</TableCell>
                          {!isEditing && <TableCell>{variant.stock_inicial || 0}</TableCell>}
                          <TableCell>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => removeVariant(index)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}

                {variantes.length === 0 && (
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
                <CardTitle>Estado</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Estado del Producto</Label>
                  <Select 
                    value={estado} 
                    onValueChange={(v) => setEstado(v as "activo" | "inactivo" | "agotado")}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="activo">Activo</SelectItem>
                      <SelectItem value="inactivo">Inactivo</SelectItem>
                      <SelectItem value="agotado">Agotado</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Category */}
            <Card>
              <CardHeader>
                <CardTitle>Categoría *</CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={categoria} onValueChange={setCategoria} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona una categoría" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {cat}
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
                      key={tag}
                      variant={selectedTags.includes(tag) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleTag(tag)}
                    >
                      {tag}
                      {selectedTags.includes(tag) && <X className="h-3 w-3 ml-1" />}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </AdminLayout>
  );
};

export default ProductForm;