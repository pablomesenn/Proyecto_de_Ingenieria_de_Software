import { apiGet, apiPost, apiPut, apiDelete } from "./http";

export type CatalogCategory = {
  _id: string;
  name: string;
  slug: string;
  productCount: number;
};

export type CatalogTag = {
  _id: string;
  name: string;
  slug: string;
  productCount: number;
};

export async function fetchCatalogCategories(): Promise<CatalogCategory[]> {
  const data = await apiGet<{ categories: CatalogCategory[] }>("/api/catalog/categories");
  return data.categories ?? [];
}

export async function createCatalogCategory(name: string): Promise<CatalogCategory> {
  const data = await apiPost<{ category: CatalogCategory }>("/api/catalog/categories", { name });
  return data.category;
}

export async function updateCatalogCategory(id: string, name: string): Promise<CatalogCategory> {
  const data = await apiPut<{ category: CatalogCategory }>(`/api/catalog/categories/${id}`, { name });
  return data.category;
}

export async function deleteCatalogCategory(id: string): Promise<void> {
  await apiDelete(`/api/catalog/categories/${id}`);
}

export async function fetchCatalogTags(): Promise<CatalogTag[]> {
  const data = await apiGet<{ tags: CatalogTag[] }>("/api/catalog/tags");
  return data.tags ?? [];
}

export async function createCatalogTag(name: string): Promise<CatalogTag> {
  const data = await apiPost<{ tag: CatalogTag }>("/api/catalog/tags", { name });
  return data.tag;
}

export async function updateCatalogTag(id: string, name: string): Promise<CatalogTag> {
  const data = await apiPut<{ tag: CatalogTag }>(`/api/catalog/tags/${id}`, { name });
  return data.tag;
}

export async function deleteCatalogTag(id: string): Promise<void> {
  await apiDelete(`/api/catalog/tags/${id}`);
}
