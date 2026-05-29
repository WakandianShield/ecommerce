# Backend — E-commerce de Vinilos

Backend en **FastAPI + PostgreSQL** con arquitectura hexagonal (Ports & Adapters).

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| FastAPI | Framework HTTP y WebSocket |
| SQLAlchemy | ORM y acceso a base de datos |
| PostgreSQL | Base de datos relacional |
| PyJWT + passlib | Seguridad: tokens JWT y hashing de contraseñas |
| python-dotenv | Configuración por variables de entorno |

---

## Estructura de carpetas

```
backend/
├── app/
│   ├── domain/              # Reglas de negocio puras (sin frameworks)
│   │   ├── entities/        # Product, Profile, Order, ChatMessage, FaqEntry, RefreshToken
│   │   ├── ports/           # Interfaces/contratos de repositorios
│   │   └── errors.py        # Excepciones del dominio
│   ├── application/
│   │   └── use_cases/       # Servicios: product, profile, session, order, chat
│   ├── infrastructure/
│   │   ├── config/          # Settings desde variables de entorno
│   │   ├── database/        # Modelos ORM, conexión, repositorios SQLAlchemy
│   │   ├── realtime/        # Repositorios en memoria para chat y FAQ
│   │   └── security/        # PasswordHasher, TokenService
│   ├── adapters/
│   │   └── api/
│   │       ├── routers/     # products, profiles, sessions, orders
│   │       ├── dependencies.py
│   │       └── schemas.py
│   ├── realtime/            # WebSocket: ConnectionManager y router
│   └── main.py
└── scripts/
    ├── create_admin.py          # Crear cuenta de administrador
    └── import_category_products.py
```

---

## Setup

1. Asegúrate de tener PostgreSQL corriendo y la base de datos creada.
2. Crea el archivo `.env` en `backend/`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecom
JWT_SECRET=cambia-esto-en-produccion
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
```

3. Instala dependencias e inicia:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La API queda disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

### Crear cuenta de administrador

Antes de usar el panel admin del frontend, crea al menos un usuario con rol `admin`:

```bash
cd backend
python scripts/create_admin.py --email admin@tienda.com --password MiPassword123 --name "Admin Principal"
```

Si el correo ya existe en la base de datos, el script actualiza su rol a `admin` sin cambiar la contraseña.

---

## Endpoints REST

### Autenticación y perfiles

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/profiles` | Registro de usuario | No |
| GET | `/profiles/me` | Perfil del usuario actual | Bearer |
| POST | `/sessions` | Login | No |
| POST | `/sessions/refresh` | Renovar access token | No |
| POST | `/sessions/logout` | Revocar refresh token | No |

### Productos

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/products` | Listar todos los productos | No |
| GET | `/products/{id}` | Obtener producto | No |
| POST | `/products` | Crear producto | admin |
| PUT | `/products/{id}` | Actualizar producto | admin |
| DELETE | `/products/{id}` | Eliminar producto | admin |
| POST | `/products/{id}/image` | Subir imagen (multipart) | admin |

### Órdenes

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/orders` | Crear orden | Bearer |
| GET | `/orders` | Órdenes del usuario | Bearer |
| GET | `/orders/{id}` | Detalle de orden | Bearer |
| GET | `/orders/admin` | Todas las órdenes | admin/operator |
| PUT | `/orders/{id}/status` | Cambiar estado de orden | admin/operator |

### Chat (WebSocket y admin)

| Tipo | Ruta | Descripción | Auth |
|---|---|---|---|
| WS | `/realtime/chat` | Conexión de chat (param: `session_id`) | No |
| GET | `/realtime/sessions` | Listar sesiones activas | admin/operator |
| GET | `/realtime/sessions/{id}` | Mensajes de una sesión | admin/operator |

---

## Roles

| Rol | Permisos |
|---|---|
| `customer` | Comprar, ver sus órdenes, usar chat |
| `operator` | Ver todas las órdenes, cambiar estados, admin de chat |
| `admin` | Todo lo anterior + CRUD de productos |

---

## Módulo de Autenticación

### Diagrama de casos de uso

```mermaid
graph LR
    Cliente([Cliente])
    Admin([Administrador])
    Op([Operador])

    UC1[Registrarse]
    UC2[Iniciar sesión]
    UC3[Renovar token]
    UC4[Cerrar sesión]
    UC5[Ver perfil]
    UC6[Administrar productos]
    UC7[Administrar órdenes]
    UC8[Acceder a rutas protegidas]

    Cliente --> UC1
    Cliente --> UC2
    Cliente --> UC3
    Cliente --> UC4
    Cliente --> UC5
    Cliente --> UC8

    Admin --> UC2
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8

    Op --> UC2
    Op --> UC7
    Op --> UC8
```

### Diagrama de clases — Auth

