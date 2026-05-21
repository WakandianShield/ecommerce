# Backend E-commerce (Hexagonal)

Backend simple en FastAPI con Postgres y arquitectura hexagonal.

## Estructura de carpetas

Este backend esta organizado con arquitectura hexagonal. La idea principal es separar el negocio de los detalles externos, como la API, la base de datos o la seguridad. Asi el centro de la aplicacion puede crecer sin depender directamente de FastAPI, Postgres o JWT.

backend/
- Carpeta raiz del backend. Aqui viven la configuracion del proyecto, la lista de dependencias, el script para correr la app y esta documentacion.

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
