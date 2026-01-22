import { useState } from "react";
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
  Plus
} from "lucide-react";
import MainLayout from "@/components/layout/MainLayout";
import { cn } from "@/lib/utils";

// Mock product data
const productData = {
  id: "1",
  name: "Porcelanato Terrazo Blanco",
  category: "Porcelanato",
  description: "Porcelanato de alta calidad con acabado terrazo, ideal para interiores modernos. Su diseño atemporal combina perfectamente con cualquier estilo de decoración, aportando elegancia y sofisticación a tus espacios.",
  tags: ["Interior", "Moderno", "Premium"],
  images: [
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=800&fit=crop",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=800&fit=crop",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=800&fit=crop",
  ],
  variants: [
    { id: "v1", size: "60x60 cm", available: true, stock: 150 },
    { id: "v2", size: "80x80 cm", available: true, stock: 75 },
    { id: "v3", size: "120x60 cm", available: false, stock: 0 },
  ],
  specs: [
    { label: "Material", value: "Porcelanato esmaltado" },
    { label: "Acabado", value: "Pulido" },
    { label: "Resistencia", value: "PEI 4" },
    { label: "Uso", value: "Residencial y comercial ligero" },
  ],
};

const relatedProducts = [
  {
    id: "2",
    name: "Mármol Calacatta Gold",
    category: "Mármol",
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=400&fit=crop",
    available: true,
  },
  {
    id: "5",
    name: "Porcelanato Madera Natural",
    category: "Porcelanato",
    image: "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=400&h=400&fit=crop",
    available: true,
  },
];

const ProductDetail = () => {
  const { id } = useParams();
  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState(productData.variants[0]);
  const [quantity, setQuantity] = useState(1);
  const [isWishlisted, setIsWishlisted] = useState(false);

  const handleQuantityChange = (delta: number) => {
    setQuantity(prev => Math.max(1, Math.min(prev + delta, selectedVariant.stock || 99)));
  };

  return (
    <MainLayout>
      <div className="container py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
          <Link to="/catalog" className="hover:text-foreground transition-colors">
            Catálogo
          </Link>
          <ChevronRight className="h-4 w-4" />
          <Link to={`/catalog?category=${productData.category.toLowerCase()}`} className="hover:text-foreground transition-colors">
            {productData.category}
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-foreground">{productData.name}</span>
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
                src={productData.images[selectedImage]}
                alt={productData.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex gap-3">
              {productData.images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={cn(
                    "w-20 h-20 rounded-md overflow-hidden border-2 transition-colors",
                    selectedImage === index ? "border-primary" : "border-transparent"
                  )}
                >
                  <img
                    src={image}
                    alt={`${productData.name} ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div>
              <Badge variant="category" className="mb-3">{productData.category}</Badge>
              <h1 className="text-3xl md:text-4xl font-display font-bold mb-4">
                {productData.name}
              </h1>
              <p className="text-muted-foreground leading-relaxed">
                {productData.description}
              </p>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              {productData.tags.map(tag => (
                <Badge key={tag} variant="tag">{tag}</Badge>
              ))}
            </div>

            {/* Size Variants */}
            <div className="space-y-3">
              <h3 className="font-medium">Tamaño</h3>
              <div className="flex flex-wrap gap-3">
                {productData.variants.map((variant) => (
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
                      selectedVariant.id === variant.id
                        ? "border-primary bg-primary/5 text-primary"
                        : variant.available
                          ? "border-border hover:border-primary/50"
                          : "border-border bg-muted text-muted-foreground cursor-not-allowed line-through"
                    )}
                  >
                    {variant.size}
                  </button>
                ))}
              </div>
            </div>

            {/* Availability */}
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
                  <span className="text-sm text-destructive">No disponible</span>
                </>
              )}
            </div>

            {/* Quantity & Actions */}
            {selectedVariant.available && (
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
                    <span className="w-12 text-center font-medium">{quantity}</span>
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
                  <Button className="flex-1" size="lg">
                    <ShoppingBag className="h-5 w-5 mr-2" />
                    Reservar Ahora
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => setIsWishlisted(!isWishlisted)}
                    className={cn(isWishlisted && "text-primary border-primary")}
                  >
                    <Heart className={cn("h-5 w-5", isWishlisted && "fill-current")} />
                  </Button>
                </div>
              </div>
            )}

            {/* Specifications */}
            <Card>
              <CardContent className="p-4">
                <h3 className="font-display font-semibold mb-3">Especificaciones</h3>
                <dl className="grid grid-cols-2 gap-3">
                  {productData.specs.map((spec) => (
                    <div key={spec.label}>
                      <dt className="text-xs text-muted-foreground">{spec.label}</dt>
                      <dd className="text-sm font-medium">{spec.value}</dd>
                    </div>
                  ))}
                </dl>
              </CardContent>
            </Card>

            {/* Reservation Note */}
            <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/50">
              <Check className="h-5 w-5 text-success mt-0.5" />
              <div className="text-sm">
                <p className="font-medium">Proceso de Reserva</p>
                <p className="text-muted-foreground">
                  Al reservar, recibirás una confirmación en un plazo de 24 horas hábiles. 
                  La reserva estará activa por 7 días.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Related Products */}
        <section className="mt-16">
          <h2 className="text-2xl font-display font-bold mb-6">
            Productos Relacionados
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedProducts.map((product) => (
              <Link 
                key={product.id}
                to={`/catalog/${product.id}`}
                className="group block"
              >
                <div className="relative aspect-square rounded-lg overflow-hidden bg-muted mb-3">
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
                </div>
                <Badge variant="category" className="mb-2">{product.category}</Badge>
                <h3 className="font-display font-semibold group-hover:text-primary transition-colors">
                  {product.name}
                </h3>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </MainLayout>
  );
};

export default ProductDetail;