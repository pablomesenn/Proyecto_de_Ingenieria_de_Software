import { useState } from "react";
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

// Mock data
const products = [
  {
    id: "1",
    name: "Porcelanato Terrazo Blanco",
    category: "Porcelanato",
    status: "active" as const,
    variants: 3,
    totalStock: 245,
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=100&h=100&fit=crop",
  },
  {
    id: "2",
    name: "Mármol Calacatta Gold",
    category: "Mármol",
    status: "active" as const,
    variants: 2,
    totalStock: 89,
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=100&h=100&fit=crop",
  },
  {
    id: "3",
    name: "Cerámica Rústica Terracota",
    category: "Cerámica",
    status: "out_of_stock" as const,
    variants: 2,
    totalStock: 0,
    image: "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=100&h=100&fit=crop",
  },
  {
    id: "4",
    name: "Granito Negro Galaxy",
    category: "Granito",
    status: "active" as const,
    variants: 2,
    totalStock: 156,
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=100&h=100&fit=crop",
  },
  {
    id: "5",
    name: "Porcelanato Madera Natural",
    category: "Porcelanato",
    status: "inactive" as const,
    variants: 2,
    totalStock: 78,
    image: "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=100&h=100&fit=crop",
  },
  {
    id: "6",
    name: "Cerámica Subway Blanca",
    category: "Cerámica",
    status: "active" as const,
    variants: 2,
    totalStock: 320,
    image: "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=100&h=100&fit=crop",
  },
];

const statusConfig = {
  active: { label: "Activo", variant: "success" as const },
  inactive: { label: "Inactivo", variant: "secondary" as const },
  out_of_stock: { label: "Sin Stock", variant: "destructive" as const },
};

const Products = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  const filteredProducts = products.filter((product) => {
    if (searchQuery && !product.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (statusFilter !== "all" && product.status !== statusFilter) {
      return false;
    }
    if (categoryFilter !== "all" && product.category !== categoryFilter) {
      return false;
    }
    return true;
  });

  const categories = [...new Set(products.map((p) => p.category))];

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-display font-bold">Gestión de Productos</h1>
            <p className="text-muted-foreground">Administra el catálogo de productos</p>
          </div>
          <Button asChild>
            <Link to="/admin/products/new">
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Producto
            </Link>
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
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
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los estados</SelectItem>
                  <SelectItem value="active">Activo</SelectItem>
                  <SelectItem value="inactive">Inactivo</SelectItem>
                  <SelectItem value="out_of_stock">Sin Stock</SelectItem>
                </SelectContent>
              </Select>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="Categoría" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas las categorías</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
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
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Imagen</TableHead>
                  <TableHead>Producto</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead className="text-center">Variantes</TableHead>
                  <TableHead className="text-center">Stock Total</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-32 text-center">
                      <div className="flex flex-col items-center gap-2">
                        <Package className="h-8 w-8 text-muted-foreground" />
                        <p className="text-muted-foreground">No se encontraron productos</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredProducts.map((product) => (
                    <TableRow key={product.id}>
                      <TableCell>
                        <img
                          src={product.image}
                          alt={product.name}
                          className="h-12 w-12 rounded-lg object-cover"
                        />
                      </TableCell>
                      <TableCell>
                        <Link
                          to={`/admin/products/${product.id}`}
                          className="font-medium hover:text-primary transition-colors"
                        >
                          {product.name}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Badge variant="category">{product.category}</Badge>
                      </TableCell>
                      <TableCell className="text-center">{product.variants}</TableCell>
                      <TableCell className="text-center">
                        <span
                          className={
                            product.totalStock === 0
                              ? "text-destructive font-medium"
                              : product.totalStock < 20
                              ? "text-warning font-medium"
                              : ""
                          }
                        >
                          {product.totalStock}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusConfig[product.status].variant}>
                          {statusConfig[product.status].label}
                        </Badge>
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
                              <Link to={`/catalog/${product.id}`} className="cursor-pointer">
                                <Eye className="h-4 w-4 mr-2" />
                                Ver en catálogo
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link to={`/admin/products/${product.id}`} className="cursor-pointer">
                                <Edit className="h-4 w-4 mr-2" />
                                Editar
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive cursor-pointer">
                              <Trash2 className="h-4 w-4 mr-2" />
                              Eliminar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Summary */}
        <div className="text-sm text-muted-foreground">
          Mostrando {filteredProducts.length} de {products.length} productos
        </div>
      </div>
    </AdminLayout>
  );
};

export default Products;
