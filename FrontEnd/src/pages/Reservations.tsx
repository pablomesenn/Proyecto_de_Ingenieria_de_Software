import { Link } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CalendarClock, ArrowRight } from "lucide-react";

const Reservations = () => {
  return (
    <MainLayout>
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-display font-bold flex items-center gap-3">
            <CalendarClock className="h-8 w-8 text-primary" />
            Mis Reservas
          </h1>
          <p className="text-muted-foreground mt-1">
            Gestiona y consulta el estado de tus reservas
          </p>
        </div>

        {/* Placeholder for future reservations list */}
        <Card className="py-16">
          <CardContent className="flex flex-col items-center text-center">
            <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
              <CalendarClock className="h-10 w-10 text-muted-foreground" />
            </div>
            <h2 className="text-xl font-display font-semibold mb-2">
              No tienes reservas activas
            </h2>
            <p className="text-muted-foreground max-w-sm mb-6">
              Explora nuestro catálogo y crea tu primera reserva desde tu lista
              de interés.
            </p>
            <div className="flex gap-3">
              <Button variant="outline" asChild>
                <Link to="/wishlist">Ver mi lista de interés</Link>
              </Button>
              <Button asChild>
                <Link to="/catalog">
                  Explorar Catálogo
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default Reservations;
