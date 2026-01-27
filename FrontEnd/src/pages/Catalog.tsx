import { useState, useEffect } from "react";
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
  List,
  Loader2,
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
import * as productsApi from "@/api/products";
import { useToast } from "@/hooks/use-toast";

const Catalog = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load categories and tags on mount
  useEffect(() => {
    const loadFilters = async () => {
      try {
        const [categoriesRes, tagsRes] = await Promise.all([
          productsApi.getCategories(),
          productsApi.getTags(),
        ]);
        setCategories(categoriesRes.categories);
        setTags(tagsRes.tags);
      } catch (err) {
        console.error("Error loading filters:", err);
        // Don't show error to user for filters, just log it
      }
    };
    loadFilters();
  }, []);

  // Load products when filters change
  useEffect(() => {
    const loadProducts = async () => {
      setLoading(true);
      setError(null);

      try {
        const params: productsApi.ProductSearchParams = {
          search_text: searchQuery || undefined,
          disponibilidad: showAvailableOnly ? true : undefined,
          limit: 50,
        };

        // Add category filter if any selected
        if (selectedCategories.length > 0) {
          params.categoria = selectedCategories[0] as any; // Backend only supports one category
        }

        // Add tags filter if any selected
        if (selectedTags.length > 0) {
          params.tags = selectedTags as any;
        }

        const response = await productsApi.searchProducts(params);

        // Debug: Log the raw response
        console.log("API Response:", response);
        console.log("Products:", response.products);

        // Map products and filter out any null values
        const mappedProducts = response.products
          .map(productsApi.mapProductToUI)
          .filter((p) => p !== null);

        console.log("Mapped Products:", mappedProducts);
        setProducts(mappedProducts);
      } catch (err) {
        console.error("Error loading products:", err);
        setError("Error cargando productos");
        toast({
          title: "Error",
          description:
            "No se pudieron cargar los productos. Verifica que el backend esté corriendo.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, [searchQuery, selectedCategories, selectedTags, showAvailableOnly, toast]);

  const toggleCategory = (category: string) => {
    setSelectedCategories(
      (prev) =>
        prev.includes(category)
          ? prev.filter((c) => c !== category)
          : [category], // Only allow one
    );
  };

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setSelectedTags([]);
    setShowAvailableOnly(false);
    setSearchQuery("");
  };

  const hasActiveFilters =
    selectedCategories.length > 0 ||
    selectedTags.length > 0 ||
    showAvailableOnly;

  const FilterContent = () => (
    <div className="space-y-6">
      {/* Availability */}
      <div className="flex items-center gap-2">
        <Checkbox
          id="available-only"
          checked={showAvailableOnly}
          onCheckedChange={(checked) => setShowAvailableOnly(checked === true)}
        />
        <Label
          htmlFor="available-only"
          className="text-sm font-normal cursor-pointer"
        >
          Solo productos disponibles
        </Label>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <Collapsible defaultOpen>
          <CollapsibleTrigger className="flex items-center justify-between w-full py-2">
            <span className="font-medium">Categorías</span>
            <ChevronDown className="h-4 w-4" />
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-2 space-y-2">
            {categories.map((category) => (
              <div key={category} className="flex items-center gap-2">
                <Checkbox
                  id={category}
                  checked={selectedCategories.includes(category)}
                  onCheckedChange={() => toggleCategory(category)}
                />
                <Label
                  htmlFor={category}
                  className="text-sm font-normal cursor-pointer flex-1"
                >
                  {category}
                </Label>
              </div>
            ))}
          </CollapsibleContent>
        </Collapsible>
      )}

      {/* Tags */}
      {tags.length > 0 && (
        <Collapsible defaultOpen>
          <CollapsibleTrigger className="flex items-center justify-between w-full py-2">
            <span className="font-medium">Etiquetas</span>
            <ChevronDown className="h-4 w-4" />
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-2">
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <Badge
                  key={tag}
                  variant={selectedTags.includes(tag) ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => toggleTag(tag)}
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>
      )}

      {hasActiveFilters && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearFilters}
          className="w-full"
        >
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
                    <Badge
                      variant="default"
                      className="ml-2 h-5 w-5 p-0 flex items-center justify-center"
                    >
                      {selectedCategories.length +
                        selectedTags.length +
                        (showAvailableOnly ? 1 : 0)}
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
            {selectedCategories.map((category) => (
              <Badge key={category} variant="secondary" className="gap-1">
                {category}
                <X
                  className="h-3 w-3 cursor-pointer"
                  onClick={() => toggleCategory(category)}
                />
              </Badge>
            ))}
            {selectedTags.map((tag) => (
              <Badge key={tag} variant="secondary" className="gap-1">
                {tag}
                <X
                  className="h-3 w-3 cursor-pointer"
                  onClick={() => toggleTag(tag)}
                />
              </Badge>
            ))}
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
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : error ? (
              <div className="text-center py-16">
                <p className="text-destructive mb-4">{error}</p>
                <Button
                  variant="outline"
                  onClick={() => window.location.reload()}
                >
                  Reintentar
                </Button>
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-muted-foreground mb-4">
                  No se encontraron productos
                </p>
                <Button variant="outline" onClick={clearFilters}>
                  Limpiar filtros
                </Button>
              </div>
            ) : (
              <div
                className={
                  viewMode === "grid"
                    ? "grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6"
                    : "space-y-4"
                }
              >
                {products.map((product, index) => (
                  <Link
                    key={product.id}
                    to={`/catalog/${product.id}`}
                    className="group block animate-fade-in"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <Card
                      variant="product"
                      className={viewMode === "list" ? "flex" : ""}
                    >
                      <div
                        className={`relative overflow-hidden ${viewMode === "list" ? "w-40 flex-shrink-0" : "aspect-square"}`}
                      >
                        <img
                          src={product.image}
                          alt={product.name}
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                        {/*<div className="absolute top-3 left-3">
                          <Badge
                            variant={
                              product.available ? "available" : "unavailable"
                            }
                          >
                            {product.available ? "Disponible" : "Agotado"}
                          </Badge>
                        </div>*/}
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
                        <Badge variant="category" className="mb-2">
                          {product.category}
                        </Badge>
                        <h3 className="font-display font-semibold group-hover:text-primary transition-colors mb-2">
                          {product.name}
                        </h3>
                        {product.variants && product.variants.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {product.variants
                              .slice(0, 3)
                              .map((variant: any) => (
                                <span
                                  key={variant.id}
                                  className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded"
                                >
                                  {variant.size} cm
                                </span>
                              ))}
                            {product.variants.length > 3 && (
                              <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                                +{product.variants.length - 3}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </Card>
                  </Link>
                ))}
              </div>
            )}

            {/* Results Count */}
            {!loading && !error && (
              <p className="text-sm text-muted-foreground mt-6">
                Mostrando {products.length} producto
                {products.length !== 1 ? "s" : ""}
              </p>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Catalog;
