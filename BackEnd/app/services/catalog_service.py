import logging
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self):
        self.repo = CatalogRepository()
        self.product_repo = ProductRepository()

    # ------------------------
    # LIST
    # ------------------------
    def list_categories(self):
        # 1) Importar/sincronizar desde productos
        product_categories = self.product_repo.get_categories() or []
        existing = {c["name"] for c in self.repo.list_categories()}

        for name in product_categories:
            if name not in existing:
                try:
                    self.repo.create_category(name)
                except Exception:
                    pass

        # 2) Listar catálogo y contar productos por el valor real guardado en productos (categoria=name)
        categories = self.repo.list_categories()
        for c in categories:
            c["productCount"] = self.product_repo.count_by_category_value(c["name"])
        return categories

    def list_tags(self):
        product_tags = self.product_repo.get_tags() or []
        existing = {t["name"] for t in self.repo.list_tags()}

        for name in product_tags:
            if name not in existing:
                try:
                    self.repo.create_tag(name)
                except Exception:
                    pass

        tags = self.repo.list_tags()
        for t in tags:
            t["productCount"] = self.product_repo.count_by_tag_value(t["name"])
        return tags

    # ------------------------
    # CREATE / UPDATE
    # ------------------------
    def create_category(self, name: str, admin_id: str):
        cat = self.repo.create_category(name)
        self._audit(admin_id, "create_category", cat["_id"], {"name": cat["name"]})
        return cat

    def update_category(self, category_id: str, name: str, admin_id: str):
        cat = self.repo.update_category(category_id, name)
        self._audit(admin_id, "update_category", cat["_id"], {"name": cat["name"]})
        return cat

    def create_tag(self, name: str, admin_id: str):
        t = self.repo.create_tag(name)
        self._audit(admin_id, "create_tag", t["_id"], {"name": t["name"]})
        return t

    def update_tag(self, tag_id: str, name: str, admin_id: str):
        t = self.repo.update_tag(tag_id, name)
        self._audit(admin_id, "update_tag", t["_id"], {"name": t["name"]})
        return t

    # ------------------------
    # DELETE (por ID)
    # ------------------------
    def delete_category(self, category_id: str, admin_id: str):
        cat = self.repo.get_category_by_id(category_id)
        if not cat:
            raise ValueError("Categoría no encontrada")

        count = self.product_repo.count_by_category_value(slug=cat.get("slug"), name=cat.get("name"))
        if count > 0:
            raise ValueError("Categoría en uso")

        ok = self.repo.delete_category(category_id)
        self._audit(admin_id, "delete_category", category_id, {"name": cat.get("name"), "slug": cat.get("slug")})
        return ok

    def delete_tag(self, tag_id: str, admin_id: str):
        tag = self.repo.get_tag_by_id(tag_id)
        if not tag:
            raise ValueError("Etiqueta no encontrada")

        count = self.product_repo.count_by_tag_value(slug=tag.get("slug"), name=tag.get("name"))
        if count > 0:
            raise ValueError("Etiqueta en uso")

        ok = self.repo.delete_tag(tag_id)
        self._audit(admin_id, "delete_tag", tag_id, {"name": tag.get("name"), "slug": tag.get("slug")})
        return ok

    # ------------------------
    # AUDIT
    # ------------------------
    def _audit(self, actor_id, action, entity_id, details=None):
        from app.config.database import get_db
        from bson import ObjectId
        from datetime import datetime

        db = get_db()
        db.audit_logs.insert_one({
            "actor_id": ObjectId(actor_id) if actor_id else None,
            "action": action,
            "entity_type": "catalog",
            "entity_id": ObjectId(entity_id) if entity_id else None,
            "details": details,
            "timestamp": datetime.utcnow()
        })

    # ------------------------
    # Para Testing
    # ------------------------

    def list_public_products(self):
        """
        Productos visibles al público
        """
        products = list(self.product_repo.products.find({
            "state": {"$ne": "eliminado"}
        }))

        return products

