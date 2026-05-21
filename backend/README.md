# Backend E-commerce (Hexagonal)

Backend simple en FastAPI con Postgres y arquitectura hexagonal.

Desglose de carpetas y archivos (lenguaje natural):

backend/
- backend/.env: aqui pones la direccion de la base de datos y la llave de acceso del servidor.
- backend/run.cmd: prepara el entorno, instala lo necesario y levanta el servidor.
- backend/requirements.txt: lista corta de paquetes que se instalan.
- backend/README.md: esta guia.

backend/app/
- backend/app/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/main.py: punto de inicio; crea tablas, une las rutas y enciende el servidor.

backend/app/domain/
- backend/app/domain/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/domain/errors.py: mensajes de error del negocio en palabras simples.

backend/app/domain/entities/
- backend/app/domain/entities/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/domain/entities/product.py: datos de producto y formas de crearlo o editarlo.
- backend/app/domain/entities/profile.py: datos del perfil del cliente.
- backend/app/domain/entities/order.py: datos de la orden y sus productos.

backend/app/domain/ports/
- backend/app/domain/ports/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/domain/ports/product_repository.py: dice como se guardan y leen productos.
- backend/app/domain/ports/profile_repository.py: dice como se guardan y leen perfiles.
- backend/app/domain/ports/order_repository.py: dice como se guardan y leen ordenes.

backend/app/application/
- backend/app/application/__init__.py: indica que esta carpeta es parte del proyecto.

backend/app/application/use_cases/
- backend/app/application/use_cases/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/application/use_cases/product_service.py: reglas basicas de productos.
- backend/app/application/use_cases/profile_service.py: reglas de registro.
- backend/app/application/use_cases/session_service.py: reglas para iniciar sesion.
- backend/app/application/use_cases/order_service.py: reglas de ordenes.

backend/app/infrastructure/
- backend/app/infrastructure/__init__.py: indica que esta carpeta es parte del proyecto.

backend/app/infrastructure/config/
- backend/app/infrastructure/config/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/infrastructure/config/settings.py: lee el .env y entrega la configuracion.

backend/app/infrastructure/database/
- backend/app/infrastructure/database/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/infrastructure/database/connection.py: abre la base y crea tablas.
- backend/app/infrastructure/database/models.py: describe como se guardan los datos en la base.
- backend/app/infrastructure/database/repositories.py: pasos reales para guardar y leer datos.

backend/app/infrastructure/security/
- backend/app/infrastructure/security/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/infrastructure/security/password_hasher.py: guarda y revisa contrasenas de forma segura.
- backend/app/infrastructure/security/token_service.py: crea y lee la llave de acceso del usuario.

backend/app/adapters/
- backend/app/adapters/__init__.py: indica que esta carpeta es parte del proyecto.

backend/app/adapters/api/
- backend/app/adapters/api/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/adapters/api/schemas.py: define el formato de lo que entra y sale.
- backend/app/adapters/api/dependencies.py: prepara la base y el usuario actual.

backend/app/adapters/api/routers/
- backend/app/adapters/api/routers/__init__.py: indica que esta carpeta es parte del proyecto.
- backend/app/adapters/api/routers/products.py: rutas de productos.
- backend/app/adapters/api/routers/profiles.py: rutas de registro y perfil.
- backend/app/adapters/api/routers/sessions.py: rutas de inicio de sesion.
- backend/app/adapters/api/routers/orders.py: rutas de ordenes.

## Setup
1. Asegura que Postgres este corriendo y exista la base de datos.
2. Configura el archivo .env en backend/ con DATABASE_URL.
3. Instala dependencias.
4. Inicia el servidor.

Ejemplo de .env:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecom

Comando:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

## Endpoints REST
- POST /profiles (registro, retorna token)
- POST /sessions (login, retorna token)
- GET /profiles/me
- GET /products
- POST /products
- GET /products/{id}
- PUT /products/{id}
- DELETE /products/{id}
- POST /orders (auth requerida)
- GET /orders (auth requerida)
- GET /orders/{id} (auth requerida)
- PUT /orders/{id}/status (auth requerida)

## Notas
- Usa Authorization: Bearer <token> para endpoints protegidos.
- CORS esta abierto para facilitar el uso con el frontend local.
