import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Heart,
  ShoppingBag,
  ArrowLeft,
  Check,
  ChevronRight,
  Minus,
  Plus,
  Loader2,
} from "lucide-react";
import MainLayout from "@/components/layout/MainLayout";
import { cn } from "@/lib/utils";
import * as productsApi from "@/api/products";
import { useWishlist } from "@/contexts/WishlistContext";
import { useToast } from "@/hooks/use-toast";

const ProductDetail = () => {
  const { id } = useParams();
  const { toast } = useToast();
  const { addItem: addToWishlist } = useWishlist();

  const [product, setProduct] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState<any | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [addingToWishlist, setAddingToWishlist] = useState(false);

  useEffect(() => {
    const loadProduct = async () => {
      if (!id) return;

      setLoading(true);
      setError(null);

      try {
        const productData = await productsApi.getProductDetail(id);
        const mappedProduct = productsApi.mapProductToUI(productData);
        setProduct(mappedProduct);

        // Select first available variant
        const firstAvailable = mappedProduct.variants.find(
          (v: any) => v.available,
        );
        setSelectedVariant(firstAvailable || mappedProduct.variants[0]);
      } catch (err) {
        console.error("Error loading product:", err);
        setError("No se pudo cargar el producto");
        toast({
          title: "Error",
          description: "No se pudo cargar el producto",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [id, toast]);

  const handleQuantityChange = (delta: number) => {
    if (!selectedVariant) return;
    setQuantity((prev) =>
      Math.max(1, Math.min(prev + delta, selectedVariant.stock || 99)),
    );
  };

  const handleAddToWishlist = async () => {
    if (!selectedVariant) return;

    setAddingToWishlist(true);
    try {
      await addToWishlist(selectedVariant.id, quantity);
      setIsWishlisted(true);
      toast({
        title: "Agregado a lista de interés",
        description: `${quantity} unidad(es) de ${product.name} agregadas`,
      });
    } catch (err) {
      toast({
        title: "Error",
        description:
          err instanceof Error ? err.message : "No se pudo agregar a la lista",
        variant: "destructive",
      });
    } finally {
      setAddingToWishlist(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="container py-16 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </MainLayout>
    );
  }

  if (error || !product) {
    return (
      <MainLayout>
        <div className="container py-16 text-center">
          <p className="text-destructive mb-4">
            {error || "Producto no encontrado"}
          </p>
          <Button variant="outline" asChild>
            <Link to="/catalog">Volver al catálogo</Link>
          </Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
          <Link
            to="/catalog"
            className="hover:text-foreground transition-colors"
          >
            Catálogo
          </Link>
          <ChevronRight className="h-4 w-4" />
          <Link
            to={`/catalog?category=${product.category.toLowerCase()}`}
            className="hover:text-foreground transition-colors"
          >
            {product.category}
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-foreground">{product.name}</span>
        </nav>

        {/* Back Button (Mobile) */}
        <Button variant="ghost" size="sm" asChild className="mb-4 md:hidden">
          <Link to="/catalog">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al catálogo
          </Link>
        </Button>

        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Image Gallery */}
          <div className="space-y-4">
            <div className="aspect-square rounded-lg overflow-hidden bg-muted">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div>
              <Badge variant="category" className="mb-3">
                {product.category}
              </Badge>
              <h1 className="text-3xl md:text-4xl font-display font-bold mb-4">
                {product.name}
              </h1>
              <p className="text-muted-foreground leading-relaxed">
                {product.description || "Producto de alta calidad."}
              </p>
            </div>

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {product.tags.map((tag: string) => (
                  <Badge key={tag} variant="tag">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Size Variants */}
            <div className="space-y-3">
              <h3 className="font-medium">Tamaño</h3>
              <div className="flex flex-wrap gap-3">
                {product.variants.map((variant: any) => (
                  <button
                    key={variant.id}
                    onClick={() => {
                      if (variant.available) {
                        setSelectedVariant(variant);
                        setQuantity(1);
                      }
                    }}
                    disabled={!variant.available}
                    className={cn(
                      "px-4 py-2 rounded-md border-2 text-sm font-medium transition-all",
                      selectedVariant?.id === variant.id
                        ? "border-primary bg-primary/5 text-primary"
                        : variant.available
                          ? "border-border hover:border-primary/50"
                          : "border-border bg-muted text-muted-foreground cursor-not-allowed line-through",
                    )}
                  >
                    {variant.size}
                  </button>
                ))}
              </div>
            </div>

            {/* Availability */}
            {selectedVariant && (
              <div className="flex items-center gap-2">
                {selectedVariant.available ? (
                  <>
                    <div className="h-2 w-2 rounded-full bg-success" />
                    <span className="text-sm text-success">
                      Disponible ({selectedVariant.stock} unidades)
                    </span>
                  </>
                ) : (
                  <>
                    <div className="h-2 w-2 rounded-full bg-destructive" />
                    <span className="text-sm text-destructive">
                      No disponible
                    </span>
                  </>
                )}
              </div>
            )}

            {/* Quantity & Actions */}
            {selectedVariant?.available && (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium">Cantidad:</span>
                  <div className="flex items-center border rounded-md">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 rounded-r-none"
                      onClick={() => handleQuantityChange(-1)}
                      disabled={quantity <= 1}
                    >
                      <Minus className="h-4 w-4" />
                    </Button>
                    <span className="w-12 text-center font-medium">
                      {quantity}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 rounded-l-none"
                      onClick={() => handleQuantityChange(1)}
                      disabled={quantity >= selectedVariant.stock}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button
                    className="flex-1"
                    size="lg"
                    onClick={handleAddToWishlist}
                    disabled={addingToWishlist}
                  >
                    {addingToWishlist ? (
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    ) : (
                      <ShoppingBag className="h-5 w-5 mr-2" />
                    )}
                    Agregar a Lista
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={handleAddToWishlist}
                    disabled={addingToWishlist}
                    className={cn(
                      isWishlisted && "text-primary border-primary",
                    )}
                  >
                    <Heart
                      className={cn("h-5 w-5", isWishlisted && "fill-current")}
                    />
                  </Button>
                </div>
              </div>
            )}

            {/* Reservation Note */}
            <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/50">
              <Check className="h-5 w-5 text-success mt-0.5" />
              <div className="text-sm">
                <p className="font-medium">Proceso de Reserva</p>
                <p className="text-muted-foreground">
                  Al agregar a tu lista de interés, podrás crear una reserva más
                  adelante. Las reservas requieren confirmación en 24 horas
                  hábiles.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProductDetail;
