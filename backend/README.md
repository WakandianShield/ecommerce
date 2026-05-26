# Backend E-commerce (Hexagonal)

Backend simple en FastAPI con Postgres y arquitectura hexagonal.

## Estructura de carpetas

backend/app/
- Contiene el codigo principal de la aplicacion. Desde aqui se arma FastAPI, se conectan las rutas, se inicializa la base de datos y se unen las capas internas del sistema.

backend/app/domain/
- Es el centro del negocio. Aqui se define que es un producto, un perfil y una orden desde el punto de vista de la tienda, junto con errores propios del dominio. Esta capa no deberia depender de FastAPI ni de Postgres.

backend/app/domain/entities/
- Guarda las entidades principales del e-commerce. Una entidad representa un concepto importante del negocio, por ejemplo productos, clientes y ordenes.

backend/app/domain/ports/
- Define contratos que el dominio necesita para comunicarse con el exterior. Por ejemplo, aqui se dice que operaciones debe tener un repositorio de productos, perfiles u ordenes, sin importar todavia si se guardan en Postgres, memoria u otro sistema.

backend/app/application/
- Coordina los casos de uso de la aplicacion. Esta capa toma las entidades del dominio y las usa para resolver acciones concretas como registrar usuarios, iniciar sesion, administrar productos o crear ordenes.

backend/app/application/use_cases/
- Contiene los servicios de aplicacion. Cada servicio agrupa reglas y pasos para una parte del sistema: productos, perfiles, sesiones y ordenes.

backend/app/infrastructure/
- Contiene detalles tecnicos externos al negocio. Aqui esta lo necesario para conectarse a la base de datos, leer configuracion, manejar contrasenas y generar tokens.

backend/app/infrastructure/config/
- Se encarga de cargar la configuracion del backend, como variables de entorno y valores necesarios para conectar servicios.

backend/app/infrastructure/database/
- Contiene la implementacion real de persistencia. Aqui se define la conexion con Postgres, las tablas/modelos de base de datos y los repositorios que guardan y consultan informacion.

backend/app/infrastructure/security/
- Agrupa la logica tecnica de seguridad. Sirve para proteger contrasenas, validar credenciales y crear o leer tokens de acceso.

backend/app/adapters/
- Contiene las entradas y salidas de la aplicacion. En este proyecto el adaptador principal es la API HTTP, pero esta capa podria tener otros adaptadores en el futuro.

backend/app/adapters/api/
- Traduce entre HTTP/FastAPI y los casos de uso internos. Aqui se definen los formatos de entrada y salida, dependencias compartidas y la conexion entre rutas y servicios.

backend/app/adapters/api/routers/
- Agrupa las rutas REST por tema. Hay rutas para productos, perfiles, sesiones y ordenes, cada una llamando a los casos de uso correspondientes.

## Setup
1. Asegura que Postgres este corriendo y exista la base de datos.
2. Configura el archivo .env en backend/ con DATABASE_URL.
3. Instala dependencias.
4. Inicia el servidor.

Ejemplo de .env:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecom
JWT_SECRET=dev-secret-change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

Comando:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

## Endpoints REST
- POST /profiles (registro, retorna tokens)
- POST /sessions (login, retorna tokens)
- POST /sessions/refresh (refresh token)
- POST /sessions/logout (revoca refresh token)
- GET /profiles/me
- GET /products
- POST /products (admin)
- POST /products/{id}/image (admin, multipart/form-data)
- GET /products/{id}
- PUT /products/{id} (admin)
- DELETE /products/{id} (admin)
- POST /orders (auth requerida)
- GET /orders (auth requerida)
- GET /orders/{id} (auth requerida)
- GET /orders/admin (admin u operador)
- PUT /orders/{id}/status (admin u operador)

## WebSocket
- WS /realtime/chat
	- Param opcional: session_id
	- Mensaje de entrada: texto plano
	- Respuesta: JSON con type=session o type=message

## Chat (admin)
- GET /realtime/sessions (admin u operador)
- GET /realtime/sessions/{session_id} (admin u operador)

## Notas
- Usa Authorization: Bearer <access_token> para endpoints protegidos.
- Los roles disponibles son: customer, admin, operator.
- CORS esta abierto para facilitar el uso con el frontend local.
- Si ya existia una base de datos, agrega la columna profiles.role y la tabla refresh_tokens (o recrea la BD en desarrollo).
- Las imagenes se guardan en backend/uploads y se sirven en /media.
