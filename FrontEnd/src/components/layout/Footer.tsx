import { Link } from "react-router-dom";
import { Phone, Mail, MapPin, Clock } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-foreground text-primary-foreground">
      <div className="container py-12 md:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-display font-bold text-lg">PK</span>
              </div>
              <div>
                <span className="font-display font-semibold text-lg">Pisos Kermy</span>
                <span className="text-xs text-primary-foreground/70 block -mt-1">Jacó S.A.</span>
              </div>
            </div>
            <p className="text-sm text-primary-foreground/80 leading-relaxed">
              Especialistas en pisos y revestimientos de alta calidad para proyectos residenciales y comerciales.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h4 className="font-display font-semibold text-lg">Enlaces</h4>
            <nav className="flex flex-col gap-2">
              <Link to="/catalog" className="text-sm text-primary-foreground/80 hover:text-primary-foreground transition-colors">
                Catálogo
              </Link>
              <Link to="/about" className="text-sm text-primary-foreground/80 hover:text-primary-foreground transition-colors">
                Sobre Nosotros
              </Link>
              <Link to="/contact" className="text-sm text-primary-foreground/80 hover:text-primary-foreground transition-colors">
                Contacto
              </Link>
              <Link to="/faq" className="text-sm text-primary-foreground/80 hover:text-primary-foreground transition-colors">
                Preguntas Frecuentes
              </Link>
            </nav>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h4 className="font-display font-semibold text-lg">Contacto</h4>
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-3 text-sm text-primary-foreground/80">
                <Phone className="h-4 w-4 text-primary" />
                <span>+506 2643-1333</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-primary-foreground/80">
                <Mail className="h-4 w-4 text-primary" />
                <span>pisoskermy@gmail.com</span>
              </div>
              <div className="flex items-start gap-3 text-sm text-primary-foreground/80">
                <MapPin className="h-4 w-4 text-primary mt-0.5" />
                <span>Jacó, Puntarenas, Costa Rica</span>
              </div>
            </div>
          </div>

          {/* Hours */}
          <div className="space-y-4">
            <h4 className="font-display font-semibold text-lg">Horario</h4>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-3 text-sm text-primary-foreground/80">
                <Clock className="h-4 w-4 text-primary" />
                <span>Lun - Vie: 9:00 - 17:00</span>
              </div>
              <div className="text-sm text-primary-foreground/80 pl-7">
                Sáb: 9:00 - 12:00
              </div>
              <div className="text-sm text-primary-foreground/80 pl-7">
                Dom: Cerrado
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-primary-foreground/20 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-primary-foreground/60">
            © {new Date().getFullYear()} Pisos Kermy Jacó S.A. Todos los derechos reservados.
          </p>
          <div className="flex gap-6">
            <Link to="/privacy" className="text-xs text-primary-foreground/60 hover:text-primary-foreground transition-colors">
              Política de Privacidad
            </Link>
            <Link to="/terms" className="text-xs text-primary-foreground/60 hover:text-primary-foreground transition-colors">
              Términos de Servicio
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;