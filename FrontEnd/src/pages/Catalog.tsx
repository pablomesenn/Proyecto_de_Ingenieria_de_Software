import { useState } from "react";
import { Link } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { 
  Search, 
  SlidersHorizontal, 
  X, 
  Heart, 
  ChevronDown,
  LayoutGrid,
  List
} from "lucide-react";
import MainLayout from "@/components/layout/MainLayout";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

// Mock data
const categories = [
  { id: "porcelanato", name: "Porcelanato", count: 45 },
  { id: "ceramica", name: "Cerámica", count: 32 },
  { id: "marmol", name: "Mármol", count: 18 },
  { id: "granito", name: "Granito", count: 12 },
  { id: "madera", name: "Madera", count: 24 },
];

const tags = [
  { id: "interior", name: "Interior" },
  { id: "exterior", name: "Exterior" },
  { id: "antideslizante", name: "Antideslizante" },
  { id: "premium", name: "Premium" },
  { id: "rustico", name: "Rústico" },
  { id: "moderno", name: "Moderno" },
];

const products = [
  {
    id: "1",
    name: "Porcelanato Terrazo Blanco",
    category: "Porcelanato",
    tags: ["Interior", "Moderno"],
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
    available: true,
    sizes: ["60x60", "80x80", "120x60"],
  },
  {
    id: "2",
    name: "Mármol Calacatta Gold",
    category: "Mármol",
    tags: ["Interior", "Premium"],
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600&h=600&fit=crop",
    available: true,
    sizes: ["60x120", "80x160"],
  },
  {
    id: "3",
    name: "Cerámica Rústica Terracota",
    category: "Cerámica",
    tags: ["Exterior", "Rústico", "Antideslizante"],
    image: "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&h=600&fit=crop",
    available: false,
    sizes: ["30x30", "45x45"],
  },
  {
    id: "4",
    name: "Granito Negro Galaxy",
    category: "Granito",
    tags: ["Interior", "Premium"],
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&h=600&fit=crop",
    available: true,
    sizes: ["60x60", "80x80"],
  },
  {
    id: "5",
    name: "Porcelanato Madera Natural",
    category: "Porcelanato",
    tags: ["Interior", "Moderno"],
    image: "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=600&h=600&fit=crop",
    available: true,
    sizes: ["20x120", "25x150"],
  },
  {
    id: "6",
    name: "Cerámica Subway Blanca",
    category: "Cerámica",
    tags: ["Interior", "Moderno"],
    image: "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=600&h=600&fit=crop",
    available: true,
    sizes: ["7.5x15", "10x20"],
  },
];

