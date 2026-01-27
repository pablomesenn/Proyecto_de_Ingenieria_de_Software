import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AdminLayout from "@/components/layout/AdminLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { fetchUsers, createUser, deleteUser, updateUser, type UiUser } from "@/api/users";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  UserPlus,
  Users,
  Shield,
  UserCircle,
} from "lucide-react";
import { toast } from "sonner";



const roleConfig = {
  admin: { label: "Administrador", icon: Shield, color: "text-primary" },
  customer: { label: "Cliente", icon: UserCircle, color: "text-muted-foreground" },
};

const UsersPage = () => {
  const [users, setUsers] = useState<UiUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<UiUser | null>(null);


  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newUserData, setNewUserData] = useState({
    name: "",
    email: "",
    phone: "",
    role: "customer" as "admin" | "customer",
    password: "",
  });

  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [userToEdit, setUserToEdit] = useState<UiUser | null>(null);

  const [editUserData, setEditUserData] = useState({
    name: "",
    email: "",
    phone: "",
    role: "customer" as "admin" | "customer",
    isActive: true,
    password: "",
  });

  
  useEffect(() => {
    async function loadUsers() {
      try {
        setLoading(true);
        const data = await fetchUsers();
        setUsers(data);
        setError(null);
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar los usuarios");
        toast.error("Error cargando usuarios (verifica sesión ADMIN)");
      } finally {
        setLoading(false);
      }
    }

    loadUsers();
  }, []);


  const filteredUsers = useMemo(() => {
    return users.filter((user) => {
      if (
        searchQuery &&
        !user.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !user.email.toLowerCase().includes(searchQuery.toLowerCase())
      ) {
        return false;
      }

      if (roleFilter !== "all" && user.role !== roleFilter) {
        return false;
      }

      if (statusFilter === "active" && !user.isActive) {
        return false;
      }

      if (statusFilter === "inactive" && user.isActive) {
        return false;
      }

      return true;
    });
  }, [users, searchQuery, roleFilter, statusFilter]);


  const handleCreateUser = async () => {
    if (!newUserData.name || !newUserData.email || !newUserData.password) {
      toast.error("Nombre, email y contraseña son requeridos");
      return;
    }

    try {
      const created = await createUser({
        name: newUserData.name,
        email: newUserData.email,
        phone: newUserData.phone,
        role: newUserData.role,
        password: newUserData.password,
      });

      // Insertar arriba en la tabla (o al final, como prefieras)
      setUsers((prev) => [created, ...prev]);

      toast.success("Usuario creado correctamente");
      setDialogOpen(false);
      setNewUserData({ name: "", email: "", phone: "", role: "customer", password: "" });
    } catch (e: any) {
      console.error(e);
      toast.error(e?.message ?? "No se pudo crear el usuario");
    }
  };


  const handleToggleStatus = async (userId: string, currentStatus: boolean) => {
      try {
    const updated = await updateUser(userId, { isActive: !currentStatus });

    setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, ...updated } : u)));

        toast.success(!currentStatus ? "Usuario activado correctamente" : "Usuario desactivado correctamente");
      } catch (err: any) {
        console.error(err);
        toast.error(err?.message ?? "No se pudo actualizar el estado");
      }
};

  const openDeleteDialog = (user: UiUser) => {
    setUserToDelete(user);
    setDeleteDialogOpen(true);
};

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setUserToDelete(null);
  };

  const confirmDeleteUser = async () => {
    if (!userToDelete) return;

    try {
      await deleteUser(userToDelete.id);

      // Backend desactiva -> reflejamos en UI
      setUsers((prev) =>
        prev.map((u) => (u.id === userToDelete.id ? { ...u, isActive: false } : u))
      );

      toast.success("Usuario desactivado correctamente");
      closeDeleteDialog();
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message ?? "No se pudo eliminar el usuario");
    }
};

  const openEditDialog = (user: UiUser) => {
    setUserToEdit(user);
    setEditUserData({
      name: user.name ?? "",
      email: user.email ?? "",
      phone: user.phone ?? "",
      role: user.role,
      isActive: user.isActive,
      password: "",
    });
    setEditDialogOpen(true);
  };

  const closeEditDialog = () => {
    setEditDialogOpen(false);
    setUserToEdit(null);
    setEditUserData({
      name: "",
      email: "",
      phone: "",
      role: "customer",
      isActive: true,
      password: "",
    });
  };

  const handleUpdateUser = async () => {
    if (!userToEdit) return;

    if (!editUserData.name.trim() || !editUserData.email.trim()) {
      toast.error("Nombre y email son requeridos");
      return;
    }

    try {
      const updated = await updateUser(userToEdit.id, {
        name: editUserData.name.trim(),
        email: editUserData.email.trim(),
        phone: editUserData.phone.trim() || null,
        role: editUserData.role,
        isActive: editUserData.isActive,
        password: editUserData.password.trim() || undefined, // solo si se llenó
      });

      // Reemplazar en lista local
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? { ...u, ...updated } : u)));

      toast.success("Usuario actualizado correctamente");
      closeEditDialog();
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message ?? "No se pudo actualizar el usuario");
    }
};






  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-display font-bold">Gestión de Usuarios</h1>
            <p className="text-muted-foreground">Administra los usuarios del sistema</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="h-4 w-4 mr-2" />
                Nuevo Usuario
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Crear Nuevo Usuario</DialogTitle>
                <DialogDescription>
                  Ingresa los datos del nuevo usuario
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nombre Completo *</Label>
                  <Input
                    id="name"
                    value={newUserData.name}
                    onChange={(e) => setNewUserData({ ...newUserData, name: e.target.value })}
                    placeholder="Nombre del usuario"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUserData.email}
                    onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
                    placeholder="email@ejemplo.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Contraseña *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newUserData.password}
                    onChange={(e) => setNewUserData({ ...newUserData, password: e.target.value })}
                    placeholder="Mín. 10 caracteres y 1 especial"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Teléfono</Label>
                  <Input
                    id="phone"
                    value={newUserData.phone}
                    onChange={(e) => setNewUserData({ ...newUserData, phone: e.target.value })}
                    placeholder="+506 0000-0000"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Rol</Label>
                  <Select
                    value={newUserData.role}
                    onValueChange={(value) =>
                      setNewUserData({ ...newUserData, role: value as "admin" | "customer" })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="customer">Cliente</SelectItem>
                      <SelectItem value="admin">Administrador</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleCreateUser}>Crear Usuario</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Desactivar Usuario</DialogTitle>
              <DialogDescription>
                {userToDelete ? (
                  <>
                    Se desactivará el usuario{" "}
                    <span className="font-medium">{userToDelete.name}</span> (
                    {userToDelete.email}). Esta acción no elimina el registro, solo lo
                    deja inactivo.
                  </>
                ) : (
                  "Esta acción no se puede deshacer."
                )}
              </DialogDescription>
            </DialogHeader>

            <DialogFooter>
              <Button variant="outline" onClick={closeDeleteDialog}>
                Cancelar
              </Button>
              <Button variant="destructive" onClick={confirmDeleteUser}>
                Desactivar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Editar Usuario</DialogTitle>
              <DialogDescription>
                Modifica los datos del usuario. Si no se ingresa contraseña, no se modifica.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Nombre Completo *</Label>
                <Input
                  id="edit-name"
                  value={editUserData.name}
                  onChange={(e) => setEditUserData({ ...editUserData, name: e.target.value })}
                  placeholder="Nombre del usuario"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-email">Email *</Label>
                <Input
                  id="edit-email"
                  type="email"
                  value={editUserData.email}
                  onChange={(e) => setEditUserData({ ...editUserData, email: e.target.value })}
                  placeholder="email@ejemplo.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-phone">Teléfono</Label>
                <Input
                  id="edit-phone"
                  value={editUserData.phone}
                  onChange={(e) => setEditUserData({ ...editUserData, phone: e.target.value })}
                  placeholder="+506 0000-0000"
                />
              </div>

              <div className="space-y-2">
                <Label>Rol</Label>
                <Select
                  value={editUserData.role}
                  onValueChange={(value) =>
                    setEditUserData({ ...editUserData, role: value as "admin" | "customer" })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">Cliente</SelectItem>
                    <SelectItem value="admin">Administrador</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Estado</Label>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={editUserData.isActive}
                    onCheckedChange={(checked) => setEditUserData({ ...editUserData, isActive: checked })}
                  />
                  <span className="text-sm">{editUserData.isActive ? "Activo" : "Inactivo"}</span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-password">Nueva Contraseña</Label>
                <Input
                  id="edit-password"
                  type="password"
                  value={editUserData.password}
                  onChange={(e) => setEditUserData({ ...editUserData, password: e.target.value })}
                  placeholder="Opcional (mín. 10 y 1 especial)"
                />
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={closeEditDialog}>
                Cancelar
              </Button>
              <Button onClick={handleUpdateUser}>
                Guardar Cambios
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>



        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nombre o email..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los roles</SelectItem>
                  <SelectItem value="admin">Administradores</SelectItem>
                  <SelectItem value="customer">Clientes</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="active">Activos</SelectItem>
                  <SelectItem value="inactive">Inactivos</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Rol</TableHead>
                  <TableHead>Teléfono</TableHead>
                  <TableHead className="text-center">Reservas</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Registro</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                    Cargando usuarios...
                  </TableCell>
                </TableRow>
                ) : error ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-32 text-center text-destructive">
                    Error cargando usuarios. Verificar token ADMIN.
                  </TableCell>
                </TableRow>
                ) : filteredUsers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-32 text-center">
                      <div className="flex flex-col items-center gap-2">
                        <Users className="h-8 w-8 text-muted-foreground" />
                        <p className="text-muted-foreground">No se encontraron usuarios</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredUsers.map((user) => {
                    const RoleIcon = roleConfig[user.role].icon;
                    return (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar>
                              <AvatarFallback className="bg-primary/10 text-primary">
                                {user.name.charAt(0)}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{user.name}</p>
                              <p className="text-xs text-muted-foreground">{user.email}</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <RoleIcon className={`h-4 w-4 ${roleConfig[user.role].color}`} />
                            <span className="text-sm">{roleConfig[user.role].label}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          {user.phone || <span className="text-muted-foreground">—</span>}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge variant="secondary">{user.reservationsCount}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Switch
                              checked={user.isActive}
                              onCheckedChange={() => handleToggleStatus(user.id, user.isActive)}
                              disabled={user.role === "admin"}
                            />
                            <span className="text-sm">
                              {user.isActive ? "Activo" : "Inactivo"}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {user.createdAt}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem onClick={() => openEditDialog(user)} className="cursor-pointer">
                                <Edit className="h-4 w-4 mr-2" />
                                Editar
                              </DropdownMenuItem>
                              {user.role !== "admin" && (
                                <>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem
                                    onClick={() => openDeleteDialog(user)}
                                    className="text-destructive cursor-pointer"
                                  >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    Eliminar
                                  </DropdownMenuItem>
                                </>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Summary */}
        <div className="text-sm text-muted-foreground">
          Mostrando {filteredUsers.length} de {users.length} usuarios
        </div>
      </div>
    </AdminLayout>
  );
};

export default UsersPage;
