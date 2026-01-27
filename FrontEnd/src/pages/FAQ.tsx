import MainLayout from "@/components/layout/MainLayout";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import { HelpCircle } from "lucide-react";

const FAQ = () => {
  const faqs = [
    {
      category: "Reservas y Pedidos",
      questions: [
        {
          question: "¿Cómo puedo hacer una reserva de productos?",
          answer:
            "Para hacer una reserva, primero debes registrarte en nuestro sistema. Luego, explora nuestro catálogo, agrega los productos que te interesan a tu lista de deseos y crea una reserva. Un administrador revisará tu solicitud dentro de las próximas 24 horas.",
        },
        {
          question: "¿Cuánto tiempo dura una reserva?",
          answer:
            "Las reservas tienen una duración de 24 horas. Si después de este tiempo no has confirmado tu compra o la reserva no ha sido aprobada, el inventario volverá a estar disponible automáticamente.",
        },
        {
          question: "¿Puedo cancelar una reserva?",
          answer:
            "Sí, puedes cancelar una reserva en estado pendiente o aprobada desde tu panel de 'Mis Reservas'. Una vez cancelada, el inventario volverá a estar disponible para otros clientes.",
        },
        {
          question: "¿Qué pasa si mi reserva es rechazada?",
          answer:
            "Si tu reserva es rechazada, recibirás una notificación por correo con la razón del rechazo (por ejemplo, stock insuficiente). Puedes crear una nueva reserva ajustando las cantidades o eligiendo otros productos.",
        },
      ],
    },
    {
      category: "Productos y Stock",
      questions: [
        {
          question: "¿Todos los productos del catálogo están disponibles?",
          answer:
            "El catálogo muestra únicamente productos con stock disponible. Las cantidades mostradas son en tiempo real y se actualizan automáticamente cuando se crean reservas.",
        },
        {
          question: "¿Puedo ver productos sin stock?",
          answer:
            "Actualmente solo mostramos productos con stock disponible. Si estás buscando un producto específico que no encuentras, contáctanos y te ayudaremos a verificar si podemos conseguirlo.",
        },
        {
          question: "¿Con qué frecuencia se actualiza el inventario?",
          answer:
            "Nuestro inventario se actualiza en tiempo real. Cuando se crea, aprueba o cancela una reserva, las cantidades disponibles se ajustan automáticamente.",
        },
        {
          question: "¿Qué tipos de pisos ofrecen?",
          answer:
            "Ofrecemos una amplia variedad: pisos laminados, porcelanatos, cerámicas, vinílicos (LVT) y mármoles naturales. Cada categoría incluye diferentes estilos, tamaños y acabados.",
        },
      ],
    },
    {
      category: "Cuenta y Seguridad",
      questions: [
        {
          question: "¿Es seguro registrarse en el sistema?",
          answer:
            "Sí, tu información está protegida. Utilizamos cifrado de contraseñas y seguimos las mejores prácticas de seguridad para proteger tus datos personales.",
        },
        {
          question: "¿Olvidé mi contraseña, qué hago?",
          answer:
            "En la página de inicio de sesión, haz clic en '¿Olvidaste tu contraseña?' y sigue las instrucciones. Recibirás un correo con un enlace para restablecer tu contraseña.",
        },
        {
          question: "¿Puedo actualizar mi información de contacto?",
          answer:
            "Sí, puedes actualizar tu nombre, teléfono y otras preferencias desde tu perfil en cualquier momento. Solo haz clic en el ícono de usuario en la parte superior derecha.",
        },
      ],
    },
    {
      category: "Entrega y Pago",
      questions: [
        {
          question: "¿Hacen entregas a domicilio?",
          answer:
            "Sí, realizamos entregas en toda la zona de Jacó y alrededores. Para otras ubicaciones, contáctanos para coordinar la logística y costos de envío.",
        },
        {
          question: "¿Cuáles son las formas de pago aceptadas?",
          answer:
            "Aceptamos efectivo, transferencias bancarias y tarjetas de crédito/débito. Los detalles de pago se coordinan directamente con nuestro equipo una vez que tu reserva sea aprobada.",
        },
        {
          question: "¿Debo pagar antes de recoger los productos?",
          answer:
            "Generalmente requerimos un adelanto del 50% una vez aprobada la reserva, y el saldo restante al momento de la entrega o retiro. Esto puede variar según el monto total.",
        },
        {
          question: "¿Ofrecen instalación?",
          answer:
            "Podemos recomendarte instaladores certificados de confianza. Contáctanos para más información sobre este servicio.",
        },
      ],
    },
    {
      category: "Notificaciones",
      questions: [
        {
          question: "¿Recibiré notificaciones sobre mi reserva?",
          answer:
            "Sí, recibirás notificaciones por correo electrónico cuando: (1) tu reserva sea aprobada, (2) tu reserva sea rechazada, (3) tu reserva esté próxima a expirar, y (4) tu reserva haya expirado.",
        },
        {
          question: "¿Puedo desactivar las notificaciones por correo?",
          answer:
            "Las notificaciones importantes sobre el estado de tus reservas no se pueden desactivar, ya que son esenciales para mantener la comunicación sobre tus pedidos.",
        },
      ],
    },
  ];

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-12">
        {/* Hero */}
        <div className="max-w-4xl mx-auto text-center mb-16">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
            <HelpCircle className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Preguntas Frecuentes
          </h1>
          <p className="text-lg text-muted-foreground">
            Encuentra respuestas a las preguntas más comunes sobre nuestros productos y servicios
          </p>
        </div>

        {/* FAQs por categoría */}
        <div className="max-w-4xl mx-auto space-y-8">
          {faqs.map((category, idx) => (
            <div key={idx}>
              <h2 className="text-2xl font-display font-bold mb-4">{category.category}</h2>
              <Card>
                <CardContent className="p-0">
                  <Accordion type="single" collapsible className="w-full">
                    {category.questions.map((faq, qIdx) => (
                      <AccordionItem key={qIdx} value={`${idx}-${qIdx}`} className="px-6">
                        <AccordionTrigger className="text-left hover:no-underline">
                          <span className="font-medium">{faq.question}</span>
                        </AccordionTrigger>
                        <AccordionContent className="text-muted-foreground leading-relaxed">
                          {faq.answer}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>

        {/* Still have questions? */}
        <div className="max-w-4xl mx-auto mt-16">
          <Card className="bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10">
            <CardContent className="py-12 text-center">
              <h2 className="text-2xl font-display font-bold mb-4">
                ¿Aún tienes preguntas?
              </h2>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                Si no encontraste la respuesta que buscabas, no dudes en contactarnos. Nuestro
                equipo está listo para ayudarte.
              </p>
              <a
                href="/contact"
                className="inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-8 font-medium transition-colors"
              >
                Contáctanos
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default FAQ;