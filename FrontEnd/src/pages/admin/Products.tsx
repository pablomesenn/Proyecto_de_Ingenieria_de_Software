import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Plus,
  Search,
  MoreHorizontal,
  Edit,
  Eye,
  Trash2,
  Package,
  Filter,
} from "lucide-react";
import { toast } from "sonner";
import { getProducts, deleteProduct, type Product } from "@/api/products";

const Products = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await getProducts();
      setProducts(response.products || []);
    } catch (error) {
      console.error("Error cargando productos:", error);
      toast.error("Error al cargar productos");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (productId: string, productName: string) => {
    if (!confirm(`¿Estás seguro de eliminar "${productName}"?`)) {
      return;
    }

    try {
      await deleteProduct(productId);
      toast.success("Producto eliminado correctamente");
      loadProducts(); // Recargar la lista
    } catch (error: any) {
      console.error("Error eliminando producto:", error);
      toast.error(error.message || "Error al eliminar producto");
    }
  };

  // Filtrar productos
  const filteredProducts = products.filter((product) => {
    const matchesSearch = (product.nombre || product.name || "")
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    
    const productEstado = (product.estado || "").toLowerCase();
    const matchesStatus = 
      statusFilter === "all" || 
      productEstado === statusFilter.toLowerCase();
    
    const matchesCategory = 
      categoryFilter === "all" || 
      product.categoria === categoryFilter || 
      product.category === categoryFilter;

    return matchesSearch && matchesStatus && matchesCategory;
  });

  // Obtener categorías únicas
  const categories = Array.from(
    new Set(
      products.map((p) => p.categoria || p.category).filter(Boolean)
    )
  );

  const getStatusBadge = (estado?: string) => {
    if (!estado) return <Badge variant="secondary">Desconocido</Badge>;
    
    switch (estado.toLowerCase()) {
      case "activo":
      case "active":
        return <Badge variant="default">Activo</Badge>;
      case "inactivo":
      case "inactive":
        return <Badge variant="secondary">Inactivo</Badge>;
      case "agotado":
      case "out_of_stock":
        return <Badge variant="destructive">Agotado</Badge>;
      default:
        return <Badge variant="secondary">{estado}</Badge>;
    }
  };

  const getTotalStock = (product: Product) => {
    const variants = product.variantes || product.variants || [];
    return variants.reduce((total, v) => total + (v.stock || 0), 0);
  };

  const getImageUrl = (product: Product) => {
    return product.imagen_url || 
           product.image_url || 
           "https://placehold.co/100x100/e2e8f0/64748b?text=Sin+Imagen";
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Cargando productos...</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold">Productos</h1>
            <p className="text-muted-foreground">
              Gestiona tu catálogo de productos
            </p>
          </div>
          <Button asChild>
            <Link to="/admin/products/new">
              <Plus className="mr-2 h-4 w-4" />
              Nuevo Producto
            </Link>
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar productos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <Filter className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los estados</SelectItem>
                  <SelectItem value="activo">Activo</SelectItem>
                  <SelectItem value="inactivo">Inactivo</SelectItem>
                  <SelectItem value="agotado">Agotado</SelectItem>
                </SelectContent>
              </Select>

              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <Package className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Categoría" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas las categorías</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat || ""}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Products Table */}
        <Card>
          <CardContent className="p-0">
            {filteredProducts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Package className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium">No hay productos</p>
                <p className="text-sm text-muted-foreground mb-4">
                  {searchTerm || statusFilter !== "all" || categoryFilter !== "all"
                    ? "No se encontraron productos con los filtros aplicados"
                    : "Comienza creando tu primer producto"}
                </p>
                {!searchTerm && statusFilter === "all" && categoryFilter === "all" && (
                  <Button asChild>
                    <Link to="/admin/products/new">
                      <Plus className="mr-2 h-4 w-4" />
                      Crear Producto
                    </Link>
                  </Button>
                )}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[80px]">Imagen</TableHead>
                    <TableHead>Producto</TableHead>
                    <TableHead>Categoría</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Variantes</TableHead>
                    <TableHead className="text-right">Stock Total</TableHead>
                    <TableHead className="w-[70px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredProducts.map((product) => (
                    <TableRow key={product._id}>
                      <TableCell>
                        <img
                          src={getImageUrl(product)}
                          alt={product.nombre || product.name}
                          className="h-12 w-12 rounded object-cover"
                          onError={(e) => {
                            e.currentTarget.src = "https://placehold.co/100x100/e2e8f0/64748b?text=Sin+Imagen";
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <div className="font-medium">
                          {product.nombre || product.name}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {product.categoria || product.category}
                        </Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(product.estado)}</TableCell>
                      <TableCell>
                        {(product.variantes || product.variants || []).length} variante(s)
                      </TableCell>
                      <TableCell className="text-right">
                        {getTotalStock(product)}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem asChild>
                              <Link to={`/admin/products/${product._id}`}>
                                <Eye className="mr-2 h-4 w-4" />
                                Ver Detalles
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link to={`/admin/products/${product._id}/edit`}>
                                <Edit className="mr-2 h-4 w-4" />
                                Editar
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() =>
                                handleDelete(
                                  product._id,
                                  product.nombre || product.name || ""
                                )
                              }
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Eliminar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Summary */}
        {filteredProducts.length > 0 && (
          <div className="text-sm text-muted-foreground">
            Mostrando {filteredProducts.length} de {products.length} productos
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default Products;