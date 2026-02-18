## Optical POS – Project Summary

This document provides a high‑level overview of the Optical POS backend implemented with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. It covers the architecture, domain models, API routes, and database structure so you can quickly understand and work on the system safely.

---

## 1. Architecture Overview

- **Tech stack**
  - **API**: FastAPI
  - **DB**: PostgreSQL (via SQLAlchemy ORM)
  - **Auth**: JWT (python‑jose) with bcrypt password hashing
  - **PDFs**: ReportLab for invoice PDF generation

- **Main modules / layering**
  - **Application entrypoint**
    - `app/main.py`
    - Creates the FastAPI app, configures CORS, and registers all routers.
  - **API layer (routing & HTTP)**
    - Directory: `app/api/`
    - Files: `auth.py`, `items.py`, `sales.py`, `lens.py`, `purchase.py`, `supplier.py`, `dashboard.py`, `prescriptions.py`, `deps.py`, `security.py`.
    - Defines all HTTP endpoints, wiring them to CRUD functions and dependencies such as DB sessions and authentication.
  - **CRUD / service layer**
    - Directory: `app/crud/`
    - Files: `item.py`, `sales.py`, `purchase.py`, `supplier.py`, `lens.py`, `dashboard.py`.
    - Encapsulates business logic and database operations, keeping route handlers thin.
  - **Domain models (ORM)**
    - Directory: `app/models/`
    - Primary file: `all_models.py` – contains the complete SQLAlchemy model set used by the app.
    - Other model files (`user.py`, `item.py`, `sales.py`, `lens.py`) exist but the active models are in `all_models.py`.
  - **Pydantic schemas (request/response models)**
    - Directory: `app/schemas/`
    - Files: `item.py`, `sales.py`, `purchase.py`, `supplier.py`, `lens.py`.
    - Define the shapes of request payloads and responses for the API.
  - **Core infrastructure**
    - `app/core/database.py` – SQLAlchemy engine, session factory, and declarative `Base`.
    - `app/core/config.py` – configuration for `DATABASE_URL` (PostgreSQL).
    - `app/core/security.py` – password hashing and JWT token creation/verification.
  - **Services / utilities**
    - `app/services/invoice_pdf.py` – generates PDF invoices using ReportLab into `app/invoices/`.

---

## 2. Application Entry & Core Infrastructure

- **FastAPI app (`app/main.py`)**
  - Creates the application:
    - `app = FastAPI(title="Optical POS API")`
  - Configures **CORS** using `CORSMiddleware` with permissive settings (intended for development):
    - `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`.
  - Defines a simple **health endpoint**:
    - `GET /` → `{ "status": "running" }`.
  - Includes routers from `app.api`:
    - `auth_router`, `items_router`, `sales_router`, `lens_router`,
      `purchase_router`, `supplier_router`, `dashboard_router`, `rx_router`.

- **Database core (`app/core/database.py`)**
  - Loads `DATABASE_URL` from `app.core.config`.
  - Creates a SQLAlchemy engine:
    - `engine = create_engine(DATABASE_URL)`
  - Configures session factory:
    - `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
  - Defines declarative base:
    - `Base = declarative_base()`

- **Configuration (`app/core/config.py`)**
  - Provides `DATABASE_URL`, defaulting to a PostgreSQL connection string if the `DATABASE_URL` environment variable is not set.
  - Intended DB: **PostgreSQL** (`postgresql://posuser:strongpassword@localhost/optical_pos` by default).

- **Security (`app/core/security.py`)**
  - Password hashing/verification:
    - Uses `passlib` `CryptContext` with `bcrypt`.
  - JWT creation:
    - Uses `python‑jose` to sign tokens with a `SECRET_KEY` and `HS256`.
    - Tokens include a subject (`sub`, typically user id) and `exp` (expiration) derived from `ACCESS_TOKEN_EXPIRE_MINUTES`.

---

## 3. Domain Models (ORM) – `app/models/all_models.py`

All main database tables are defined as SQLAlchemy models extending `Base` from `app.core.database`.

### 3.1 Users & Roles

- **Role**
  - Table: `roles`
  - Fields: `id`, `name`
  - Relations:
    - `users`: one‑to‑many to `User`.
  - Purpose: application role (e.g., admin, staff).

