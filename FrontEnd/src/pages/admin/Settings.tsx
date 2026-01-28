import { useState } from "react";
import AdminLayout from "@/components/layout/AdminLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import {
  Bell,
  Mail,
  Clock,
  Database,
  Shield,
  Save,
  RotateCcw,
} from "lucide-react";

const Settings = () => {
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    reservationExpiration: 24,
    lowStockThreshold: 10,
    emailNotifications: true,
    reservationNotifications: true,
    inventoryAlerts: true,
    autoApproveReservations: false,
    maintenanceMode: false,
  });

  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: "Configuración guardada",
        description: "Los cambios se han aplicado correctamente.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudieron guardar los cambios.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSettings({
      reservationExpiration: 24,
      lowStockThreshold: 10,
      emailNotifications: true,
      reservationNotifications: true,
      inventoryAlerts: true,
      autoApproveReservations: false,
      maintenanceMode: false,
    });
    
    toast({
      title: "Configuración restablecida",
      description: "Se han restaurado los valores predeterminados.",
    });
  };

  return (
    <AdminLayout>
      <div className="space-y-6 max-w-4xl">
        <div>
          <h1 className="text-2xl font-display font-bold">Configuración del Sistema</h1>
          <p className="text-muted-foreground">
            Administra las preferencias y comportamiento del sistema
          </p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              <CardTitle>Reservas</CardTitle>
            </div>
            <CardDescription>
              Configuración del sistema de reservas
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="expiration">
                Tiempo de expiración de reservas (horas)
              </Label>
              <Input
                id="expiration"
                type="number"
                value={settings.reservationExpiration}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    reservationExpiration: parseInt(e.target.value) || 24,
                  })
                }
                min={1}
                max={168}
              />
              <p className="text-xs text-muted-foreground">
                Las reservas se cancelarán automáticamente después de este tiempo
              </p>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Aprobación automática</Label>
                <p className="text-xs text-muted-foreground">
                  Las reservas se aprobarán automáticamente sin revisión manual
                </p>
              </div>
              <Switch
                checked={settings.autoApproveReservations}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, autoApproveReservations: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-primary" />
              <CardTitle>Inventario</CardTitle>
            </div>
            <CardDescription>
              Configuración de control de inventario
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="threshold">
                Umbral de stock bajo (unidades)
              </Label>
              <Input
                id="threshold"
                type="number"
                value={settings.lowStockThreshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    lowStockThreshold: parseInt(e.target.value) || 10,
                  })
                }
                min={1}
                max={100}
              />
              <p className="text-xs text-muted-foreground">
                Se generará una alerta cuando el stock esté por debajo de este valor
              </p>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Alertas de inventario</Label>
                <p className="text-xs text-muted-foreground">
                  Recibir notificaciones cuando el stock esté bajo
                </p>
              </div>
              <Switch
                checked={settings.inventoryAlerts}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, inventoryAlerts: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-primary" />
              <CardTitle>Notificaciones</CardTitle>
            </div>
            <CardDescription>
              Gestiona las notificaciones del sistema
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Notificaciones por email</Label>
                <p className="text-xs text-muted-foreground">
                  Habilitar envío de correos electrónicos
                </p>
              </div>
              <Switch
                checked={settings.emailNotifications}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, emailNotifications: checked })
                }
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Notificaciones de reservas</Label>
                <p className="text-xs text-muted-foreground">
                  Recibir alertas sobre nuevas reservas y cambios de estado
                </p>
              </div>
              <Switch
                checked={settings.reservationNotifications}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, reservationNotifications: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <CardTitle>Sistema</CardTitle>
            </div>
            <CardDescription>
              Configuración general del sistema
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Modo de mantenimiento</Label>
                <p className="text-xs text-muted-foreground">
                  Deshabilitar acceso público al sistema
                </p>
              </div>
              <Switch
                checked={settings.maintenanceMode}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, maintenanceMode: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button onClick={handleSave} disabled={loading}>
            <Save className="h-4 w-4 mr-2" />
            Guardar cambios
          </Button>
          <Button variant="outline" onClick={handleReset} disabled={loading}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Restablecer
          </Button>
        </div>
      </div>
    </AdminLayout>
  );
};

export default Settings;