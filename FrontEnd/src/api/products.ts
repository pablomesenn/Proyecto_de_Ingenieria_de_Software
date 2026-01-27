import { apiGet, apiPost, apiPut, apiDelete } from "./http";

// Types based on backend schemas
export type ProductCategory =
  | "Porcelanato"
  | "Cerámica"
  | "Mármol"
  | "Granito"
  | "Madera"
  | "Laminados"
  | "Ceramica";

export type ProductTag =
  | "Interior"
  | "Exterior"
  | "Antideslizante"
  | "Premium"
  | "Rustico"
  | "Moderno"
  | string;

export interface ProductVariant {
  _id: string;
  size: string;
  stock: number;
  available: boolean;
  reserved: number;
}

export interface Product {
  _id: string;
  name?: string;
  nombre?: string; // Spanish field name
  description?: string;
  descripcion_embalaje?: string; // Spanish field name
  category?: ProductCategory;
  categoria?: ProductCategory; // Spanish field name
  tags?: ProductTag[];
  image_url?: string;
  imagen_url?: string; // Spanish field name
  variants?: ProductVariant[];
  variantes?: ProductVariant[]; // Spanish field name
  estado?: "activo" | "inactivo" | string;
  disponible?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ProductSearchParams {
  search_text?: string;
  categoria?: ProductCategory;
  tags?: ProductTag[];
  disponibilidad?: boolean;
  skip?: number;
  limit?: number;
}

export interface ProductsResponse {
  products: Product[];
  count: number;
}

export interface CategoriesResponse {
  categories: ProductCategory[];
}

export interface TagsResponse {
  tags: ProductTag[];
}

// API functions
export async function searchProducts(
  params: ProductSearchParams = {},
): Promise<ProductsResponse> {
  const queryParams = new URLSearchParams();

  if (params.search_text) queryParams.append("search_text", params.search_text);
  if (params.categoria) queryParams.append("categoria", params.categoria);
  if (params.tags && params.tags.length > 0) {
    params.tags.forEach((tag) => queryParams.append("tags", tag));
  }
  if (params.disponibilidad !== undefined)
    queryParams.append("disponibilidad", String(params.disponibilidad));
  if (params.skip !== undefined)
    queryParams.append("skip", String(params.skip));
  if (params.limit !== undefined)
    queryParams.append("limit", String(params.limit));

  const queryString = queryParams.toString();
  const path = `/api/products/search${queryString ? `?${queryString}` : ""}`;

  return apiGet<ProductsResponse>(path);
}

export async function getProducts(
  skip: number = 0,
  limit: number = 20,
): Promise<ProductsResponse> {
  return apiGet<ProductsResponse>(`/api/products/?skip=${skip}&limit=${limit}`);
}

export async function getProductDetail(productId: string): Promise<Product> {
  return apiGet<Product>(`/api/products/${productId}`);
}

export interface CreateProductRequest {
  nombre: string;
  imagen_url: string;
  categoria: string;
  tags?: string[];
  estado?: "activo" | "inactivo" | "agotado";
  descripcion_embalaje?: string;
  variantes: Array<{
    tamano_pieza: string;
    unidad?: string;
    precio?: number;
    stock_inicial?: number;
  }>;
}

export interface UpdateProductRequest {
  nombre?: string;
  imagen_url?: string;
  categoria?: string;
  tags?: string[];
  estado?: "activo" | "inactivo" | "agotado";
  descripcion_embalaje?: string;
  variantes?: Array<{
    _id?: string;
    tamano_pieza: string;
    unidad?: string;
    precio?: number;
    stock_inicial?: number;
  }>;
}

export async function createProduct(
  data: CreateProductRequest
): Promise<{ message: string; product: Product }> {
  return apiPost<{ message: string; product: Product }>("/api/products/", data);
}

export async function updateProduct(
  productId: string,
  data: UpdateProductRequest
): Promise<{ message: string; product: Product }> {
  return apiPut<{ message: string; product: Product }>(`/api/products/${productId}`, data);
}

export async function updateProductState(
  productId: string,
  estado: "activo" | "inactivo" | "agotado"
): Promise<{ message: string }> {
  return apiPut<{ message: string }>(`/api/products/${productId}/state`, { estado });
}

export async function deleteProduct(
  productId: string
): Promise<{ message: string }> {
  return apiDelete<{ message: string }>(`/api/products/${productId}`);
}

export async function getCategories(): Promise<CategoriesResponse> {
  return apiGet<CategoriesResponse>("/api/products/categories");
}

export async function getTags(): Promise<TagsResponse> {
  return apiGet<TagsResponse>("/api/products/tags");
}

// Helper function to map backend product to UI format
// Handles both English and Spanish field names
export function mapProductToUI(product: Product) {
  // Handle case where product might not have all fields
  if (!product) {
    console.error("Product is null or undefined");
    return null;
  }

  // Handle both Spanish and English field names
  const name = product.name || product.nombre || "Producto sin nombre";
  const category = product.category || product.categoria || "Sin categoría";
  const description = product.description || product.descripcion_embalaje || "";
  const imageUrl =
    product.image_url ||
    product.imagen_url ||
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop";

  // Handle variants - could be in different formats
  let variants = [];
  if (Array.isArray(product.variants)) {
    variants = product.variants;
  } else if (Array.isArray(product.variantes)) {
    variants = product.variantes;
  }

  // Map variants with proper field names
  const mappedVariants = variants.map((v) => {
    // Handle both English and Spanish field names for size
    const size =
      v.size || (v as any).tamano_pieza || (v as any).tamaño_pieza || "";

    return {
      id: v._id || "",
      size: size,
      stock: v.stock || 0,
      available: v.available !== undefined ? v.available : false,
      reserved: v.reserved || 0,
    };
  });

  // Determine availability - check if any variant has stock
  const estado = product.estado || "activo";
  const hasStock = mappedVariants.some((v) => v.stock > 0);
  const available =
    product.disponible !== undefined
      ? product.disponible
      : (estado === "activo" || estado === "ACTIVE") && hasStock;

  return {
    id: product._id || "",
    name: name,
    description: description,
    category: category as string,
    tags: Array.isArray(product.tags) ? product.tags : [],
    image: imageUrl,
    available: available,
    status: estado,
    variants: mappedVariants,
    createdAt: product.created_at || "",
    updatedAt: product.updated_at || "",
  };
}

// Get product with real-time inventory data
export async function getProductWithInventory(productId: string) {
  const product = await getProductDetail(productId);
  return mapProductToUI(product);
}