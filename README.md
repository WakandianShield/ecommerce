# E-commerce de Vinilos

Tienda en línea de discos de vinilo con carrito de compras, chat en tiempo real y panel de administración.

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + PostgreSQL (arquitectura hexagonal) |
| Frontend | HTML + CSS + JavaScript vanilla |
| Autenticación | JWT (access + refresh tokens) |
| Chat | WebSocket + FAQ automático en memoria |

---

## Repositorios de documentación

- [Backend](backend/README.md) — API REST, módulo de auth, módulo de chat, base de datos
- [Frontend](frontend/README.md) — Páginas, auth.js, carrito, diagramas de componentes

---

## Inicio rápido

### Backend

```bash
cd backend
# Crear .env con DATABASE_URL y JWT_SECRET
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Crear cuenta de administrador

```bash
cd backend
python scripts/create_admin.py --email admin@tienda.com --password MiPassword123 --name "Admin"
```

Con la sesión iniciada como admin, el navbar del frontend muestra un icono de escudo que lleva directamente al panel de administración para gestionar productos y órdenes.

### Frontend

Abre `frontend/home/index.html` directamente en el navegador o con cualquier servidor estático.

---

## Diagrama de casos de uso — Sistema completo

```mermaid
graph LR
    Cliente([Cliente])
    Admin([Administrador])
    Op([Operador])
    Sistema([Sistema - FAQ Bot])

    subgraph Compras
        UC1[Ver catálogo]
        UC2[Filtrar por categoría]
        UC3[Usar carrito]
        UC4[Realizar checkout]
        UC5[Ver historial de órdenes]
    end

    subgraph Autenticación
        UC6[Registrarse]
        UC7[Iniciar sesión]
        UC8[Renovar sesión]
    end

    subgraph Chat
        UC9[Enviar mensaje]
        UC10[Recibir respuesta automática]
        UC11[Revisar sesiones de chat]
    end

    subgraph Administración
        UC12[Crear / editar productos]
        UC13[Subir imagen de producto]
        UC14[Gestionar órdenes]
        UC15[Ver todas las órdenes]
    end

    Cliente --> UC1
    Cliente --> UC2
    Cliente --> UC3
    Cliente --> UC4
    Cliente --> UC5
    Cliente --> UC6
    Cliente --> UC7
    Cliente --> UC8
    Cliente --> UC9
    UC9 --> UC10
    Sistema --> UC10

    Admin --> UC12
    Admin --> UC13
    Admin --> UC15
    Admin --> UC14
    Admin --> UC11

    Op --> UC15
    Op --> UC14
    Op --> UC11
```

---

## Diagrama de secuencia — Flujo completo de compra

```mermaid
sequenceDiagram
    participant U as Usuario
    participant FE as Frontend (JS)
    participant Auth as auth.js
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL

    Note over U,DB: 1 — Autenticación
    U->>FE: Ingresa email y contraseña
    FE->>BE: POST /sessions
    BE->>DB: Validar credenciales
    DB-->>BE: ProfileAuth
    BE-->>FE: {access_token, refresh_token, profile}
    FE->>FE: Guarda tokens en localStorage

    Note over U,DB: 2 — Navegación y carrito
    U->>FE: Navega al catálogo
    FE->>BE: GET /products
    BE->>DB: SELECT products
    DB-->>BE: Productos
    BE-->>FE: Lista de productos
    U->>FE: Agrega al carrito
    FE->>FE: Guarda carrito en localStorage

    Note over U,DB: 3 — Checkout y orden
    U->>FE: Abre checkout y confirma
    FE->>Auth: sgGetToken()
    Auth-->>FE: access_token (refresca si expiró)
    FE->>BE: POST /orders {shipping_address, items}
    BE->>DB: Verifica stock por producto
    DB-->>BE: Stock disponible
    BE->>DB: INSERT orders + order_items
    BE->>DB: UPDATE products.stock (decrementa)
    DB-->>BE: Order creada
    BE-->>FE: {id, status: "created", total_cents}
    FE-->>U: Redirige a página de éxito
