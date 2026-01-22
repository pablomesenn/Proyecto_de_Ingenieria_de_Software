# BACKEND# Pisos Kermy Jacó - Backend API

Sistema de Gestión y Solicitud de Reservas para Pisos Kermy Jacó S.A.

## 📋 Descripción

Backend del sistema de gestión de productos, inventario y reservas desarrollado con Flask 3.1.x, MongoDB y Redis. Implementa una arquitectura monolítica modular con separación clara de responsabilidades.

## 🏗️ Arquitectura

### Stack Tecnológico

- **Framework**: Flask 3.1.x
- **Base de Datos**: MongoDB 6.x
- **Caché**: Redis 7.x
- **Autenticación**: JWT (Flask-JWT-Extended)
- **Rate Limiting**: Flask-Limiter
- **Email**: SMTP (Gmail)
- **Containerización**: Docker & Docker Compose

### Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py              # Factory de la aplicación
│   ├── config/                  # Configuraciones
│   ├── models/                  # Modelos de MongoDB
│   ├── schemas/                 # Esquemas de validación
│   ├── routes/                  # Endpoints de la API
│   ├── services/                # Lógica de negocio
│   ├── repositories/            # Acceso a datos
│   ├── middleware/              # Middleware (auth, RBAC, etc.)
│   ├── utils/                   # Utilidades
│   ├── jobs/                    # Jobs programados
│   └── constants/               # Constantes del sistema
├── tests/                       # Tests
├── logs/                        # Logs de la aplicación
├── .env.example                 # Ejemplo de variables de entorno
├── requirements.txt             # Dependencias
├── Dockerfile                   # Imagen Docker
├── docker-compose.yml           # Orquestación de servicios
└── run.py                       # Punto de entrada
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose (recomendado)
- MongoDB 6.x (si no usas Docker)
- Redis 7.x (si no usas Docker)

### Opción 1: Con Docker (Recomendado)

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repo>
   cd backend
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

3. **Levantar los servicios**
   ```bash
   docker-compose up -d
   ```

4. **Verificar que todo esté funcionando**
   ```bash
   curl http://localhost:5000/health
   ```

### Opción 2: Instalación Local

1. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

4. **Asegurar que MongoDB y Redis estén corriendo**
   ```bash
   # MongoDB en localhost:27017
   # Redis en localhost:6379
   ```

5. **Ejecutar la aplicación**
   ```bash
   python run.py
   ```

## 🔧 Configuración

### Variables de Entorno Principales

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta
DEBUG=True

# MongoDB
MONGODB_URI=mongodb://localhost:27017/pisos_kermy_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=tu-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600

# Email (Gmail)
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Ver `.env.example` para todas las opciones disponibles.

## 📡 API Endpoints

### Autenticación (`/api/auth`)

| Método | Endpoint | Descripción | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/login` | Iniciar sesión | 5/15 min |
| POST | `/refresh` | Refrescar token | - |
| POST | `/logout` | Cerrar sesión | - |
| POST | `/forgot-password` | Solicitar reset | 3/hora |
| POST | `/reset-password` | Resetear contraseña | 5/hora |
| GET | `/verify-token` | Verificar token | - |

### Usuarios (`/api/users`)

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| GET | `/` | Listar usuarios | ADMIN |
| GET | `/:id` | Obtener usuario | ADMIN/propio |
| POST | `/` | Crear usuario | ADMIN |
| PUT | `/:id` | Actualizar usuario | ADMIN/propio |
| DELETE | `/:id` | Eliminar usuario | ADMIN |
| GET | `/profile` | Ver perfil propio | CLIENT |
| PUT | `/profile` | Editar perfil | CLIENT |

### Productos (`/api/products`)

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| GET | `/` | Listar productos | Todos |
| GET | `/:id` | Obtener producto | Todos |
| POST | `/` | Crear producto | ADMIN |
| PUT | `/:id` | Actualizar producto | ADMIN |
| DELETE | `/:id` | Eliminar producto | ADMIN |
| GET | `/search` | Buscar productos | Todos |

### Inventario (`/api/inventory`)

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| GET | `/` | Listar inventario | ADMIN |
| POST | `/adjust` | Ajustar inventario | ADMIN |
| GET | `/history` | Historial de cambios | ADMIN |

### Wishlist (`/api/wishlist`)

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| GET | `/` | Ver wishlist | CLIENT |
| POST | `/items` | Agregar ítem | CLIENT |
| PUT | `/items/:id` | Actualizar ítem | CLIENT |
| DELETE | `/items/:id` | Eliminar ítem | CLIENT |
| POST | `/convert-to-reservation` | Convertir a reserva | CLIENT |

### Reservas (`/api/reservations`)

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| GET | `/` | Listar reservas | CLIENT/ADMIN |
| GET | `/:id` | Obtener reserva | CLIENT/ADMIN |
| POST | `/` | Crear reserva | CLIENT |
| PUT | `/:id/cancel` | Cancelar reserva | CLIENT/ADMIN |
| PUT | `/:id/approve` | Aprobar reserva | ADMIN |
| PUT | `/:id/reject` | Rechazar reserva | ADMIN |

### Admin (`/api/admin`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/categories` | Listar categorías |
| POST | `/categories` | Crear categoría |
| PUT | `/categories/:id` | Actualizar categoría |
| DELETE | `/categories/:id` | Eliminar categoría |
| GET | `/export/products` | Exportar productos |
| GET | `/export/reservations` | Exportar reservas |
| GET | `/audit-log` | Ver auditoría |

