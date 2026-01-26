import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { login as loginService, logout as logoutService } from "@/api/auth";
import { getProfile } from "@/api/users";

export type UserRole = "admin" | "customer";

export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  role: UserRole;
  avatar?: string;
  createdAt: Date;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; role?: UserRole }>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;
  const isAdmin = user?.role === "admin";

  // Verificar si hay sesión al cargar
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      // Intentar obtener perfil del usuario
      getProfile()
        .then((profile) => {
          setUser({
            id: profile.id,
            email: profile.email,
            name: profile.name,
            phone: profile.phone,
            role: profile.role as UserRole,
            createdAt: new Date(),
          });
        })
        .catch(() => {
          // Token inválido, limpiar
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; role?: UserRole }> => {
    try {
      const response = await loginService(email, password);
      
      const userRole: UserRole = response.user.role === "ADMIN" ? "admin" : "customer";
      
      setUser({
        id: response.user._id,
        email: response.user.email,
        name: response.user.name || "",
        phone: response.user.phone || "",
        role: userRole,
        createdAt: new Date(),
      });
      
      return { success: true, role: userRole };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false };
    }
  };

  const logout = async () => {
    try {
      await logoutService();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
    }
  };

  const updateProfile = (data: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...data });
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isAdmin,
        isLoading,
        login,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}