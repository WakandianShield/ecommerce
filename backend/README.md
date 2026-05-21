# E-Commerce Backend – Arquitectura Hexagonal

Backend de un sistema de e-commerce construido con **Python + FastAPI + GraphQL (Strawberry)** siguiendo **Arquitectura Hexagonal**.

## Estructura del Proyecto

```
app/
├── domain/              # Núcleo del negocio (sin dependencias externas)
│   ├── entities/        # Entidades: Product, Profile, Order
│   ├── ports/           # Interfaces/contratos: repositorios abstractos
│   └── exceptions.py    # Excepciones de dominio
│
├── application/         # Casos de uso (orquestación de la lógica)
│   └── use_cases/
│       ├── products/    # get_all, get_by_id, get_by_category
│       ├── profiles/    # register, login, get_profile
│       └── orders/      # create_order, get_order, get_orders_by_profile
│
├── infrastructure/      # Implementaciones concretas (DB, Auth)
│   ├── database/
│   │   ├── connection.py          # SQLAlchemy + auto-creación de tablas
│   │   ├── models/                # Modelos ORM (ProductModel, ProfileModel, OrderModel)
│   │   └── repositories/         # Implementaciones PostgreSQL de los puertos
│   └── auth/
│       └── jwt_handler.py         # JWT + bcrypt
│
├── adapters/            # Puntos de entrada/salida
│   └── graphql/
│       ├── schema.py    # Queries y Mutations (100% GraphQL)
│       └── types/       # Tipos GraphQL: ProductType, UserProfileType, OrderType
│
└── main.py              # Punto de entrada FastAPI + CORS + contexto GraphQL
```

## Entidades

| Entidad | Descripción |
|---------|-------------|
| **Product** | Álbum de vinilo con nombre, artista, año, precio y categoría |
| **Profile** | Perfil de compra (usuario) con autenticación JWT |
| **Order** | Orden de compra con items, dirección y estado |

## Requisitos

- Python 3.10+
- PostgreSQL corriendo localmente

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Configuración

Edita el archivo `.env`:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/ecommerce
JWT_SECRET=tu-clave-secreta
```

Las tablas se crean **automáticamente** al iniciar el servidor si no existen.

## Ejecutar

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## GraphQL Playground

Abre `http://localhost:8000/graphql` en el navegador.

## Operaciones GraphQL

### Mutations

```graphql
# Registro
mutation {
  register(fullName: "Juan Perez", email: "juan@mail.com", password: "123456") {
    token
    user { id fullName email }
  }
}

# Login
mutation {
  login(email: "juan@mail.com", password: "123456") {
    token
    user { id fullName email }
  }
}

# Crear orden (requiere token en header Authorization: Bearer <token>)
mutation {
  createOrderFromItems(
    items: [{ name: "Illmatic", price: 549.0, qty: 1, img: "..." }]
    shippingAddress: "Av. Reforma 123, CDMX"
    totalCents: 54900
  ) {
    id
    status
    totalCents
  }
}
```

### Queries

```graphql
# Todos los productos
query { products { id name artist priceCents category } }

# Por categoría
query { products(category: "hip-hop") { name artist } }

# Perfil autenticado
query { me { id fullName email } }

# Mis órdenes
query { orders { id status totalCents createdAt } }
```