```mermaid
classDiagram
    class Profile {
        +UUID id
        +str full_name
        +str email
        +str role
    }
    class ProfileAuth {
        +UUID id
        +str full_name
        +str email
        +str role
        +str password_hash
    }
    class TokenService {
        +str secret
        +str algorithm
        +int access_expire_minutes
        +int refresh_expire_days
        +create_access_token(profile_id, role) str
        +create_refresh_token(profile_id, role) tuple
        +decode_token(token) dict
    }
    class PasswordHasher {
        +hash(password) str
        +verify(password, hash) bool
    }
    class ProfileRepository {
        <<interface>>
        +get_by_email(email) ProfileAuth
        +get_by_id(id) Profile
        +create(full_name, email, password_hash) Profile
    }
    class RefreshTokenRepository {
        <<interface>>
        +create(profile_id, token_id, expires_at) RefreshToken
        +get_valid(token_id) RefreshToken
        +revoke(token_id) None
    }
    class SessionService {
        +login(email, password) tuple
        +refresh(refresh_token) tuple
        +logout(refresh_token) None
        -issue_tokens(profile) tuple
    }
    class ProfileService {
        +register(full_name, email, password) Profile
    }

    SessionService --> TokenService
    SessionService --> PasswordHasher
    SessionService --> ProfileRepository
    SessionService --> RefreshTokenRepository
    ProfileService --> ProfileRepository
    ProfileService --> PasswordHasher
    ProfileAuth --|> Profile
```

### Diagrama de secuencia — Flujo de login

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as Router /sessions
    participant SS as SessionService
    participant PR as ProfileRepository
    participant PH as PasswordHasher
    participant TS as TokenService
    participant DB as PostgreSQL

    C->>API: POST /sessions {email, password}
    API->>SS: login(email, password)
    SS->>PR: get_by_email(email)
    PR->>DB: SELECT * FROM profiles WHERE email=?
    DB-->>PR: ProfileAuth row
    PR-->>SS: ProfileAuth
    SS->>PH: verify(password, password_hash)
    PH-->>SS: True
    SS->>TS: create_access_token(id, role)
    TS-->>SS: access_token (JWT)
    SS->>TS: create_refresh_token(id, role)
    TS-->>SS: refresh_token, token_id
    SS->>DB: INSERT refresh_tokens
    SS-->>API: (access_token, refresh_token, profile)
    API-->>C: 200 {access_token, refresh_token, profile}
```

### Diagrama de secuencia — Validación de JWT y acceso a endpoint protegido

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as Endpoint protegido
    participant Dep as get_current_profile()
    participant TS as TokenService
    participant PR as ProfileRepository
    participant DB as PostgreSQL

    C->>API: GET /profiles/me (Authorization: Bearer <token>)
    API->>Dep: extract token from header
    Dep->>TS: decode_token(token)
    alt Token inválido o expirado
        TS-->>Dep: raise InvalidToken
        Dep-->>C: 401 Unauthorized
    else Token válido
        TS-->>Dep: {sub: profile_id, role, type: "access"}
        Dep->>PR: get_by_id(profile_id)
        PR->>DB: SELECT * FROM profiles WHERE id=?
        DB-->>PR: Profile row
        PR-->>Dep: Profile
        Dep-->>API: current_profile
        API-->>C: 200 {id, full_name, email, role}
    end
```

### Diagrama de arquitectura — Auth

```mermaid
graph TD
    subgraph Adapters
        A1[routers/sessions.py]
        A2[routers/profiles.py]
        A3[dependencies.py]
        A4[schemas.py]
    end

    subgraph Application
        B1[SessionService]
        B2[ProfileService]
    end

    subgraph Domain
        C1[Profile / ProfileAuth]
        C2[RefreshToken]
        C3["ProfileRepository (port)"]
        C4["RefreshTokenRepository (port)"]
        C5[errors.py]
    end

    subgraph Infrastructure
        D1[SqlAlchemyProfileRepository]
        D2[SqlAlchemyRefreshTokenRepository]
        D3[TokenService]
        D4[PasswordHasher]
        D5[PostgreSQL]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B1
    B1 --> C3
    B1 --> C4
    B1 --> D3
    B1 --> D4
    B2 --> C3
    B2 --> D4
    D1 --> C3
    D2 --> C4
    D1 --> D5
    D2 --> D5
```

---

## Módulo de Chat

### Diagrama de casos de uso

```mermaid
graph LR
    Cliente([Cliente])
    Admin([Administrador/Operador])
    Sistema([Sistema])

    UC1[Conectarse al chat]
    UC2[Enviar mensaje]
    UC3[Recibir respuesta automática]
    UC4[Ver sesiones activas]
    UC5[Revisar historial de sesión]
    UC6[Detectar pregunta frecuente]

    Cliente --> UC1
    Cliente --> UC2
    UC2 --> UC3
    UC3 --> UC6
    Admin --> UC4
    Admin --> UC5
    Sistema --> UC6
```

### Diagrama de clases — Chat

