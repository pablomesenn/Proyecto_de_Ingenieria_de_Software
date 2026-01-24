"""
Servicio de Wishlist
Implementa la lógica de negocio para gestión de wishlist
Casos de Uso:
- CU-006: Gestionar wishlist
- CU-007: Mover de wishlist a reserva
"""

from app.models.wishlist import Wishlist, WishlistItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.user import User
from app.middleware.error_handler import ValidationError, NotFoundError, ConflictError


class WishlistService:
    """
    Servicio para gestión de wishlist
    Implementa RF-10, RF-11, RF-12, RF-13
    """

    @staticmethod
    def get_or_create_wishlist(user_id):
        """
        Obtiene o crea la wishlist del usuario
        Cada usuario tiene una única wishlist

        Args:
            user_id: ID del usuario

        Returns:
            Wishlist: Wishlist del usuario
        """
        try:
            user = User.objects.get(id=user_id)
            wishlist = Wishlist.objects.get(usuario_id=user)
        except Wishlist.DoesNotExist:
            wishlist = Wishlist(usuario_id=user)
            wishlist.save()

        return wishlist

    @staticmethod
    def get_wishlist(user_id, include_availability=True):
        """
        Obtiene la wishlist del usuario con disponibilidad calculada
        Implementa RF-12: Wishlist con disponibilidad en tiempo real

        Args:
            user_id: ID del usuario
            include_availability: Si incluir disponibilidad

        Returns:
            dict: Wishlist con disponibilidad por ítem
        """
        wishlist = WishlistService.get_or_create_wishlist(user_id)
        wishlist_dict = wishlist.to_dict(include_products=True)

        if include_availability:
            # Agregar disponibilidad a cada ítem
            for item in wishlist_dict['items']:
                availability = WishlistService._get_item_availability(
                    item['producto_id'],
                    item['variante_index']
                )
                item['disponibilidad'] = availability

        return wishlist_dict

    @staticmethod
    def add_item(user_id, producto_id, variante_index, cantidad=1):
        """
        Agrega un ítem a la wishlist
        Implementa RF-11: Detección de duplicados y consolidación

        Args:
            user_id: ID del usuario
            producto_id: ID del producto
            variante_index: Índice de la variante
            cantidad: Cantidad a agregar

        Returns:
            dict: Resultado de la operación
        """
        # Validar que el producto existe y está visible
        try:
            producto = Product.objects.get(id=producto_id)
        except Product.DoesNotExist:
            raise NotFoundError("Producto no encontrado")

        if not producto.is_visible():
            raise ValidationError("Producto no disponible")

        # Validar que la variante existe
        if variante_index >= len(producto.variantes):
            raise ValidationError("Variante no válida")

        # Validar cantidad
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")

        # Obtener o crear wishlist
        wishlist = WishlistService.get_or_create_wishlist(user_id)

        # Agregar o actualizar (consolidación automática)
        action = wishlist.add_or_update_item(producto_id, variante_index, cantidad)

        return {
            'action': action,  # 'added' o 'updated'
            'message': 'Producto consolidado en wishlist' if action == 'updated' else 'Producto agregado a wishlist',
            'wishlist': wishlist.to_dict(include_products=True)
        }

    @staticmethod
    def update_item(user_id, producto_id, variante_index, cantidad):
        """
        Actualiza la cantidad de un ítem

        Args:
            user_id: ID del usuario
            producto_id: ID del producto
            variante_index: Índice de la variante
            cantidad: Nueva cantidad

        Returns:
            dict: Resultado de la operación
        """
        if cantidad < 0:
            raise ValidationError("La cantidad no puede ser negativa")

        wishlist = WishlistService.get_or_create_wishlist(user_id)

        success = wishlist.update_item_quantity(producto_id, variante_index, cantidad)

        if not success:
            raise NotFoundError("Ítem no encontrado en la wishlist")

        return {
            'message': 'Ítem eliminado de wishlist' if cantidad == 0 else 'Cantidad actualizada',
            'wishlist': wishlist.to_dict(include_products=True)
        }

    @staticmethod
    def remove_item(user_id, producto_id, variante_index):
        """
        Elimina un ítem de la wishlist

        Args:
            user_id: ID del usuario
            producto_id: ID del producto
            variante_index: Índice de la variante

        Returns:
            dict: Resultado de la operación
        """
        wishlist = WishlistService.get_or_create_wishlist(user_id)

        success = wishlist.remove_item(producto_id, variante_index)

        if not success:
            raise NotFoundError("Ítem no encontrado en la wishlist")

        return {
            'message': 'Ítem eliminado de wishlist',
            'wishlist': wishlist.to_dict(include_products=True)
        }

    @staticmethod
    def clear_wishlist(user_id):
        """
        Vacía completamente la wishlist

        Args:
            user_id: ID del usuario

        Returns:
            dict: Resultado de la operación
        """
        wishlist = WishlistService.get_or_create_wishlist(user_id)
        wishlist.clear()

        return {
            'message': 'Wishlist vaciada',
            'wishlist': wishlist.to_dict()
        }

    @staticmethod
    def validate_for_reservation(user_id):
        """
        Valida que la wishlist pueda convertirse a reserva
        Implementa RF-13: Validación antes de convertir a reserva

        Args:
            user_id: ID del usuario

        Returns:
            dict: {
                'valid': bool,
                'items': [...],  # Ítems válidos
                'errors': [...]  # Ítems con problemas
            }
        """
        wishlist = WishlistService.get_or_create_wishlist(user_id)

        if wishlist.get_total_items() == 0:
            raise ValidationError("La wishlist está vacía")

        valid_items = []
        error_items = []

        for item in wishlist.items:
            producto_id = str(item.producto_id.id)
            variante_index = item.variante_index
            cantidad = item.cantidad

            # Verificar disponibilidad
            availability = WishlistService._get_item_availability(
                producto_id,
                variante_index
            )

            if availability['disponibilidad'] >= cantidad:
                valid_items.append({
                    'producto_id': producto_id,
                    'variante_index': variante_index,
                    'cantidad': cantidad,
                    'disponibilidad': availability['disponibilidad']
                })
            else:
                error_items.append({
                    'producto_id': producto_id,
                    'variante_index': variante_index,
                    'cantidad_solicitada': cantidad,
                    'disponibilidad': availability['disponibilidad'],
                    'error': 'Disponibilidad insuficiente'
                })

        return {
            'valid': len(error_items) == 0,
            'items': valid_items,
            'errors': error_items
        }

    @staticmethod
    def _get_item_availability(producto_id, variante_index):
        """
        Obtiene disponibilidad de un ítem específico

        Args:
            producto_id: ID del producto
            variante_index: Índice de la variante

        Returns:
            dict: Información de disponibilidad
        """
        try:
            inventory = Inventory.objects.get(
                producto_id=producto_id,
                variante_index=variante_index
            )

            return {
                'stock_total': inventory.stock_total,
                'stock_retenido': inventory.stock_retenido,
                'disponibilidad': inventory.get_disponibilidad()
            }
        except Inventory.DoesNotExist:
            return {
                'stock_total': 0,
                'stock_retenido': 0,
                'disponibilidad': 0
            }
