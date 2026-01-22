import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Shield, Truck, Award, ChevronRight } from "lucide-react";
import MainLayout from "@/components/layout/MainLayout";
import heroImage from "@/assets/hero-tiles.jpg";

// Mock featured products
const featuredProducts = [
  {
    id: "1",
    name: "Porcelanato Terrazo",
    category: "Porcelanato",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
    available: true,
  },
  {
    id: "2", 
    name: "Mármol Calacatta",
    category: "Mármol",
    image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=400&fit=crop",
    available: true,
  },
  {
    id: "3",
    name: "Cerámica Rústica",
    category: "Cerámica",
    image: "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=400&h=400&fit=crop",
    available: false,
  },
  {
    id: "4",
    name: "Granito Natural",
    category: "Granito",
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=400&fit=crop",
    available: true,
  },
];

const features = [
  {
    icon: Shield,
    title: "Calidad Garantizada",
    description: "Productos de las mejores marcas con garantía extendida",
  },
  {
    icon: Truck,
    title: "Entrega Segura",
    description: "Servicio de entrega profesional en toda la zona",
  },
  {
    icon: Award,
    title: "25+ Años de Experiencia",
    description: "Décadas transformando espacios en Costa Rica",
  },
];

const Index = () => {
  return (
    <MainLayout>
      {/* Hero Section */}
      <section className="relative min-h-[80vh] flex items-center">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroImage})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-foreground/90 via-foreground/70 to-transparent" />
        </div>

        {/* Content */}
        <div className="container relative z-10 py-20">
          <div className="max-w-2xl space-y-8 animate-fade-in-up">
            <Badge variant="secondary" className="text-sm px-4 py-1.5">
              Nuevas colecciones 2026
            </Badge>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-bold text-primary-foreground leading-tight">
              Transformamos tus espacios con estilo y calidad
            </h1>
            
            <p className="text-lg text-primary-foreground/80 max-w-lg">
              Descubre nuestra colección exclusiva de pisos y revestimientos para crear ambientes únicos que reflejen tu personalidad.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button variant="hero" size="xl" asChild>
                <Link to="/catalog">
                  Ver Catálogo
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button variant="heroOutline" size="xl" asChild>
                <Link to="/contact">
                  Contáctanos
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-muted/50">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={feature.title}
                className="flex items-start gap-4 animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-display font-semibold text-lg mb-1">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-20">
        <div className="container">
          <div className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-3xl md:text-4xl font-display font-bold mb-2">
                Productos Destacados
              </h2>
              <p className="text-muted-foreground">
                Selección de nuestras mejores opciones
              </p>
            </div>
            <Button variant="ghost" asChild className="hidden sm:flex">
              <Link to="/catalog">
                Ver todos
                <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product, index) => (
              <Link 
                key={product.id} 
                to={`/catalog/${product.id}`}
                className="group block animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
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

          <div className="mt-8 text-center sm:hidden">
            <Button variant="outline" asChild>
              <Link to="/catalog">
                Ver todo el catálogo
                <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-hero">
        <div className="container text-center">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-primary-foreground mb-4">
            ¿Listo para transformar tu espacio?
          </h2>
          <p className="text-primary-foreground/80 max-w-xl mx-auto mb-8">
            Explora nuestro catálogo completo y encuentra el piso perfecto para tu proyecto. 
            Ofrecemos asesoría personalizada sin compromiso.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="secondary" size="xl" asChild>
              <Link to="/catalog">
                Explorar Catálogo
              </Link>
            </Button>
            <Button variant="heroOutline" size="xl" asChild>
              <Link to="/register">
                Crear Cuenta
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </MainLayout>
  );
};

export default Index;