- **User**
  - Table: `users`
  - Fields: `id`, `username` (unique), `password_hash`, `role_id`, `is_active`, `created_at`.
  - Relations:
    - `role`: many‑to‑one to `Role`.
  - Purpose: authenticated system user accounts.

### 3.2 Customers & Suppliers

- **Customer**
  - Table: `customers`
  - Fields: `id`, `name`, `phone` (unique), `created_at`.
  - Relations:
    - `sales`: one‑to‑many to `Sale` (cascade delete‑orphan).
  - Purpose: end customers / patients.

- **Supplier**
  - Table: `suppliers`
  - Fields: `id`, `name`, `phone`, `gstin`, `address`, `created_at`.
  - Relations:
    - `purchases`: one‑to‑many to `Purchase`.
    - `lens_orders`: one‑to‑many to `LensOrder`.
  - Purpose: product and lens vendors.

### 3.3 Inventory: Categories, Items, StockMovements

- **Category**
  - Table: `categories`
  - Fields: `id`, `name` (unique).
  - Relations:
    - `items`: one‑to‑many to `Item`.
  - Purpose: groups items into categories (frames, lenses, etc.).

- **Item**
  - Table: `items`
  - Fields (key): `id`, `name`, `category_id`, `brand`, `model`, `color`, `size`,
    `barcode`, `hsn_code`, `cost_price`, `selling_price`, `gst_percent`,
    `stock_qty`, `reorder_level`, `created_at`.
  - Relations:
    - `category`: many‑to‑one to `Category`.
  - Purpose: individual inventory items with pricing and GST data.

- **StockMovement**
  - Table: `stock_movements`
  - Fields: `id`, `item_id`, `change_qty`, `movement_type`, `reference_id`, `created_at`.
  - Purpose: audit trail for inventory changes (e.g., purchases, corrections).

### 3.4 Purchasing

- **Purchase**
  - Table: `purchases`
  - Fields: `id`, `supplier_id`, `invoice_no`, `date`, `total`, `created_at`.
  - Relations:
    - `supplier`: many‑to‑one to `Supplier`.
    - `items`: one‑to‑many to `PurchaseItem`.
  - Purpose: purchase header for supplier invoices.

- **PurchaseItem**
  - Table: `purchase_items`
  - Fields: `id`, `purchase_id`, `item_id`, `qty`, `price`, `gst_percent`.
  - Relations:
    - `purchase`: many‑to‑one to `Purchase`.
  - Purpose: line items within a purchase; also drive stock increments and stock movement logs.

### 3.5 Sales, Sale Items, Payments, Delivery

- **Sale**
  - Table: `sales`
  - Fields: `id`, `customer_id`, `customer_name`, `customer_phone`, `total`,
    `paid`, `balance`, `status`, `created_by`, `created_at`.
  - Relations:
    - `customer`: many‑to‑one to `Customer`.
    - `items`: one‑to‑many to `SaleItem` (cascade).
    - `prescriptions`: one‑to‑many to `Prescription` (cascade).
    - `lens_orders`: one‑to‑many to `LensOrder` (cascade).
    - `payments`: one‑to‑many to `Payment` (cascade).
  - Purpose: sales/invoices tying together customer, items, payments, and clinical data.

- **SaleItem**
  - Table: `sale_items`
  - Fields:
    - Core: `id`, `sale_id`, `item_id`, `qty`, `price`.
    - Stored GST fields: `gst_percent`, `gst_amount`, `cgst`, `sgst`, `taxable_value`.
  - Relations:
    - `sale`: many‑to‑one to `Sale`.
    - `item`: many‑to‑one to `Item`.
  - Helper properties:
    - `gross_value`, `effective_taxable_value`, `effective_gst_percent`,
      `effective_gst_amount`, `effective_cgst`, `effective_sgst`, `total_value`.
  - Purpose: detailed taxable accounting per line item.

- **Payment**
  - Table: `payments`
  - Fields: `id`, `sale_id`, `amount`, `method`, `created_at`.
  - Relations:
    - `sale`: many‑to‑one to `Sale`.
  - Purpose: individual payments against a sale (cash, card, etc.).

- **Delivery**
  - Table: `deliveries`
  - Fields: `id`, `sale_id`, `expected_date`, `delivered`, `delivered_at`.
  - Purpose: tracks delivery status for a sale order.

### 3.6 Clinical: Prescriptions & Lens Orders