const Catalog = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const toggleCategory = (id: string) => {
    setSelectedCategories(prev => 
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  const toggleTag = (id: string) => {
    setSelectedTags(prev => 
      prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
    );
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setSelectedTags([]);
    setShowAvailableOnly(false);
    setSearchQuery("");
  };

  const hasActiveFilters = selectedCategories.length > 0 || selectedTags.length > 0 || showAvailableOnly;

  // Filter products
  const filteredProducts = products.filter(product => {
    if (searchQuery && !product.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (selectedCategories.length > 0 && !selectedCategories.some(c => 
      product.category.toLowerCase() === categories.find(cat => cat.id === c)?.name.toLowerCase()
    )) {
      return false;
    }
    if (showAvailableOnly && !product.available) {
      return false;
    }
    return true;
  });

  const FilterContent = () => (
    <div className="space-y-6">
      {/* Availability */}
      <div className="flex items-center gap-2">
        <Checkbox 
          id="available-only" 
          checked={showAvailableOnly}
          onCheckedChange={(checked) => setShowAvailableOnly(checked === true)}
        />
        <Label htmlFor="available-only" className="text-sm font-normal cursor-pointer">
          Solo productos disponibles
        </Label>
      </div>

      {/* Categories */}
      <Collapsible defaultOpen>
        <CollapsibleTrigger className="flex items-center justify-between w-full py-2">
          <span className="font-medium">Categorías</span>
          <ChevronDown className="h-4 w-4" />
        </CollapsibleTrigger>
        <CollapsibleContent className="pt-2 space-y-2">
          {categories.map((category) => (
            <div key={category.id} className="flex items-center gap-2">
              <Checkbox 
                id={category.id}
                checked={selectedCategories.includes(category.id)}
                onCheckedChange={() => toggleCategory(category.id)}
              />
              <Label htmlFor={category.id} className="text-sm font-normal cursor-pointer flex-1">
                {category.name}
              </Label>
              <span className="text-xs text-muted-foreground">{category.count}</span>
            </div>
          ))}
        </CollapsibleContent>
      </Collapsible>

      {/* Tags */}
      <Collapsible defaultOpen>
        <CollapsibleTrigger className="flex items-center justify-between w-full py-2">
          <span className="font-medium">Etiquetas</span>
          <ChevronDown className="h-4 w-4" />
        </CollapsibleTrigger>
        <CollapsibleContent className="pt-2">
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <Badge
                key={tag.id}
                variant={selectedTags.includes(tag.id) ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => toggleTag(tag.id)}
              >
                {tag.name}
              </Badge>
            ))}
          </div>
        </CollapsibleContent>
      </Collapsible>

      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={clearFilters} className="w-full">
          <X className="h-4 w-4 mr-2" />
          Limpiar filtros
        </Button>
      )}
    </div>
  );

  return (
    <MainLayout>
      <div className="container py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-display font-bold mb-2">
            Catálogo de Productos
          </h1>
          <p className="text-muted-foreground">
            Explora nuestra selección de pisos y revestimientos de alta calidad
          </p>
        </div>

        {/* Search and Filters Bar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar productos..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            {/* Mobile Filter Button */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" className="lg:hidden">
                  <SlidersHorizontal className="h-4 w-4 mr-2" />
                  Filtros
                  {hasActiveFilters && (
                    <Badge variant="default" className="ml-2 h-5 w-5 p-0 flex items-center justify-center">
                      {selectedCategories.length + selectedTags.length + (showAvailableOnly ? 1 : 0)}
                    </Badge>
                  )}
                </Button>
              </SheetTrigger>
              <SheetContent side="left">
                <SheetHeader>
                  <SheetTitle>Filtros</SheetTitle>
                </SheetHeader>
                <div className="mt-6">
                  <FilterContent />
                </div>
              </SheetContent>
            </Sheet>

            {/* View Toggle */}
            <div className="flex border rounded-md">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="icon"
                onClick={() => setViewMode("grid")}
                className="rounded-r-none"
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="icon"
                onClick={() => setViewMode("list")}
                className="rounded-l-none"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2 mb-6">
            {selectedCategories.map(id => {
              const category = categories.find(c => c.id === id);
              return category ? (
                <Badge key={id} variant="secondary" className="gap-1">
                  {category.name}
                  <X 
                    className="h-3 w-3 cursor-pointer" 
                    onClick={() => toggleCategory(id)}
                  />
                </Badge>
              ) : null;
            })}
            {showAvailableOnly && (
              <Badge variant="secondary" className="gap-1">
                Disponibles
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => setShowAvailableOnly(false)}
                />
              </Badge>
            )}
          </div>
        )}

        {/* Main Content */}
        <div className="flex gap-8">
          {/* Desktop Sidebar */}
          <aside className="hidden lg:block w-64 flex-shrink-0">
            <Card className="p-4 sticky top-20">
              <FilterContent />
            </Card>
          </aside>

          {/* Product Grid */}
          <div className="flex-1">
            {filteredProducts.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-muted-foreground mb-4">No se encontraron productos</p>
                <Button variant="outline" onClick={clearFilters}>
                  Limpiar filtros
                </Button>
              </div>
            ) : (
              <div className={viewMode === "grid" 
                ? "grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6"
                : "space-y-4"
              }>
                {filteredProducts.map((product, index) => (
                  <Link 
                    key={product.id}
                    to={`/catalog/${product.id}`}
                    className="group block animate-fade-in"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <Card variant="product" className={viewMode === "list" ? "flex" : ""}>
                      <div className={`relative overflow-hidden ${viewMode === "list" ? "w-40 flex-shrink-0" : "aspect-square"}`}>
                        <img
                          src={product.image}
                          alt={product.name}
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                        <div className="absolute top-3 left-3">
                          <Badge variant={product.available ? "available" : "unavailable"}>
                            {product.available ? "Disponible" : "Agotado"}
                          </Badge>
                        </div>
                        <button 
                          className="absolute top-3 right-3 h-8 w-8 rounded-full bg-background/80 backdrop-blur flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-background"
                          onClick={(e) => {
                            e.preventDefault();
                            // TODO: Add to wishlist
                          }}
                        >
                          <Heart className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="p-4">
                        <Badge variant="category" className="mb-2">{product.category}</Badge>
                        <h3 className="font-display font-semibold group-hover:text-primary transition-colors mb-2">
                          {product.name}
                        </h3>
                        <div className="flex flex-wrap gap-1">
                          {product.sizes.map(size => (
                            <span key={size} className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                              {size} cm
                            </span>
                          ))}
                        </div>
                      </div>
                    </Card>
                  </Link>
                ))}
              </div>
            )}

            {/* Results Count */}
            <p className="text-sm text-muted-foreground mt-6">
              Mostrando {filteredProducts.length} de {products.length} productos
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Catalog;