from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.config.database import get_db
from app.constants.roles import UserRole
from app.constants.states import ReservationState
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)
reservation_repo = ReservationRepository()
product_repo = ProductRepository()
inventory_repo = InventoryRepository()


def require_admin(f):
    """Decorador para verificar que el usuario sea admin"""
    def wrapper(*args, **kwargs):
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')
        
        if user_role != UserRole.ADMIN:
            return jsonify({'error': 'Permisos insuficientes'}), 403
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_admin
def get_dashboard_stats():
    """
    Obtiene estadisticas generales para el dashboard de administracion
    """
    try:
        db = get_db()
        
        # Estadisticas de reservas
        total_reservations = db.reservations.count_documents({})
        pending_reservations = db.reservations.count_documents({'state': ReservationState.PENDING})
        today_reservations = db.reservations.count_documents({
            'created_at': {
                '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
        })
        
        # Estadisticas de productos - CORREGIDO: usar 'estado' en vez de 'state'
        total_products = db.products.count_documents({'estado': 'activo'})
        
        # Productos con stock bajo (menos de 10 unidades disponibles)
        low_stock_count = 0
        products = list(db.products.find({'estado': 'activo'}))
        
        for product in products:
            # Buscar variantes en la coleccion variants (no dentro del producto)
            variants = list(db.variants.find({'product_id': product['_id']}))
            
            for variant in variants:
                # CORREGIDO: usar 'stock_total' y calcular disponible
                inventory = db.inventory.find_one({'variant_id': variant['_id']})
                if inventory:
                    stock_total = inventory.get('stock_total', 0)
                    stock_retenido = inventory.get('stock_retenido', 0)
                    stock_disponible = stock_total - stock_retenido
                    
                    if stock_disponible < 10:
                        low_stock_count += 1
                        break
        
        # Estadisticas de usuarios
        total_users = db.users.count_documents({})
        this_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = db.users.count_documents({
            'created_at': {'$gte': this_month_start}
        })
        
        # Alertas activas (reservas por expirar en las proximas 24 horas)
        tomorrow = datetime.now() + timedelta(days=1)
        expiring_soon = db.reservations.count_documents({
            'state': ReservationState.PENDING,
            'expires_at': {
                '$gte': datetime.now(),
                '$lte': tomorrow
            }
        })
        
        return jsonify({
            'stats': {
                'pending_reservations': {
                    'value': pending_reservations,
                    'change': f'+{today_reservations} hoy'
                },
                'active_products': {
                    'value': total_products,
                    'low_stock': low_stock_count
                },
                'total_users': {
                    'value': total_users,
                    'new_this_month': new_users_this_month
                },
                'alerts': {
                    'value': expiring_soon + low_stock_count
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadisticas del dashboard: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@dashboard_bp.route('/pending-reservations', methods=['GET'])
@jwt_required()
@require_admin
def get_pending_reservations():
    """
    Obtiene las reservas pendientes recientes para el dashboard
    """
    try:
        reservations = list(reservation_repo.collection.find({
            'state': ReservationState.PENDING
        }).sort('created_at', -1).limit(5))
        
        # Obtener informacion del usuario para cada reserva
        db = get_db()
        result = []
        
        for res in reservations:
            user = db.users.find_one({'_id': res['user_id']})
            
            # Calcular tiempo hasta expiracion
            expires_at = res.get('expires_at')
            expires_in = None
            if expires_at:
                time_left = expires_at - datetime.now()
                hours = int(time_left.total_seconds() // 3600)
                if hours < 1:
                    mins = int(time_left.total_seconds() // 60)
                    expires_in = f'{mins} minutos' if mins > 0 else 'Expirando'
                elif hours < 24:
                    expires_in = f'{hours} horas'
                else:
                    days = hours // 24
                    expires_in = f'{days} dias'
            
            # Calcular total de unidades
            total_units = sum(item['quantity'] for item in res.get('items', []))
            
            result.append({
                '_id': str(res['_id']),
                'customer_name': user.get('nombre', user.get('email', 'Usuario')) if user else 'Usuario',
                'items_count': len(res.get('items', [])),
                'total_units': total_units,
                'created_at': res['created_at'].isoformat(),
                'expires_in': expires_in
            })
        
        return jsonify({'reservations': result}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo reservas pendientes: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@dashboard_bp.route('/expiring-reservations', methods=['GET'])
@jwt_required()
@require_admin
def get_expiring_reservations():
    """
    Obtiene reservas que estan por expirar (proximas 12 horas)
    """
    try:
        twelve_hours = datetime.now() + timedelta(hours=12)
        
        reservations = list(reservation_repo.collection.find({
            'state': ReservationState.PENDING,
            'expires_at': {
                '$gte': datetime.now(),
                '$lte': twelve_hours
            }
        }).sort('expires_at', 1).limit(5))
        
        db = get_db()
        result = []
        
        for res in reservations:
            user = db.users.find_one({'_id': res['user_id']})
            
            expires_at = res.get('expires_at')
            time_left = expires_at - datetime.now()
            hours = int(time_left.total_seconds() // 3600)
            
            if hours < 1:
                mins = int(time_left.total_seconds() // 60)
                expires_in = f'{mins} min'
            else:
                expires_in = f'{hours} horas'
            
            result.append({
                '_id': str(res['_id']),
                'customer_name': user.get('nombre', user.get('email', 'Usuario')) if user else 'Usuario',
                'expires_in': expires_in
            })
        
        return jsonify({'reservations': result}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo reservas por expirar: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@dashboard_bp.route('/low-stock-products', methods=['GET'])
@jwt_required()
@require_admin
def get_low_stock_products():
    """
    Obtiene productos con stock bajo (menos de 10 unidades disponibles)
    """
    try:
        db = get_db()
        products = list(db.products.find({'estado': 'activo'}))
        
        low_stock_items = []
        
        for product in products:
            # Buscar variantes en la coleccion variants
            variants = list(db.variants.find({'product_id': product['_id']}))
            
            for variant in variants:
                # CORREGIDO: usar 'stock_total' y calcular disponible
                inventory = db.inventory.find_one({'variant_id': variant['_id']})
                
                if inventory:
                    stock_total = inventory.get('stock_total', 0)
                    stock_retenido = inventory.get('stock_retenido', 0)
                    stock_disponible = stock_total - stock_retenido
                else:
                    stock_disponible = 0
                
                if stock_disponible < 10:
                    low_stock_items.append({
                        '_id': str(product['_id']),
                        'name': product.get('nombre', 'Producto'),
                        'variant_name': variant.get('tamano_pieza', 'Variante'),
                        'stock': stock_disponible
                    })
                    
                    # Limitar a 5 productos
                    if len(low_stock_items) >= 5:
                        break
            
            if len(low_stock_items) >= 5:
                break
        
        return jsonify({'products': low_stock_items}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo productos con stock bajo: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500