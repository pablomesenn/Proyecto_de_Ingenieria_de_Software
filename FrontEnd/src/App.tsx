import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { WishlistProvider } from "./contexts/WishlistContext";
import { AuthProvider } from "./contexts/AuthContext";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import Catalog from "./pages/Catalog";
import ProductDetail from "./pages/ProductDetail";
import Wishlist from "./pages/Wishlist";
import Reservations from "./pages/Reservations";
import NotFound from "./pages/NotFound";

// Admin pages
import Dashboard from "./pages/admin/Dashboard";
import Products from "./pages/admin/Products";
import ProductForm from "./pages/admin/ProductForm";
import Categories from "./pages/admin/Categories";
import Inventory from "./pages/admin/Inventory";
import InventoryAdjust from "./pages/admin/InventoryAdjust";
import InventoryHistory from "./pages/admin/InventoryHistory";
import AdminReservations from "./pages/admin/AdminReservations";
import ReservationDetail from "./pages/admin/ReservationDetail";
import Users from "./pages/admin/Users";
import UserForm from "./pages/admin/UserForm";
import Export from "./pages/admin/Export";
import Profile from "./pages/admin/Profile";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <WishlistProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/catalog" element={<Catalog />} />
              <Route path="/catalog/:id" element={<ProductDetail />} />
              <Route path="/wishlist" element={<Wishlist />} />
              <Route path="/reservations" element={<Reservations />} />
              
              {/* Admin routes */}
              <Route path="/admin" element={<Dashboard />} />
              <Route path="/admin/products" element={<Products />} />
              <Route path="/admin/products/new" element={<ProductForm />} />
              <Route path="/admin/products/:id" element={<ProductForm />} />
              <Route path="/admin/categories" element={<Categories />} />
              <Route path="/admin/inventory" element={<Inventory />} />
              <Route path="/admin/inventory/adjust" element={<InventoryAdjust />} />
              <Route path="/admin/inventory/history" element={<InventoryHistory />} />
              <Route path="/admin/reservations" element={<AdminReservations />} />
              <Route path="/admin/reservations/:id" element={<ReservationDetail />} />
              <Route path="/admin/users" element={<Users />} />
              <Route path="/admin/users/new" element={<UserForm />} />
              <Route path="/admin/users/:id" element={<UserForm />} />
              <Route path="/admin/export" element={<Export />} />
              <Route path="/admin/profile" element={<Profile />} />
              
              {/* Catch-all */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </WishlistProvider>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;