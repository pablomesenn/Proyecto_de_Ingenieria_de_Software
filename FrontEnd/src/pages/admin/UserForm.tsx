import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { ArrowLeft, Shield, UserCircle } from "lucide-react";
import { toast } from "sonner";

const UserForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  // Form state
  const [name, setName] = useState(isEditing ? "María García" : "");
  const [email, setEmail] = useState(isEditing ? "maria@email.com" : "");
  const [phone, setPhone] = useState(isEditing ? "+506 8888-1234" : "");
  const [role, setRole] = useState<"admin" | "customer">(isEditing ? "customer" : "customer");
  const [isActive, setIsActive] = useState(true);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim() || !email.trim()) {
      toast.error("Nombre y email son requeridos");
      return;
    }

    if (!isEditing && !password) {
      toast.error("La contraseña es requerida para nuevos usuarios");
      return;
    }

    if (password && password !== confirmPassword) {
      toast.error("Las contraseñas no coinciden");
      return;
    }

    if (password && password.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    toast.success(isEditing ? "Usuario actualizado correctamente" : "Usuario creado correctamente");
    navigate("/admin/users");
  };

  return (
    <AdminLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button type="button" variant="ghost" size="icon" asChild>
            <Link to="/admin/users">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-display font-bold">
              {isEditing ? "Editar Usuario" : "Nuevo Usuario"}
            </h1>
            <p className="text-muted-foreground">
              {isEditing ? "Modifica los datos del usuario" : "Completa el formulario para crear un nuevo usuario"}
            </p>
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="outline" asChild>
              <Link to="/admin/users">Cancelar</Link>
            </Button>
            <Button type="submit">
              {isEditing ? "Guardar Cambios" : "Crear Usuario"}
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <Card>
              <CardHeader>
                <CardTitle>Información Personal</CardTitle>
                <CardDescription>Datos básicos del usuario</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nombre Completo *</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Nombre del usuario"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Correo Electrónico *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="email@ejemplo.com"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Teléfono</Label>
                  <Input
                    id="phone"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+506 0000-0000"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Password */}
            <Card>
              <CardHeader>
                <CardTitle>{isEditing ? "Cambiar Contraseña" : "Contraseña"}</CardTitle>
                <CardDescription>
                  {isEditing 
                    ? "Deja en blanco para mantener la contraseña actual" 
                    : "Define la contraseña del usuario"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="password">
                    {isEditing ? "Nueva Contraseña" : "Contraseña *"}
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirmar Contraseña</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  La contraseña debe tener al menos 6 caracteres
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Role */}
            <Card>
              <CardHeader>
                <CardTitle>Rol del Usuario</CardTitle>
                <CardDescription>Define los permisos del usuario</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Select value={role} onValueChange={(v) => setRole(v as "admin" | "customer")}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">
                      <div className="flex items-center gap-2">
                        <UserCircle className="h-4 w-4" />
                        <span>Cliente</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="admin">
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        <span>Administrador</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                <div className="p-3 rounded-lg bg-muted/50 text-sm">
                  {role === "admin" ? (
                    <p>Los administradores tienen acceso completo al panel de administración.</p>
                  ) : (
                    <p>Los clientes pueden ver el catálogo, crear listas de deseos y hacer reservas.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Status */}
            <Card>
              <CardHeader>
                <CardTitle>Estado de la Cuenta</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Cuenta Activa</Label>
                    <p className="text-xs text-muted-foreground">
                      El usuario puede iniciar sesión
                    </p>
                  </div>
                  <Switch checked={isActive} onCheckedChange={setIsActive} />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </AdminLayout>
  );
};

export default UserForm;