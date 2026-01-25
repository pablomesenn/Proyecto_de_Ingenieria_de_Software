from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_repository import VariantRepository
from app.repositories.inventory_repository import InventoryRepository
from app.services.reservation_service import ReservationService
import logging

logger = logging.getLogger(__name__)


class WishlistService:
    def __init__(self):
        self.wishlist_repo = WishlistRepository()
        self.variant_repo = VariantRepository()
        self.inventory_repo = InventoryRepository()

    def get_wishlist(self, user_id):
        """
        Obtiene la wishlist de un usuario con disponibilidad calculada (CU-006, RF-12)
        """
        items = self.wishlist_repo.get_items_with_details(user_id)

        return {
            'user_id': user_id,
            'items': items,
            'total_items': len(items)
        }

    def add_item(self, user_id, variant_id, quantity=1):
        """
        Agrega un item a la wishlist (CU-006, RF-10, RF-11)
        """
        # Validar que la variante existe
        variant = self.variant_repo.find_by_id(variant_id)
        if not variant:
            raise ValueError("Variante no encontrada")

        # Validar cantidad
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        # Agregar item
        wishlist = self.wishlist_repo.add_item(user_id, variant_id, quantity)

        return self.get_wishlist(user_id)

    def update_item(self, user_id, item_id, quantity):
        """
        Actualiza la cantidad de un item en la wishlist (CU-006, RF-10)
        """
        # Validar cantidad
        if quantity < 0:
            raise ValueError("La cantidad no puede ser negativa")

        if quantity == 0:
            # Si la cantidad es 0, eliminar el item
            return self.remove_item(user_id, item_id)

        # Actualizar cantidad
        success = self.wishlist_repo.update_item_quantity(user_id, item_id, quantity)

        if not success:
            raise ValueError("Item no encontrado en la wishlist")

        return self.get_wishlist(user_id)

    def remove_item(self, user_id, item_id):
        success = self.wishlist_repo.remove_item(user_id, item_id)

        if not success:
            raise ValueError("Item no encontrado en la wishlist")

        return self.get_wishlist(user_id)

    def clear_wishlist(self, user_id):
        """
        Limpia toda la wishlist (CU-006, RF-10)
        """
        self.wishlist_repo.clear(user_id)
        return {'message': 'Wishlist limpiada exitosamente'}

    def convert_to_reservation(self, user_id, items_to_reserve):
        """
        Convierte items de la wishlist a reserva (CU-007, RF-13)

        Args:
            user_id: ID del usuario
            items_to_reserve: Lista de items con formato:
                [{'item_id': 'xxx', 'quantity': 2}, ...]

        Returns:
            Reserva creada
        """
        # Obtener wishlist con detalles
        wishlist = self.get_wishlist(user_id)
        wishlist_items = wishlist['items']

        # Validar que los items existen en la wishlist
        reservation_items = []
        for item_to_reserve in items_to_reserve:
            item_id = item_to_reserve['item_id']
            quantity = item_to_reserve['quantity']

            # Buscar item en wishlist
            wishlist_item = next(
                (item for item in wishlist_items if str(item['item_id']) == str(item_id)),
                None
            )

            if not wishlist_item:
                raise ValueError(f"Item {item_id} no encontrado en wishlist")

            # Validar cantidad
            if quantity <= 0:
                raise ValueError(f"Cantidad inválida para item {item_id}")

            if quantity > wishlist_item['quantity']:
                raise ValueError(
                    f"Cantidad solicitada ({quantity}) excede cantidad en wishlist ({wishlist_item['quantity']})"
                )

            # Validar disponibilidad (RF-12)
            available = wishlist_item.get('disponibilidad', 0)
            if quantity > available:
                raise ValueError(
                    f"Stock insuficiente para {wishlist_item['product_name']} "
                    f"({wishlist_item['variant_size']}). Disponible: {available}"
                )

            # Agregar a items de reserva
            reservation_items.append({
                'variant_id': wishlist_item['variant_id'],
                'product_name': wishlist_item['product_name'],
                'variant_size': wishlist_item['variant_size'],
                'quantity': quantity,
                'price': wishlist_item.get('variant_price')
            })

        # Crear reserva usando ReservationService
        reservation_service = ReservationService()
        reservation = reservation_service.create_reservation(
            user_id=user_id,
            items=reservation_items
        )

        # Opcional: Eliminar items de la wishlist después de crear la reserva
        for item_to_reserve in items_to_reserve:
            try:
                self.wishlist_repo.remove_item(user_id, item_to_reserve['item_id'])
            except Exception as e:
                logger.warning(f"No se pudo eliminar item {item_to_reserve['item_id']} de wishlist: {str(e)}")

        return reservation

    def get_wishlist_summary(self, user_id):
        """
        Obtiene un resumen de la wishlist con totales
        """
        wishlist = self.get_wishlist(user_id)
        items = wishlist['items']

        total_quantity = sum(item['quantity'] for item in items)
        total_value = sum(
            item['quantity'] * (item.get('variant_price') or 0)
            for item in items
        )

        items_with_stock = sum(1 for item in items if item.get('disponibilidad', 0) > 0)
        items_out_of_stock = len(items) - items_with_stock

        return {
            'user_id': user_id,
            'total_items': len(items),
            'total_quantity': total_quantity,
            'total_value': total_value,
            'items_with_stock': items_with_stock,
            'items_out_of_stock': items_out_of_stock
        }
