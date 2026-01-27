import MainLayout from "@/components/layout/MainLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Building2, Award, Users, Target } from "lucide-react";

const About = () => {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Sobre Nosotros
          </h1>
          <p className="text-lg text-muted-foreground leading-relaxed">
            Somos Pisos Kermy Jacó S.A., tu aliado de confianza en soluciones de pisos y
            revestimientos de alta calidad en Costa Rica.
          </p>
        </div>

        {/* Quiénes Somos */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-3xl font-display font-bold mb-4">¿Quiénes Somos?</h2>
              <p className="text-muted-foreground leading-relaxed mb-4">
                Desde nuestra fundación, nos hemos dedicado a ofrecer las mejores opciones en
                pisos laminados, porcelanatos, cerámicas, vinílicos y mármoles para proyectos
                residenciales y comerciales.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Con años de experiencia en el mercado costarricense, nos enorgullecemos de
                brindar no solo productos de excelencia, sino también un servicio al cliente
                excepcional y asesoría personalizada para cada proyecto.
              </p>
            </div>
            <div className="relative h-[300px] rounded-lg overflow-hidden bg-gradient-to-br from-primary/10 to-primary/5">
              <div className="absolute inset-0 flex items-center justify-center">
                <Building2 className="h-32 w-32 text-primary/20" />
              </div>
            </div>
          </div>
        </section>

        {/* Valores */}
        <section className="mb-16">
          <h2 className="text-3xl font-display font-bold text-center mb-12">
            Nuestros Valores
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-4">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <Award className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">Calidad</h3>
                  <p className="text-muted-foreground">
                    Trabajamos con marcas reconocidas y productos certificados que
                    garantizan durabilidad y belleza.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-4">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <Users className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">Servicio</h3>
                  <p className="text-muted-foreground">
                    Nuestro equipo está comprometido en brindar atención personalizada y
                    asesoría en cada etapa de tu proyecto.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-4">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <Target className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">Compromiso</h3>
                  <p className="text-muted-foreground">
                    Nos dedicamos a superar las expectativas de nuestros clientes.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Misión y Visión */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 gap-8">
            <Card className="bg-gradient-to-br from-primary/5 to-background">
              <CardContent className="pt-6">
                <h3 className="text-2xl font-display font-bold mb-4">Nuestra Misión</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Ofrecer soluciones integrales en pisos y revestimientos de alta calidad,
                  brindando a nuestros clientes productos excepcionales, asesoría experta y un
                  servicio que transforme sus espacios en lugares únicos y funcionales.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-primary/5 to-background">
              <CardContent className="pt-6">
                <h3 className="text-2xl font-display font-bold mb-4">Nuestra Visión</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Ser la empresa líder en Costa Rica en distribución de pisos y revestimientos,
                  reconocida por nuestra innovación, calidad de productos y excelencia en el
                  servicio al cliente.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Call to Action */}
        <section className="text-center">
          <Card className="bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10">
            <CardContent className="py-12">
              <h2 className="text-3xl font-display font-bold mb-4">
                ¿Listo para transformar tu espacio?
              </h2>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                Explora nuestro catálogo de productos y descubre las mejores opciones para tu
                proyecto.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="/catalog"
                  className="inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-8 font-medium transition-colors"
                >
                  Ver Catálogo
                </a>
                <a
                  href="/contact"
                  className="inline-flex items-center justify-center rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-8 font-medium transition-colors"
                >
                  Contáctanos
                </a>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </MainLayout>
  );
};

export default About;