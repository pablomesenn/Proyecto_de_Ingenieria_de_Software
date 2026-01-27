import { useEffect, useState } from "react";

import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Edit, Trash2, Tags, FolderOpen } from "lucide-react";
import { toast } from "sonner";

// import para las funciones de catalogo
import { 
  fetchCatalogCategories,
  createCatalogCategory,
  updateCatalogCategory,
  deleteCatalogCategory,
  fetchCatalogTags,
  createCatalogTag,
  updateCatalogTag,
  deleteCatalogTag,
  type CatalogCategory,
  type CatalogTag,
} from "@/api/catalog";

import { getCategories, getTags } from "@/api/products";

// Mock data
//const initialCategories = [
//  { id: "1", name: "Porcelanato", productCount: 45, slug: "porcelanato" },
//  { id: "2", name: "Cerámica", productCount: 32, slug: "ceramica" },
//  { id: "3", name: "Mármol", productCount: 18, slug: "marmol" },
//  { id: "4", name: "Granito", productCount: 12, slug: "granito" },
//  { id: "5", name: "Madera", productCount: 24, slug: "madera" },
//];

//const initialTags = [
//  { id: "1", name: "Interior", productCount: 89, color: "bg-blue-500" },
//  { id: "2", name: "Exterior", productCount: 45, color: "bg-green-500" },
//  { id: "3", name: "Antideslizante", productCount: 28, color: "bg-yellow-500" },
//  { id: "4", name: "Premium", productCount: 15, color: "bg-purple-500" },
//  { id: "5", name: "Rústico", productCount: 22, color: "bg-orange-500" },
//  { id: "6", name: "Moderno", productCount: 56, color: "bg-cyan-500" },
//];

type UiCategory = {
  id: string;       // viene del backend (_id)
  name: string;
  slug: string;
  productCount: number;
};

type UiTag = {
  id: string;       // viene del backend (_id) o el nombre si no hay _id
  name: string;
  productCount: number;
  color: string;    // calculado en front
};

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[áäà]/g, "a")
    .replace(/[éëè]/g, "e")
    .replace(/[íïì]/g, "i")
    .replace(/[óöò]/g, "o")
    .replace(/[úüù]/g, "u")
    .replace(/ñ/g, "n")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

const TAG_COLORS = [
  "bg-blue-500",
  "bg-green-500",
  "bg-yellow-500",
  "bg-purple-500",
  "bg-orange-500",
  "bg-cyan-500",
  "bg-pink-500",
  "bg-indigo-500",
];

function stableColorFromString(input: string) {
  
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash = (hash * 31 + input.charCodeAt(i)) >>> 0;
  }
  return TAG_COLORS[hash % TAG_COLORS.length];
}




