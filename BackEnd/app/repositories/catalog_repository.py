from bson import ObjectId
from datetime import datetime
from app.config.database import get_db

class CatalogRepository:
    def __init__(self):
        db = get_db()
        self.categories = db.categories
        self.tags = db.tags
        self.products = db.products

    # ---------- Helpers ----------
    def _slugify(self, name: str) -> str:
        return name.strip().lower().replace(" ", "-")

    # ---------- Categories ----------
    def list_categories(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "products",
                    "let": {"catName": "$name"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$categoria", "$$catName"]}}},
                        {"$count": "count"}
                    ],
                    "as": "usage"
                }
            },
            {
                "$addFields": {
                    "productCount": {
                        "$ifNull": [{"$arrayElemAt": ["$usage.count", 0]}, 0]
                    }
                }
            },
            {"$project": {"usage": 0}},
            {"$sort": {"name": 1}}
        ]
        return list(self.categories.aggregate(pipeline))

    def create_category(self, name: str):
        name = name.strip()
        slug = self._slugify(name)

        # Unicidad por nombre (case-insensitive)
        exists = self.categories.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if exists:
            raise ValueError("Ya existe una categoría con ese nombre")

        doc = {
            "name": name,
            "slug": slug,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        res = self.categories.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    def update_category(self, category_id: str, new_name: str):
        new_name = new_name.strip()
        new_slug = self._slugify(new_name)

        cat = self.categories.find_one({"_id": ObjectId(category_id)})
        if not cat:
            raise ValueError("Categoría no encontrada")

        # Unicidad
        exists = self.categories.find_one({
            "_id": {"$ne": ObjectId(category_id)},
            "name": {"$regex": f"^{new_name}$", "$options": "i"}
        })
        if exists:
            raise ValueError("Ya existe una categoría con ese nombre")

        old_name = cat["name"]

        self.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": {"name": new_name, "slug": new_slug, "updated_at": datetime.utcnow()}}
        )

        # Propagar a productos (mantener consistencia de filtros)
        if old_name != new_name:
            self.products.update_many(
                {"categoria": old_name},
                {"$set": {"categoria": new_name, "updated_at": datetime.utcnow()}}
            )

        return self.categories.find_one({"_id": ObjectId(category_id)})

    def delete_category(self, category_id: str):
        cat = self.categories.find_one({"_id": ObjectId(category_id)})
        if not cat:
            raise ValueError("Categoría no encontrada")

        in_use = self.products.count_documents({"categoria": cat["name"]})
        if in_use > 0:
            # flujo alterno: está en uso -> bloquear
            raise RuntimeError(f"Categoría en uso ({in_use} productos). Reasigne antes de eliminar.")

        res = self.categories.delete_one({"_id": ObjectId(category_id)})
        return res.deleted_count > 0

    # ---------- Tags ----------
    def list_tags(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "products",
                    "let": {"tagName": "$name"},
                    "pipeline": [
                        {"$match": {"$expr": {"$in": ["$$tagName", "$tags"]}}},
                        {"$count": "count"}
                    ],
                    "as": "usage"
                }
            },
            {
                "$addFields": {
                    "productCount": {
                        "$ifNull": [{"$arrayElemAt": ["$usage.count", 0]}, 0]
                    }
                }
            },
            {"$project": {"usage": 0}},
            {"$sort": {"name": 1}}
        ]
        return list(self.tags.aggregate(pipeline))

    def create_tag(self, name: str):
        name = name.strip()
        slug = self._slugify(name)

        exists = self.tags.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if exists:
            raise ValueError("Ya existe una etiqueta con ese nombre")

        doc = {
            "name": name,
            "slug": slug,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        res = self.tags.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    def update_tag(self, tag_id: str, new_name: str):
        new_name = new_name.strip()
        new_slug = self._slugify(new_name)

        t = self.tags.find_one({"_id": ObjectId(tag_id)})
        if not t:
            raise ValueError("Etiqueta no encontrada")

        exists = self.tags.find_one({
            "_id": {"$ne": ObjectId(tag_id)},
            "name": {"$regex": f"^{new_name}$", "$options": "i"}
        })
        if exists:
            raise ValueError("Ya existe una etiqueta con ese nombre")

        old_name = t["name"]

        self.tags.update_one(
            {"_id": ObjectId(tag_id)},
            {"$set": {"name": new_name, "slug": new_slug, "updated_at": datetime.utcnow()}}
        )

        # Propagar a productos: reemplazar string dentro del array tags
        if old_name != new_name:
            self.products.update_many(
                {"tags": old_name},
                [
                    {
                        "$set": {
                            "tags": {
                                "$map": {
                                    "input": "$tags",
                                    "as": "tg",
                                    "in": {"$cond": [{"$eq": ["$$tg", old_name]}, new_name, "$$tg"]}
                                }
                            },
                            "updated_at": datetime.utcnow()
                        }
                    }
                ]
            )

        return self.tags.find_one({"_id": ObjectId(tag_id)})

    def delete_tag(self, tag_id: str):
        t = self.tags.find_one({"_id": ObjectId(tag_id)})
        if not t:
            raise ValueError("Etiqueta no encontrada")

        in_use = self.products.count_documents({"tags": t["name"]})
        if in_use > 0:
            raise RuntimeError(f"Etiqueta en uso ({in_use} productos). Remueva/Reasigne antes de eliminar.")

        res = self.tags.delete_one({"_id": ObjectId(tag_id)})
        return res.deleted_count > 0
    
    def get_category_by_id(self, category_id: str):
        return self.categories.find_one({"_id": ObjectId(category_id)})

    def get_tag_by_id(self, tag_id: str):
        return self.tags.find_one({"_id": ObjectId(tag_id)})