- **Prescription**
  - Table: `prescriptions`
  - Fields (key): `id`, `sale_id`, `sphere_r`, `cyl_r`, `axis_r`, `add_r`,
    `sphere_l`, `cyl_l`, `axis_l`, `add_l`, `pd`, `notes`, `created_at`.
  - Relations:
    - `sale`: many‑to‑one to `Sale`.
    - `lens_orders`: one‑to‑many to `LensOrder`.
  - Purpose: stores optical prescription data tied to a sale.

- **LensOrder**
  - Table: `lens_orders`
  - Fields (key): `id`, `sale_id`, `prescription_id`, `lens_type`, `index_value`,
    `coating`, `tint`, `supplier_id`, `order_date`, `expected_date`, `status`, `created_at`.
  - Relations:
    - `sale`: many‑to‑one to `Sale`.
    - `prescription`: many‑to‑one to `Prescription`.
    - `supplier`: many‑to‑one to `Supplier`.
    - `logs`: one‑to‑many to `LensOrderStatusLog` (cascade).
  - Purpose: tracks external lens orders linked to prescriptions and suppliers.

- **LensOrderStatusLog**
  - Table: `lens_order_status_log`
  - Fields: `id`, `lens_order_id`, `status`, `changed_at`, `changed_by`.
  - Relations:
    - `order`: many‑to‑one to `LensOrder`.
  - Purpose: audit log of status changes for lens orders.

---

## 4. Pydantic Schemas – `app/schemas/*`

Schemas define request and response structures for endpoints, decoupled from ORM models.

- **Items & Categories (`app/schemas/item.py`)**
  - Category schemas: `CategoryCreate`, `CategoryOut`, `CategoryUpdate`.
  - Item schemas: `ItemCreate`, `ItemOut`, `ItemUpdate`.
  - Used in `/items` routes for creation, listing, and updates.

- **Sales & Payments (`app/schemas/sales.py`)**
  - Input: `SaleItemIn`, `SaleCreate` (captures items, payment details, and customer info).
  - Output: `SaleItemOut`, `PaymentOut`, `SaleDetailOut`, `SaleOut` with GST breakdowns.

- **Purchases (`app/schemas/purchase.py`)**
  - Input: `PurchaseItemIn`, `PurchaseCreate` to represent supplier invoices with line items.

- **Suppliers (`app/schemas/supplier.py`)**
  - `SupplierCreate`, `SupplierOut` covering name, phone, GSTIN, and address.

- **Prescriptions & Lens Orders (`app/schemas/lens.py`)**
  - `PrescriptionCreate` – prescription data.
  - `LensOrderCreate` – lens order payload (sale, prescription, supplier, dates, status).
  - `StatusUpdate` – simple status update payload for lens orders.

---

## 5. API Routing Structure – `app/api/*`

Routers are created with `APIRouter` and included in `app/main.py`. Most routes depend on authentication via `get_current_user`.

### 5.1 Authentication – `app/api/auth.py`

- Router: `prefix="/auth"`, `tags=["auth"]`.
- Key endpoint:
  - `POST /auth/login`
    - Accepts username/password.
    - Verifies user credentials against the `User` table.
    - Returns a JWT access token (`access_token`, `token_type="bearer"`).

### 5.2 Items & Categories – `app/api/items.py`

- Router: `prefix="/items"`, `tags=["Items"]`.
- All endpoints require `get_current_user` (from `app.api.security`).
- Endpoints:
  - `POST /items/categories` – create category.
  - `GET /items/categories` – list categories.
  - `PUT /items/categories/{cid}` – update category.
  - `DELETE /items/categories/{cid}` – delete category.
  - `POST /items/` – create inventory item.
  - `GET /items/` – list items.
  - `PUT /items/{item_id}` – update item.
  - `DELETE /items/{item_id}` – delete item.
  - `GET /items/search` – query by name/brand/model.
  - `GET /items/low-stock` – list items where `stock_qty <= reorder_level`.
- Talks to `app.crud.item` and sometimes queries `Item` directly.

### 5.3 Sales & Invoices – `app/api/sales.py`