```mermaid
classDiagram
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
    class ChatRepository {
        <<interface>>
        +save(message) ChatMessage
        +list_by_session(session_id) List~ChatMessage~
        +list_sessions() List~str~
    }
    class FaqRepository {
        <<interface>>
        +list_all() List~FaqEntry~
    }
    class FaqMatcher {
        <<interface>>
        +match(text) FaqEntry or None
    }
    class SimpleFaqMatcher {
        +match(text) FaqEntry or None
        -normalize(text) str
    }
    class InMemoryChatRepository {
        -dict _store
        -Lock _lock
        +save(message) ChatMessage
        +list_by_session(session_id) List~ChatMessage~
        +list_sessions() List~str~
    }
    class ConnectionManager {
        -dict _connections
        +connect(ws, session_id) None
        +disconnect(session_id) None
        +send_json(session_id, payload) None
    }
    class ChatService {
        +open_session(session_id?) str
        +handle_message(session_id, text) tuple
        +list_messages(session_id) List~ChatMessage~
        +list_sessions() List~str~
    }

    ChatService --> ChatRepository
    ChatService --> FaqMatcher
    SimpleFaqMatcher ..|> FaqMatcher
    SimpleFaqMatcher --> FaqRepository
    InMemoryChatRepository ..|> ChatRepository
    ChatMessage --* ChatRepository
    FaqEntry --* FaqRepository
```

### Diagrama de secuencia — Conexión WebSocket y flujo de mensajes

```mermaid
sequenceDiagram
    participant C as Cliente (browser)
    participant WS as WebSocket Router
    participant CM as ConnectionManager
    participant CS as ChatService
    participant FM as SimpleFaqMatcher
    participant Repo as InMemoryChatRepository

    C->>WS: WS connect /realtime/chat?session_id=
    WS->>CS: open_session(session_id?)
    CS-->>WS: session_id (nuevo o existente)
    WS->>CM: connect(websocket, session_id)
    WS-->>C: {type: "session", session_id: "abc123"}

    loop Por cada mensaje
        C->>WS: texto plano ("¿Tienen envío gratis?")
        WS->>CS: handle_message(session_id, texto)
        CS->>Repo: save(user_message)
        CS->>FM: match(texto)
        FM-->>CS: FaqEntry o None
        CS->>Repo: save(assistant_message)
        CS-->>WS: (user_msg, assistant_msg)
        WS->>CM: send_json(session_id, user_msg)
        WS-->>C: {type: "message", message: {...}}
        WS->>CM: send_json(session_id, assistant_msg)
        WS-->>C: {type: "message", message: {...}}
    end
```

### Diagrama de secuencia — Flujo de respuesta automática (FAQ)

```mermaid
sequenceDiagram
    participant CS as ChatService
    participant FM as SimpleFaqMatcher
    participant FR as InMemoryFaqRepository

    CS->>FM: match("tienen envio gratis?")
    FM->>FM: normalize(texto) → "tienen envio gratis"
    FM->>FR: list_all()
    FR-->>FM: [FaqEntry(keywords=["envio","gratis"]), ...]
    loop Por cada FaqEntry
        FM->>FM: contar coincidencias de keywords en texto
    end
    alt Hay coincidencias
        FM-->>CS: FaqEntry con más keywords coincidentes
        CS-->>CS: assistant_content = faq.answer
    else Sin coincidencias
        FM-->>CS: None
        CS-->>CS: assistant_content = "No encontré respuesta, ¿puedes reformular?"
    end
```

### Diagrama de arquitectura — Chat

```mermaid
graph TD
    subgraph realtime/
        R1[router.py — WS endpoint]
        R2[connection_manager.py]
    end

    subgraph Adapters
        A1[routers/sessions.py — admin endpoints]
    end

    subgraph application/
        B1[ChatService]
    end

    subgraph domain/
        C1[ChatMessage]
        C2[FaqEntry]
        C3["ChatRepository (port)"]
        C4["FaqRepository (port)"]
        C5["FaqMatcher (port)"]
    end

    subgraph infrastructure/realtime/
        D1[InMemoryChatRepository]
        D2[InMemoryFaqRepository]
        D3[SimpleFaqMatcher]
    end

    R1 --> R2
    R1 --> B1
    A1 --> B1
    B1 --> C3
    B1 --> C5
    D1 -->|implementa| C3
    D2 -->|implementa| C4
    D3 -->|implementa| C5
    D3 --> D2
```

---

## Base de datos

```mermaid
erDiagram
    profiles {
        uuid id PK
        string full_name
        string email
        string password_hash
        string role
        datetime created_at
    }
    products {
        uuid id PK
        string name
        text description
        int price_cents
        int stock
        string category
        text image_url
        bool is_active
        datetime created_at
    }
    orders {
        uuid id PK
        uuid profile_id FK
        string status
        int total_cents
        text shipping_address
        datetime created_at
    }
    order_items {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        string name
        int unit_price_cents
        int quantity
    }
    refresh_tokens {
        string id PK
        uuid profile_id FK
        datetime expires_at
        datetime revoked_at
        datetime created_at
    }

    profiles ||--o{ orders : "realiza"
    orders ||--|{ order_items : "contiene"
    products ||--o{ order_items : "referenciado en"
    profiles ||--o{ refresh_tokens : "posee"
```

---

## Notas

- Usa `Authorization: Bearer <access_token>` en todos los endpoints protegidos.
- CORS abierto para desarrollo local con el frontend.
- Las imágenes se guardan en `backend/uploads/` y se sirven en `/media`.
- El chat es completamente en memoria: los mensajes se pierden al reiniciar el servidor.