const Categories = () => {
  const [categories, setCategories] = useState<CatalogCategory[]>([]);
  const [tags, setTags] = useState<CatalogTag[]>([]);

  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newTagName, setNewTagName] = useState("");
  const [editingCategory, setEditingCategory] = useState<CatalogCategory | null>(null);
  const [editingTag, setEditingTag] = useState<CatalogTag | null>(null);

  useEffect(() => {
  const load = async () => {
    const [catRes, tagRes] = await Promise.all([fetchCatalogCategories(), fetchCatalogTags()]);

    setCategories(catRes);
    setTags(tagRes);
  };

  load().catch((e) => {
    toast.error("No se pudieron cargar categorías/tags");
    console.error(e);
  });
}, []);

  const handleAddCategory = async () => {
    if (!newCategoryName.trim()) return;
    try {
      const created = await createCatalogCategory(newCategoryName.trim());
      setCategories((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
      setNewCategoryName("");
      setCategoryDialogOpen(false);
      toast.success("Categoría creada correctamente");
    } catch (e: any) {
      toast.error(e?.message || "No se pudo crear la categoría");
    }
  };

  


  const handleUpdateCategory = async () => {
    if (!editingCategory || !newCategoryName.trim()) return;
    try {
      const updated = await updateCatalogCategory(editingCategory._id, newCategoryName.trim());
      setCategories((prev) =>
        prev.map((c) => (c._id === updated._id ? updated : c)).sort((a, b) => a.name.localeCompare(b.name))
      );
      setNewCategoryName("");
      setEditingCategory(null);
      setCategoryDialogOpen(false);
      toast.success("Categoría actualizada correctamente");
    } catch (e: any) {
      toast.error(e?.message || "No se pudo actualizar la categoría");
    }
  };


  const handleDeleteCategory = async (id: string) => {
    try {
      await deleteCatalogCategory(id);
      setCategories((prev) => prev.filter((c) => c._id !== id));
      toast.success("Categoría eliminada correctamente");
    } catch (e: any) {
      // el backend devuelve 409 con mensaje "en uso"
      toast.error(e?.message || "No se pudo eliminar la categoría");
    }
  };


  const handleAddTag = async () => {
    if (!newTagName.trim()) return;
    try {
      const created = await createCatalogTag(newTagName.trim());
      setTags((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
      setNewTagName("");
      setTagDialogOpen(false);
      toast.success("Etiqueta creada correctamente");
    } catch (e: any) {
      toast.error(e?.message || "No se pudo crear la etiqueta");
    }
  };

  const handleUpdateTag = async () => {
    if (!editingTag || !newTagName.trim()) return;
    try {
      const updated = await updateCatalogTag(editingTag._id, newTagName.trim());
      setTags((prev) => prev.map((t) => (t._id === updated._id ? updated : t)).sort((a, b) => a.name.localeCompare(b.name)));
      setNewTagName("");
      setEditingTag(null);
      setTagDialogOpen(false);
      toast.success("Etiqueta actualizada correctamente");
    } catch (e: any) {
      toast.error(e?.message || "No se pudo actualizar la etiqueta");
    }
  };

  const handleDeleteTag = async (id: string) => {
    try {
      await deleteCatalogTag(id);
      setTags((prev) => prev.filter((t) => t._id !== id));
      toast.success("Etiqueta eliminada correctamente");
    } catch (e: any) {
      toast.error(e?.message || "No se pudo eliminar la etiqueta");
    }
  };


  const openEditCategory = (category: CatalogCategory) => {
    setEditingCategory(category);
    setNewCategoryName(category.name);
    setCategoryDialogOpen(true);
  };

  const openEditTag = (tag: CatalogTag) => {
    setEditingTag(tag);
    setNewTagName(tag.name);
    setTagDialogOpen(true);
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-display font-bold">Categorías y Etiquetas</h1>
          <p className="text-muted-foreground">Organiza el catálogo con categorías y etiquetas</p>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="categories" className="space-y-6">
          <TabsList>
            <TabsTrigger value="categories" className="gap-2">
              <FolderOpen className="h-4 w-4" />
              Categorías
            </TabsTrigger>
            <TabsTrigger value="tags" className="gap-2">
              <Tags className="h-4 w-4" />
              Etiquetas
            </TabsTrigger>
          </TabsList>

          {/* Categories Tab */}
          <TabsContent value="categories">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Categorías de Productos</CardTitle>
                  <CardDescription>Agrupa los productos por tipo de material</CardDescription>
                </div>
                <Dialog open={categoryDialogOpen} onOpenChange={(open) => {
                  setCategoryDialogOpen(open);
                  if (!open) {
                    setEditingCategory(null);
                    setNewCategoryName("");
                  }
                }}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Nueva Categoría
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingCategory ? "Editar Categoría" : "Nueva Categoría"}
                      </DialogTitle>
                      <DialogDescription>
                        {editingCategory
                          ? "Modifica el nombre de la categoría"
                          : "Ingresa el nombre de la nueva categoría"}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="category-name">Nombre de la Categoría</Label>
                        <Input
                          id="category-name"
                          value={newCategoryName}
                          onChange={(e) => setNewCategoryName(e.target.value)}
                          placeholder="Ej: Porcelanato"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setCategoryDialogOpen(false)}>
                        Cancelar
                      </Button>
                      <Button onClick={editingCategory ? handleUpdateCategory : handleAddCategory}>
                        {editingCategory ? "Guardar Cambios" : "Crear Categoría"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nombre</TableHead>
                      <TableHead>Slug</TableHead>
                      <TableHead className="text-center">Productos</TableHead>
                      <TableHead className="w-[100px]">Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {categories.map((category) => (
                      <TableRow key={category._id}>
                        <TableCell className="font-medium">{category.name}</TableCell>
                        <TableCell className="text-muted-foreground">{category.slug}</TableCell>
                        <TableCell className="text-center">
                          <Badge variant="secondary">{category.productCount}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => openEditCategory(category)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteCategory(category._id)}
                              disabled={category.productCount > 0}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tags Tab */}
          <TabsContent value="tags">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Etiquetas de Productos</CardTitle>
                  <CardDescription>Etiquetas para filtrar y organizar productos</CardDescription>
                </div>
                <Dialog open={tagDialogOpen} onOpenChange={(open) => {
                  setTagDialogOpen(open);
                  if (!open) {
                    setEditingTag(null);
                    setNewTagName("");
                  }
                }}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Nueva Etiqueta
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingTag ? "Editar Etiqueta" : "Nueva Etiqueta"}
                      </DialogTitle>
                      <DialogDescription>
                        {editingTag
                          ? "Modifica el nombre de la etiqueta"
                          : "Ingresa el nombre de la nueva etiqueta"}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="tag-name">Nombre de la Etiqueta</Label>
                        <Input
                          id="tag-name"
                          value={newTagName}
                          onChange={(e) => setNewTagName(e.target.value)}
                          placeholder="Ej: Premium"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setTagDialogOpen(false)}>
                        Cancelar
                      </Button>
                      <Button onClick={editingTag ? handleUpdateTag : handleAddTag}>
                        {editingTag ? "Guardar Cambios" : "Crear Etiqueta"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-3">
                  {tags.map((tag) => (
                    <div
                      key={tag._id}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-card"
                    >
                      <div className={`h-3 w-3 rounded-full ${stableColorFromString(tag.name)}`} />
                      <span className="font-medium">{tag.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        {tag.productCount}
                      </Badge>
                      <div className="flex gap-1 ml-2 border-l pl-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => openEditTag(tag)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => handleDeleteTag(tag._id)}
                          disabled={tag.productCount > 0}
                        >
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AdminLayout>
  );
};

export default Categories;