- Router: `prefix="/sales"`, `tags=["Sales"]`.
- Requires `get_current_user` for all endpoints.
- Endpoints:
  - `POST /sales/` – create a sale (`SaleCreate`), calling `app.crud.sales.create_sale`.
  - `GET /sales/{sale_id}` – returns detailed sale info, GST breakdown, items, and payments (`get_sale`).
  - `GET /sales/{sale_id}/pdf` – generates an invoice PDF via `app.services.invoice_pdf.generate_invoice_pdf` and returns it as a `FileResponse`.
  - `POST /sales/{sale_id}/return` – process item returns and adjust stock and sale balances.
  - `GET /sales/{sale_id}/return-pdf` – generate a PDF return/credit note using ReportLab and return as `StreamingResponse`.
  - `GET /sales/` – list recent sales with basic info.

### 5.4 Prescriptions – `app/api/prescriptions.py`

- Router: `prefix="/prescriptions"`, `tags=["prescriptions"]`.
- Endpoints:
  - `POST /prescriptions/` – creates a `Prescription` directly using SQLAlchemy.
    - Cleans empty string fields to `None` before persistence.
    - Currently **does not** enforce authentication (`get_current_user`).

### 5.5 Lens Orders – `app/api/lens.py`

- Router: `prefix="/lens"`, `tags=["Lens"]`.
- Endpoints (auth‑protected via `get_current_user`):
  - `POST /lens/prescription` – creates a prescription using `app.crud.lens.create_prescription`.
  - `POST /lens/order` – creates a `LensOrder` using `create_lens_order`.
  - `PUT /lens/{order_id}/status` – updates lens order status (`update_status`).
  - `GET /lens/` – lists lens orders (`list_orders`).

### 5.6 Purchases – `app/api/purchase.py`

- Router: `prefix="/purchase"`, `tags=["Purchase"]`.
- Endpoints (auth‑protected):
  - `POST /purchase/` – creates a purchase (`PurchaseCreate`) via `app.crud.purchase.create_purchase`.

### 5.7 Suppliers – `app/api/supplier.py`

- Router: `prefix="/suppliers"`, `tags=["Suppliers"]`.
- Endpoints (auth‑protected):
  - `POST /suppliers/` – create supplier.
  - `GET /suppliers/` – list suppliers (implemented twice: once via CRUD, once with direct query).
  - `DELETE /suppliers/{sid}` – delete supplier via CRUD.

### 5.8 Dashboard – `app/api/dashboard.py`

- Router: `prefix="/dashboard"`, `tags=["Dashboard"]`.
- Endpoints (auth‑protected):
  - `GET /dashboard/` – returns aggregated metrics via `app.crud.dashboard.get_dashboard`:
    - Today’s sales totals and count.
    - Today’s purchase totals.
    - Low‑stock items.
    - Pending and ready lens orders.

### 5.9 Shared Dependencies & Auth Helpers – `app/api/deps.py` & `app/api/security.py`

- `app/api/deps.py`
  - `get_db()` – yields `SessionLocal` sessions from `app.core.database`.
  - Declares `oauth2_scheme` and a `get_current_user` implementation (not the primary one used).

- `app/api/security.py`
  - Defines `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")`.
  - `get_current_user`:
    - Validates JWT from the `Authorization: Bearer` header.
    - Loads the `User` from DB.
    - Raises `HTTPException` (401) on invalid or missing auth.
  - This is the helper actually imported by most routers.

---

## 6. CRUD / Business Logic Layer – `app/crud/*`

- **Items (`app/crud/item.py`)**
  - Category CRUD: create, list, update, delete categories.
  - Item CRUD: create, list, update, delete items.
  - Search: simple text search over name/brand/model.

- **Sales (`app/crud/sales.py`)**
  - `create_sale`:
    - Validates stock for requested items.
    - Calculates GST, taxable value, line totals, and persists `SaleItem` rows.
    - Updates `Item.stock_qty` (deducts quantities).
    - Persists payments in `Payment`.
  - `get_sale`:
    - Returns full sale details including customer data, items, GST breakdowns, and payments.
  - Handles sale returns and related stock/balance adjustments.

- **Purchases (`app/crud/purchase.py`)**
  - Creates `Purchase` and `PurchaseItem` records.
  - Updates item stock upwards.
  - Records `StockMovement` entries for traceability.

- **Suppliers (`app/crud/supplier.py`)**
  - Basic supplier create/list/delete helpers.

- **Lens (`app/crud/lens.py`)**
  - `create_prescription` and `create_lens_order`.
  - `update_status` and logging into `LensOrderStatusLog`.
  - `list_orders` returns orders with denormalized fields like patient/supplier names.

