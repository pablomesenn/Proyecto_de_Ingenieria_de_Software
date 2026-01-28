import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
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
  AlertCircle,
  LogIn,
} from "lucide-react";
import MainLayout from "@/components/layout/MainLayout";
import { cn } from "@/lib/utils";
import * as productsApi from "@/api/products";
import * as inventoryApi from "@/api/inventory";
import { useWishlist } from "@/contexts/WishlistContext";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { createReservation } from "@/api/reservations";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const { addItem: addToWishlist } = useWishlist();

  const [product, setProduct] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState<any | null>(null);
  const [variantInventory, setVariantInventory] = useState<any | null>(null);
  const [loadingInventory, setLoadingInventory] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [addingToWishlist, setAddingToWishlist] = useState(false);
  const [creatingReservation, setCreatingReservation] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);

  useEffect(() => {
    const loadProduct = async () => {
      if (!id) return;

      setLoading(true);
      setError(null);

      try {
        const productData = await productsApi.getProductDetail(id);
        const mappedProduct = productsApi.mapProductToUI(productData);
        setProduct(mappedProduct);

        // Select first variant (will load inventory after)
        if (mappedProduct.variants.length > 0) {
          setSelectedVariant(mappedProduct.variants[0]);
        }
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

  // Load inventory when variant changes
  useEffect(() => {
    const loadInventory = async () => {
      if (!selectedVariant) return;

      setLoadingInventory(true);
      try {
        const inventory = await inventoryApi.getInventoryByVariant(
          selectedVariant.id,
        );
        setVariantInventory(inventory);

        // Update available stock in selected variant
        setSelectedVariant((prev: any) => ({
          ...prev,
          stock: inventory.stock_disponible,
          available: inventory.disponible && inventory.stock_disponible > 0,
        }));

        // Reset quantity if exceeds available stock
        if (quantity > inventory.stock_disponible) {
          setQuantity(Math.max(1, inventory.stock_disponible));
        }
      } catch (err) {
        console.error("Error loading inventory:", err);
        // Don't show error toast, just log it
        // Product might not have inventory record yet
        setVariantInventory(null);
      } finally {
        setLoadingInventory(false);
      }
    };

    loadInventory();
  }, [selectedVariant?.id]);

  const handleQuantityChange = (delta: number) => {
    if (!variantInventory) return;

    const maxStock = variantInventory.stock_disponible || 0;
    setQuantity((prev) => Math.max(1, Math.min(prev + delta, maxStock)));
  };

  const handleVariantChange = (variant: any) => {
    setSelectedVariant(variant);
    setQuantity(1);
    setVariantInventory(null);
  };

  const handleAddToWishlist = async () => {
    // Check if user is logged in
    if (!user) {
      setShowLoginDialog(true);
      return;
    }

    if (!selectedVariant || !variantInventory?.disponible) return;

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

  const handleCreateReservation = async () => {
    // Check if user is logged in
    if (!user) {
      setShowLoginDialog(true);
      return;
    }

    if (!selectedVariant || !variantInventory?.disponible) return;

    setCreatingReservation(true);
    try {
      const reservationData = {
        items: [
          {
            variant_id: selectedVariant.id,
            quantity: quantity,
            product_name: product.name,
            variant_size: selectedVariant.size,
            price: selectedVariant.price,
          },
        ],
      };

      const result = await createReservation(reservationData);

      toast({
        title: "Reserva creada exitosamente",
        description: `Tu reserva ha sido creada. Espera la confirmación del administrador.`,
      });

      // Navigate to reservations page
      navigate("/reservations");
    } catch (err) {
      toast({
        title: "Error",
        description:
          err instanceof Error ? err.message : "No se pudo crear la reserva",
        variant: "destructive",
      });
    } finally {
      setCreatingReservation(false);
    }
  };

  const getStockStatus = () => {
    if (!variantInventory) {
      return {
        message: "Verificando disponibilidad...",
        color: "text-muted-foreground",
        dotColor: "bg-muted-foreground",
      };
    }

    if (
      !variantInventory.disponible ||
      variantInventory.stock_disponible === 0
    ) {
      return {
        message: "No disponible",
        color: "text-destructive",
        dotColor: "bg-destructive",
      };
    }

    if (variantInventory.stock_disponible < 10) {
      return {
        message: `Pocas unidades (${variantInventory.stock_disponible} disponibles)`,
        color: "text-yellow-600",
        dotColor: "bg-yellow-600",
      };
    }

    return {
      message: `Disponible (${variantInventory.stock_disponible} unidades)`,
      color: "text-success",
      dotColor: "bg-success",
    };
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

  const stockStatus = getStockStatus();
  const canAddToWishlist =
    variantInventory?.disponible && variantInventory?.stock_disponible > 0;

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
                    onClick={() => handleVariantChange(variant)}
                    className={cn(
                      "px-4 py-2 rounded-md border-2 text-sm font-medium transition-all",
                      selectedVariant?.id === variant.id
                        ? "border-primary bg-primary/5 text-primary"
                        : "border-border hover:border-primary/50",
                    )}
                  >
                    {variant.size}
                  </button>
                ))}
              </div>
            </div>

            {/* Availability with real-time inventory */}
            <div className="flex items-center gap-2">
              {loadingInventory ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    Verificando disponibilidad...
                  </span>
                </>
              ) : (
                <>
                  <div
                    className={cn("h-2 w-2 rounded-full", stockStatus.dotColor)}
                  />
                  <span className={cn("text-sm", stockStatus.color)}>
                    {stockStatus.message}
                  </span>
                </>
              )}
            </div>

            {/* Stock retention info */}
            {variantInventory && variantInventory.stock_retenido > 0 && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-muted/50 text-sm">
                <AlertCircle className="h-4 w-4 text-muted-foreground mt-0.5" />
                <p className="text-muted-foreground">
                  {variantInventory.stock_retenido} unidades en proceso de
                  reserva
                </p>
              </div>
            )}

            {/* Quantity & Actions */}
            {canAddToWishlist && (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium">Cantidad:</span>
                  <div className="flex items-center border rounded-md">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 rounded-r-none"
                      onClick={() => handleQuantityChange(-1)}
                      disabled={quantity <= 1 || loadingInventory}
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
                      disabled={
                        quantity >= (variantInventory?.stock_disponible || 0) ||
                        loadingInventory
                      }
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button
                    className="flex-1"
                    size="lg"
                    onClick={handleCreateReservation}
                    disabled={creatingReservation || loadingInventory}
                  >
                    {creatingReservation ? (
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    ) : (
                      <ShoppingBag className="h-5 w-5 mr-2" />
                    )}
                    Hacer Reserva
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={handleAddToWishlist}
                    disabled={addingToWishlist || loadingInventory}
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

            {/* Out of stock message */}
            {!canAddToWishlist && !loadingInventory && (
              <div className="p-4 rounded-lg bg-muted/50 border border-border">
                <p className="text-sm text-muted-foreground">
                  Este tamaño no está disponible actualmente. Por favor
                  selecciona otro tamaño o revisa más tarde.
                </p>
              </div>
            )}

            {/* Reservation Note */}
            <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/50">
              <Check className="h-5 w-5 text-success mt-0.5" />
              <div className="text-sm">
                <p className="font-medium">Proceso de Reserva</p>
                <p className="text-muted-foreground">
                  Las reservas requieren confirmación del administrador en 24
                  horas hábiles. Usa el botón de corazón para agregar a tu lista
                  de interés sin crear una reserva inmediata.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Login Required Dialog */}
        <AlertDialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>
                Necesitas ingresar con una cuenta para acceder
              </AlertDialogTitle>
              <AlertDialogDescription>
                Para crear reservas o agregar productos a tu lista de interés,
                necesitas iniciar sesión con tu cuenta.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancelar</AlertDialogCancel>
              <AlertDialogAction onClick={() => navigate("/login")}>
                <LogIn className="h-4 w-4 mr-2" />
                Iniciar Sesión
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </MainLayout>
  );
};

export default ProductDetail;
