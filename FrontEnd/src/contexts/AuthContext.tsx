import React, { createContext, useContext, useState, ReactNode } from "react";

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
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock admin user for demo purposes
const mockAdminUser: User = {
  id: "admin-1",
  email: "admin@pisoskermy.com",
  name: "Administrador",
  phone: "+506 2643-1234",
  role: "admin",
  createdAt: new Date("2024-01-01"),
};

const mockCustomerUser: User = {
  id: "customer-1",
  email: "cliente@email.com",
  name: "Juan Pérez",
  phone: "+506 8888-1234",
  role: "customer",
  createdAt: new Date("2024-06-15"),
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(mockAdminUser); // Default to admin for demo

  const isAuthenticated = user !== null;
  const isAdmin = user?.role === "admin";

  const login = async (email: string, password: string): Promise<boolean> => {
    // Mock login - in production this would validate against backend
    if (email.includes("admin")) {
      setUser(mockAdminUser);
      return true;
    }
    setUser(mockCustomerUser);
    return true;
  };

  const logout = () => {
    setUser(null);
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