```

---

## Diagrama de secuencia — Login y validación JWT

```mermaid
sequenceDiagram
    participant U as Usuario
    participant FE as Frontend
    participant BE as Backend
    participant TS as TokenService
    participant DB as PostgreSQL

    U->>FE: POST /sessions {email, password}
    FE->>BE: Envía credenciales
    BE->>DB: SELECT profile WHERE email=?
    DB-->>BE: ProfileAuth
    BE->>BE: verify_password(password, hash)
    BE->>TS: create_access_token(id, role)
    TS-->>BE: JWT access (exp: 60 min)
    BE->>TS: create_refresh_token(id, role)
    TS-->>BE: JWT refresh + token_id
    BE->>DB: INSERT refresh_tokens
    BE-->>FE: {access_token, refresh_token}

    Note over U,DB: Más tarde — acceso a ruta protegida
    FE->>BE: GET /orders (Authorization: Bearer <token>)
    BE->>TS: decode_token(token)
    TS-->>BE: {sub, role, type: "access", exp}
    BE->>DB: SELECT profile WHERE id=sub
    DB-->>BE: Profile
    BE-->>FE: Lista de órdenes del usuario
```

---

## Diagrama de secuencia — Subida de imagen de producto

```mermaid
sequenceDiagram
    participant A as Admin
    participant FE as admin.js
    participant BE as Backend
    participant FS as Sistema de archivos

    A->>FE: Selecciona archivo de imagen
    FE->>BE: POST /products/{id}/image (multipart/form-data)
    BE->>BE: Valida tipo MIME y tamaño
    BE->>FS: Guarda en backend/uploads/{filename}
    FS-->>BE: Ruta guardada
    BE-->>FE: {image_url: "/media/{filename}"}
    FE->>BE: PUT /products/{id} {image_url}
    BE->>BE: update_product(id, {image_url})
    BE-->>FE: Producto actualizado
    FE-->>A: Muestra nueva imagen
```

---

## Diagrama de secuencia — Comunicación WebSocket (Chat)

```mermaid
sequenceDiagram
    participant C as Cliente (browser)
    participant FE as chat.js
    participant WS as Backend WebSocket
    participant CS as ChatService
    participant FM as FAQ Matcher

    C->>FE: Abre página de chat
    FE->>WS: WS connect /realtime/chat
    WS->>CS: open_session()
    CS-->>WS: session_id
    WS-->>FE: {type: "session", session_id}
    FE->>FE: Guarda session_id en localStorage

    loop Conversación
        C->>FE: Escribe y envía mensaje
        FE->>WS: texto plano
        WS->>CS: handle_message(session_id, texto)
        CS->>FM: match(texto)
        FM-->>CS: FaqEntry o None
        CS-->>WS: (user_msg, assistant_msg)
        WS-->>FE: {type: "message", message: user_msg}
        WS-->>FE: {type: "message", message: assistant_msg}
        FE-->>C: Muestra ambos mensajes
    end
