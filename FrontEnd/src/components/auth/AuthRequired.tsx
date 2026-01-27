import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogIn, ShieldAlert } from "lucide-react";

interface LoginRequiredProps {
  message?: string;
  description?: string;
}

const LoginRequired = ({
  message = "Necesitas ingresar con una cuenta para acceder",
  description = "Por favor inicia sesión para continuar",
}: LoginRequiredProps) => {
  return (
    <Card className="py-16">
      <CardContent className="flex flex-col items-center text-center">
        <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
          <ShieldAlert className="h-10 w-10 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-display font-semibold mb-2">{message}</h2>
        <p className="text-muted-foreground max-w-sm mb-6">{description}</p>
        <div className="flex gap-3">
          <Button variant="outline" asChild>
            <Link to="/">Volver al inicio</Link>
          </Button>
          <Button asChild>
            <Link to="/login">
              <LogIn className="h-4 w-4 mr-2" />
              Iniciar Sesión
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default LoginRequired;
