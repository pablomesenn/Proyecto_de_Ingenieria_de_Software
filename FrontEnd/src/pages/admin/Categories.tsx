import { useState } from "react";
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

// Mock data
const initialCategories = [
  { id: "1", name: "Porcelanato", productCount: 45, slug: "porcelanato" },
  { id: "2", name: "Cerámica", productCount: 32, slug: "ceramica" },
  { id: "3", name: "Mármol", productCount: 18, slug: "marmol" },
  { id: "4", name: "Granito", productCount: 12, slug: "granito" },
  { id: "5", name: "Madera", productCount: 24, slug: "madera" },
];

const initialTags = [
  { id: "1", name: "Interior", productCount: 89, color: "bg-blue-500" },
  { id: "2", name: "Exterior", productCount: 45, color: "bg-green-500" },
  { id: "3", name: "Antideslizante", productCount: 28, color: "bg-yellow-500" },
  { id: "4", name: "Premium", productCount: 15, color: "bg-purple-500" },
  { id: "5", name: "Rústico", productCount: 22, color: "bg-orange-500" },
  { id: "6", name: "Moderno", productCount: 56, color: "bg-cyan-500" },
];

const Categories = () => {
  const [categories, setCategories] = useState(initialCategories);
  const [tags, setTags] = useState(initialTags);
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newTagName, setNewTagName] = useState("");
  const [editingCategory, setEditingCategory] = useState<typeof initialCategories[0] | null>(null);
  const [editingTag, setEditingTag] = useState<typeof initialTags[0] | null>(null);

  const handleAddCategory = () => {
    if (!newCategoryName.trim()) return;
    const newCategory = {
      id: Date.now().toString(),
      name: newCategoryName,
      productCount: 0,
      slug: newCategoryName.toLowerCase().replace(/\s+/g, "-"),
    };
    setCategories((prev) => [...prev, newCategory]);
    setNewCategoryName("");
    setCategoryDialogOpen(false);
    toast.success("Categoría creada correctamente");
  };

  const handleUpdateCategory = () => {
    if (!editingCategory || !newCategoryName.trim()) return;
    setCategories((prev) =>
      prev.map((cat) =>
        cat.id === editingCategory.id
          ? { ...cat, name: newCategoryName, slug: newCategoryName.toLowerCase().replace(/\s+/g, "-") }
          : cat
      )
    );
    setNewCategoryName("");
    setEditingCategory(null);
    setCategoryDialogOpen(false);
    toast.success("Categoría actualizada correctamente");
  };

  const handleDeleteCategory = (id: string) => {
    setCategories((prev) => prev.filter((cat) => cat.id !== id));
    toast.success("Categoría eliminada correctamente");
  };

  const handleAddTag = () => {
    if (!newTagName.trim()) return;
    const colors = ["bg-blue-500", "bg-green-500", "bg-yellow-500", "bg-purple-500", "bg-orange-500", "bg-cyan-500"];
    const newTag = {
      id: Date.now().toString(),
      name: newTagName,
      productCount: 0,
      color: colors[Math.floor(Math.random() * colors.length)],
    };
    setTags((prev) => [...prev, newTag]);
    setNewTagName("");
    setTagDialogOpen(false);
    toast.success("Etiqueta creada correctamente");
  };

  const handleUpdateTag = () => {
    if (!editingTag || !newTagName.trim()) return;
    setTags((prev) =>
      prev.map((tag) => (tag.id === editingTag.id ? { ...tag, name: newTagName } : tag))
    );
    setNewTagName("");
    setEditingTag(null);
    setTagDialogOpen(false);
    toast.success("Etiqueta actualizada correctamente");
  };

  const handleDeleteTag = (id: string) => {
    setTags((prev) => prev.filter((tag) => tag.id !== id));
    toast.success("Etiqueta eliminada correctamente");
  };

  const openEditCategory = (category: typeof initialCategories[0]) => {
    setEditingCategory(category);
    setNewCategoryName(category.name);
    setCategoryDialogOpen(true);
  };

  const openEditTag = (tag: typeof initialTags[0]) => {
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
                      <TableRow key={category.id}>
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
                              onClick={() => handleDeleteCategory(category.id)}
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
                      key={tag.id}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-card"
                    >
                      <div className={`h-3 w-3 rounded-full ${tag.color}`} />
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
                          onClick={() => handleDeleteTag(tag.id)}
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