```

---

## Diagrama de clases — Sistema completo

```mermaid
classDiagram
    class Profile {
        +UUID id
        +str full_name
        +str email
        +str role
    }
    class Product {
        +UUID id
        +str name
        +str description
        +int price_cents
        +int stock
        +str category
        +str image_url
        +bool is_active
    }
    class Order {
        +UUID id
        +UUID profile_id
        +str status
        +int total_cents
        +str shipping_address
        +List~OrderItem~ items
    }
    class OrderItem {
        +UUID id
        +UUID product_id
        +str name
        +int unit_price_cents
        +int quantity
    }
    class CartItem {
        +str id
        +str name
        +int price_cents
        +int quantity
        +str image_url
    }
    class ChatMessage {
        +UUID id
        +str session_id
        +str sender
        +str content
        +datetime created_at
    }
    class FaqEntry {
        +UUID id
        +str question
        +str answer
        +List~str~ keywords
    }
    class RefreshToken {
        +str id
        +UUID profile_id
        +datetime expires_at
        +datetime revoked_at
    }
    class TokenService {
        +create_access_token(profile_id, role) str
        +create_refresh_token(profile_id, role) tuple
        +decode_token(token) dict
    }

    Profile "1" --> "0..*" Order : realiza
    Profile "1" --> "0..*" RefreshToken : posee
    Order "1" --> "1..*" OrderItem : contiene
    OrderItem "0..*" --> "1" Product : referencia
    CartItem "0..*" --> "1" Product : representa
    ChatMessage "0..*" --> "1" FaqEntry : generada por
    TokenService --> Profile : emite tokens para
```

---

## Diagrama de componentes — Arquitectura general

```mermaid
graph TD
    subgraph Frontend [Frontend — Vanilla JS]
        F1[auth.js]
        F2[Catálogo + Categorías]
        F3[Carrito + Checkout]
        F4[Órdenes]
        F5[Chat]
        F6[Panel Admin]
    end

    subgraph Backend [Backend — FastAPI]
        subgraph Adapters
            A1[Routers REST]
            A2[WebSocket Router]
            A3[Schemas + Dependencies]
        end
        subgraph Application
            B1[ProductService]
            B2[SessionService]
            B3[OrderService]
            B4[ChatService]
            B5[ProfileService]
        end
        subgraph Domain
            C1[Entidades]
            C2[Ports / Interfaces]
            C3[Errores de dominio]
        end
        subgraph Infrastructure
            D1[SQLAlchemy Repositories]
            D2[InMemory Repositories]
            D3[TokenService]
            D4[PasswordHasher]
        end
    end

    subgraph DB [Base de datos]
        E1[(PostgreSQL)]
    end

    subgraph Realtime [Tiempo real]
        R1[ConnectionManager]
        R2[FAQ Matcher en memoria]
    end

    F1 -->|POST /sessions, /profiles| A1
    F2 -->|GET /products| A1
    F3 -->|POST /orders| A1
    F4 -->|GET /orders| A1
    F5 -->|WS /realtime/chat| A2
    F6 -->|CRUD /products, /orders/admin| A1

    A1 --> B1
    A1 --> B2
    A1 --> B3
    A1 --> B5
    A2 --> B4

    B1 --> C2
    B2 --> C2
    B3 --> C2
    B4 --> C2
    B5 --> C2

    C2 --> D1
    C2 --> D2
    B2 --> D3
    B2 --> D4
    B5 --> D4

    D1 --> E1
    A2 --> R1
    B4 --> R2
```

---

## Diagrama de arquitectura hexagonal (Backend)

```mermaid
graph LR
    subgraph Núcleo
        D[Domain\nEntidades + Ports]
        A[Application\nUse Cases / Services]
    end

    subgraph Exterior
        direction TB
        In[Adapters de entrada\nHTTP Routers\nWebSocket Router]
        Out[Adapters de salida\nSQLAlchemy Repos\nInMemory Repos\nTokenService\nPasswordHasher]
    end

    In -->|llama| A
    A -->|usa puertos| D
    D -->|implementado por| Out
```

---

## Variables de entorno requeridas (Backend)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/ecom` |
| `JWT_SECRET` | Clave secreta para firmar tokens | `mi-secreto-seguro` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del access token | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Duración del refresh token | `30` |

---

## Roles del sistema

| Rol | Accesos |
|---|---|
| `customer` | Catálogo, carrito, checkout, órdenes propias, chat |
| `operator` | Todo lo anterior + ver todas las órdenes + cambiar estados + admin de chat |
| `admin` | Todo lo anterior + CRUD de productos + subir imágenes |