## 🔐 Autenticación y Autorización

### JWT Tokens

El sistema usa JWT con dos tipos de tokens:

1. **Access Token**: Válido por 1 hora, usado para operaciones normales
2. **Refresh Token**: Válido por 30 días, usado para obtener nuevos access tokens

### Roles y Permisos (RBAC)

- **ADMIN**: Acceso completo al sistema
- **CLIENT**: Acceso a catálogo, wishlist y reservas propias

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_auth.py
```

## 📊 Monitoreo

### Health Check

```bash
GET /health
```

Respuesta:
```json
{
  "status": "healthy",
  "service": "Pisos Kermy API",
  "version": "1.0.0"
}
```

### Logs

Los logs se almacenan en `logs/app.log` con rotación automática.

## 🔄 Jobs Programados

### Expiración de Reservas
- **Frecuencia**: Cada 5 minutos
- **Función**: Expira reservas vencidas y libera inventario

### Notificaciones
- **Frecuencia**: Diaria a las 9:00 AM
- **Función**: Envía avisos de reservas por vencer

## 🐳 Docker

### Servicios Disponibles

- **backend**: API Flask (puerto 5000)
- **mongodb**: Base de datos (puerto 27017)
- **redis**: Caché (puerto 6379)
- **mongo-express**: UI de MongoDB (puerto 8081) - solo en desarrollo

### Comandos Útiles

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build

# Ejecutar con Mongo Express (desarrollo)
docker-compose --profile dev up -d
```

## 📝 Desarrollo

### Agregar un Nuevo Módulo

1. Crear modelo en `app/models/`
2. Crear esquema de validación en `app/schemas/`
3. Crear repositorio en `app/repositories/`
4. Crear servicio en `app/services/`
5. Crear rutas en `app/routes/`
6. Registrar blueprint en `app/__init__.py`

### Convenciones de Código

- **Formato**: Black
- **Linting**: Flake8
- **Naming**: snake_case para funciones y variables
- **Docstrings**: Google style

## 🐛 Troubleshooting

### MongoDB no conecta
```bash
# Verificar que MongoDB está corriendo
docker-compose ps

# Ver logs de MongoDB
docker-compose logs mongodb
```

### Redis no disponible
```bash
# Verificar Redis
docker-compose ps redis

# La aplicación funciona sin Redis (sin caché)
```

### Rate Limit activado
- Esperar el tiempo indicado
- O desactivar en `.env`: `RATE_LIMIT_ENABLED=False`

## 📚 Documentación Adicional

- [Software Architecture Document (SAD)](../docs/SAD.pdf)
- [Especificación de Requerimientos (ERS)](../docs/ERS.pdf)

## 👥 Equipo

- Alonso Durán Muñoz
- Pablo Mesén Alvarado
- Luis Urbina Salazar
- Andrés Mora Urbina

## 📄 Licencia

Proyecto académico - TEC 2026