- **Dashboard (`app/crud/dashboard.py`)**
  - Aggregates key metrics:
    - Today’s sales totals and counts.
    - Purchases total.
    - Low‑stock items.
    - Count of lens orders by status (pending, ready, etc.).

---

## 7. Database Structure & Relationships

- **Database engine**
  - PostgreSQL, accessed through SQLAlchemy’s synchronous engine.

- **Session management**
  - `SessionLocal` from `app.core.database` is used in a `get_db` dependency to provide a session per request, with proper closing after the request.

- **Key relationships (high‑level)**
  - `Role` (1) ↔ (N) `User`
  - `Customer` (1) ↔ (N) `Sale`
  - `Category` (1) ↔ (N) `Item`
  - `Supplier` (1) ↔ (N) `Purchase`
  - `Purchase` (1) ↔ (N) `PurchaseItem`
  - `Sale` (1) ↔ (N) `SaleItem`
  - `Sale` (1) ↔ (N) `Payment`
  - `Sale` (1) ↔ (N) `Prescription`
  - `Sale` (1) ↔ (N) `LensOrder`
  - `Prescription` (1) ↔ (N) `LensOrder`
  - `Supplier` (1) ↔ (N) `LensOrder`
  - `LensOrder` (1) ↔ (N) `LensOrderStatusLog`

- **Migrations**
  - No explicit Alembic / migrations directory is present in the repo; schema evolution appears to be managed outside of this codebase or manually.

---

## 8. Authentication & Authorization

- **Authentication**
  - Handled via JWT tokens created by `app.core.security.create_access_token`.
  - `POST /auth/login` issues tokens on successful username/password authentication.
  - Protected endpoints depend on `get_current_user` (in `app.api.security`) to:
    - Extract and verify the JWT from the `Authorization` header.
    - Load the `User` from the database.
    - Reject invalid/expired tokens with `401 Unauthorized`.

- **Authorization**
  - A `Role` model exists but there is no explicit role‑based authorization enforcement in the routes.
  - In practice, access is enforced at the **authenticated vs unauthenticated** level in this codebase.

- **Notable detail**
  - Some endpoints (e.g., `POST /prescriptions/` in `app/api/prescriptions.py`) currently do **not** check `get_current_user` and are unauthenticated.

---

## 9. Invoices & PDFs – `app/services/invoice_pdf.py`

- Uses ReportLab to generate PDF invoices:
  - Files are written under `app/invoices` as `invoice_{sale.id}.pdf`.
  - Includes clinic header, sale details (invoice number/date, customer name, phone).
  - Renders a table of items with:
    - HSN code, quantity, rate, taxable value, GST %, GST amount, and line total.
  - Calculates and displays:
    - Subtotal, GST breakdown (CGST/SGST), and grand total.
  - Adds a signature section at the bottom.
- The `/sales/{sale_id}/pdf` endpoint wraps this and returns the generated file via `FileResponse`.

---

## 10. Typical Request Flow

1. **Client authenticates** via `POST /auth/login` and receives a JWT.
2. **Client calls protected APIs** (e.g., `/items`, `/sales`, `/purchase`, `/lens`, `/suppliers`, `/dashboard`) with `Authorization: Bearer <token>`.
3. The router handler:
   - Uses `Depends(get_current_user)` to ensure the user is authenticated.
   - Uses `Depends(get_db)` to obtain a SQLAlchemy session.
   - Calls into the **CRUD layer** (`app.crud.*`) to perform business logic and DB operations.
4. The CRUD function:
   - Reads/writes ORM models (`app.models.all_models`).
   - Commits or rolls back as appropriate.
5. The route returns **Pydantic schemas** (`app.schemas.*`) as responses.
6. For invoices or returns, the service layer creates PDFs, which are streamed or returned as files.

---

## 11. Notes for Future Changes

- **Do not change existing routes lightly**
  - `AGENT.md` indicates this is a production system; keep route paths, shapes, and behaviors backward compatible.
- **Maintain DB compatibility**
  - Any model changes should be coordinated with PostgreSQL schema changes and ideally managed via migrations.
- **Keep the modular structure**
  - New features should follow the same pattern:
    - Schema(s) in `app/schemas/`
    - CRUD logic in `app/crud/`
    - Routes in `app/api/`
    - ORM models in `app/models/all_models.py` (if new tables are needed).

