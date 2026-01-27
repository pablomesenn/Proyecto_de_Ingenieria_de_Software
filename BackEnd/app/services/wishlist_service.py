from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_repository import VariantRepository
from app.repositories.inventory_repository import InventoryRepository
from app.services.reservation_service import ReservationService
import logging
import time
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

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

    def _retry_operation(self, operation, max_retries=3, delay=1):
        """
        Retry a database operation with exponential backoff

        Args:
            operation: Callable to retry
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries (seconds)

        Returns:
            Result of the operation

        Raises:
            Exception from the last failed attempt
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return operation()
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Database operation failed after {max_retries} attempts: {str(e)}")
            except Exception as e:
                # For non-connection errors, don't retry
                logger.error(f"Non-retryable error in database operation: {str(e)}")
                raise

        # If we exhausted all retries, raise the last exception
        raise last_exception

    def convert_to_reservation(self, user_id, items_to_reserve):
        """
        Convierte items de la wishlist a reserva (CU-007, RF-13)
        WITH IMPROVED ERROR HANDLING AND RETRY LOGIC

        Args:
            user_id: ID del usuario
            items_to_reserve: Lista de items con formato:
                [{'item_id': 'xxx', 'quantity': 2}, ...]

        Returns:
            Reserva creada
        """
        try:
            logger.info(f"Starting wishlist to reservation conversion for user {user_id}")
            logger.debug(f"Items to reserve: {items_to_reserve}")

            # Obtener wishlist con detalles (with retry)
            def get_wishlist_operation():
                return self.get_wishlist(user_id)

            wishlist = self._retry_operation(get_wishlist_operation)
            wishlist_items = wishlist['items']

            logger.info(f"Retrieved wishlist with {len(wishlist_items)} items")

            # Validar que los items existen en la wishlist
            reservation_items = []
            for item_to_reserve in items_to_reserve:
                item_id = item_to_reserve['item_id']
                quantity = item_to_reserve['quantity']

                logger.debug(f"Processing item_id: {item_id}, quantity: {quantity}")

                # Buscar item en wishlist
                wishlist_item = next(
                    (item for item in wishlist_items if str(item['item_id']) == str(item_id)),
                    None
                )

                if not wishlist_item:
                    logger.error(f"Item {item_id} not found in wishlist")
                    raise ValueError(f"Item {item_id} no encontrado en wishlist")

                logger.debug(f"Found wishlist item: {wishlist_item.get('product', {}).get('nombre', 'Unknown')}")

                # Validar cantidad
                if quantity <= 0:
                    raise ValueError(f"Cantidad inválida para item {item_id}")

                if quantity > wishlist_item['quantity']:
                    raise ValueError(
                        f"Cantidad solicitada ({quantity}) excede cantidad en wishlist ({wishlist_item['quantity']})"
                    )

                # Validar disponibilidad (RF-12)
                # Check both 'disponibilidad' and 'stock_disponible' from inventory object
                inventory = wishlist_item.get('inventory', {})
                available = inventory.get('disponibilidad', inventory.get('stock_disponible', 0))

                # Also check root-level 'stock' field as fallback
                if available == 0:
                    available = wishlist_item.get('stock', 0)

                logger.debug(f"Available stock for item: {available}")

                if quantity > available:
                    # Extract product name from nested structure
                    product_name = wishlist_item.get('product', {}).get('nombre') or wishlist_item.get('product', {}).get('name', 'Producto')
                    variant_size = wishlist_item.get('variant', {}).get('tamano_pieza') or wishlist_item.get('variant', {}).get('size', '')

                    error_msg = f"Stock insuficiente para {product_name} ({variant_size}). Disponible: {available}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                # Agregar a items de reserva
                # Extract data from nested structure (handles both Spanish and English field names)
                product_name = wishlist_item.get('product', {}).get('nombre') or wishlist_item.get('product', {}).get('name', 'Producto')
                variant_size = wishlist_item.get('variant', {}).get('tamano_pieza') or wishlist_item.get('variant', {}).get('size', '')
                variant_price = wishlist_item.get('variant', {}).get('precio') or wishlist_item.get('variant', {}).get('price')

                reservation_item = {
                    'variant_id': wishlist_item['variant_id'],
                    'product_name': product_name,
                    'variant_size': variant_size,
                    'quantity': quantity,
                    'price': variant_price
                }

                reservation_items.append(reservation_item)
                logger.debug(f"Added reservation item: {product_name} - {variant_size} x{quantity}")

            logger.info(f"Validated {len(reservation_items)} items for reservation")

            # Crear reserva usando ReservationService (with retry)
            def create_reservation_operation():
                reservation_service = ReservationService()
                return reservation_service.create_reservation(
                    user_id=user_id,
                    items=reservation_items
                )

            reservation = self._retry_operation(create_reservation_operation)
            logger.info(f"Reservation created successfully: {reservation._id}")

            # Eliminar items de la wishlist después de crear la reserva
            # (Best effort - don't fail the whole operation if this fails)
            for item_to_reserve in items_to_reserve:
                try:
                    self.wishlist_repo.remove_item(user_id, item_to_reserve['item_id'])
                    logger.debug(f"Removed item {item_to_reserve['item_id']} from wishlist")
                except Exception as e:
                    logger.warning(
                        f"No se pudo eliminar item {item_to_reserve['item_id']} de wishlist: {str(e)}. "
                        "This is non-critical - continuing."
                    )

            logger.info(f"Wishlist to reservation conversion completed successfully")
            return reservation

        except ValueError as e:
            # Business logic errors - don't retry, just re-raise
            logger.error(f"Validation error in convert_to_reservation: {str(e)}")
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            # Database connection errors - already retried in _retry_operation
            error_msg = (
                "No se pudo conectar a la base de datos. "
                "Por favor, verifica tu conexión a internet e intenta nuevamente."
            )
            logger.error(f"Database connection error after retries: {str(e)}")
            raise ValueError(error_msg)
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error in convert_to_reservation: {str(e)}", exc_info=True)
            raise ValueError(f"Error inesperado al crear la reserva: {str(e)}")

    def get_wishlist_summary(self, user_id):
        """
        Obtiene un resumen de la wishlist con totales
        """
        wishlist = self.get_wishlist(user_id)
        items = wishlist['items']

        total_quantity = sum(item['quantity'] for item in items)

        # Calculate total value - handle nested variant structure
        total_value = 0
        for item in items:
            variant_price = item.get('variant', {}).get('precio') or item.get('variant', {}).get('price', 0)
            total_value += item['quantity'] * variant_price

        # Check availability from inventory or root-level fields
        items_with_stock = 0
        for item in items:
            inventory = item.get('inventory', {})
            available = inventory.get('disponibilidad', inventory.get('stock_disponible', 0))
            if available == 0:
                available = item.get('stock', 0)
            if available > 0:
                items_with_stock += 1

        items_out_of_stock = len(items) - items_with_stock

        return {
            'user_id': user_id,
            'total_items': len(items),
            'total_quantity': total_quantity,
            'total_value': total_value,
            'items_with_stock': items_with_stock,
            'items_out_of_stock': items_out_of_stock
        }
