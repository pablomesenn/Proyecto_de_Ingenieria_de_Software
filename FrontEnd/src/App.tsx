import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { WishlistProvider } from "./contexts/WishlistContext";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import Catalog from "./pages/Catalog";
import ProductDetail from "./pages/ProductDetail";
import Wishlist from "./pages/Wishlist";
import Reservations from "./pages/Reservations";
import About from "./pages/About";
import Contact from "./pages/Contact";
import FAQ from "./pages/FAQ";
import NotFound from "./pages/NotFound";
import Profile from "./pages/Profile";

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
import AdminProfile from "./pages/admin/Profile";

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
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/faq" element={<FAQ />} />
              
              {/* Protected route - Profile for all authenticated users */}
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />
              
              {/* Admin routes - Protected */}
              <Route path="/admin" element={
                <ProtectedRoute requireAdmin>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/admin/products" element={
                <ProtectedRoute requireAdmin>
                  <Products />
                </ProtectedRoute>
              } />
              <Route path="/admin/products/new" element={
                <ProtectedRoute requireAdmin>
                  <ProductForm />
                </ProtectedRoute>
              } />
              <Route path="/admin/products/:id" element={
                <ProtectedRoute requireAdmin>
                  <ProductForm />
                </ProtectedRoute>
              } />
              <Route path="/admin/categories" element={
                <ProtectedRoute requireAdmin>
                  <Categories />
                </ProtectedRoute>
              } />
              <Route path="/admin/inventory" element={
                <ProtectedRoute requireAdmin>
                  <Inventory />
                </ProtectedRoute>
              } />
              <Route path="/admin/inventory/adjust" element={
                <ProtectedRoute requireAdmin>
                  <InventoryAdjust />
                </ProtectedRoute>
              } />
              <Route path="/admin/inventory/history" element={
                <ProtectedRoute requireAdmin>
                  <InventoryHistory />
                </ProtectedRoute>
              } />
              <Route path="/admin/reservations" element={
                <ProtectedRoute requireAdmin>
                  <AdminReservations />
                </ProtectedRoute>
              } />
              <Route path="/admin/reservations/:id" element={
                <ProtectedRoute requireAdmin>
                  <ReservationDetail />
                </ProtectedRoute>
              } />
              <Route path="/admin/users" element={
                <ProtectedRoute requireAdmin>
                  <Users />
                </ProtectedRoute>
              } />
              <Route path="/admin/users/new" element={
                <ProtectedRoute requireAdmin>
                  <UserForm />
                </ProtectedRoute>
              } />
              <Route path="/admin/users/:id" element={
                <ProtectedRoute requireAdmin>
                  <UserForm />
                </ProtectedRoute>
              } />
              <Route path="/admin/export" element={
                <ProtectedRoute requireAdmin>
                  <Export />
                </ProtectedRoute>
              } />
              <Route path="/admin/profile" element={
                <ProtectedRoute requireAdmin>
                  <AdminProfile />
                </ProtectedRoute>
              } />
              
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