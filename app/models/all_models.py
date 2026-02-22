from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Numeric,
    ForeignKey, Date, TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# =========================================================
# ROLES / USERS
# =========================================================

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password_hash = Column(Text)
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    role = relationship("Role", back_populates="users")


# =========================================================
# CUSTOMERS / SUPPLIERS
# =========================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)

    name = Column(String(200))
    phone = Column(String(20), unique=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # FIXED relationship
    sales = relationship(
        "Sale",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    phone = Column(String(20))
    gstin = Column(String(50))
    address = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    purchases = relationship("Purchase", back_populates="supplier")
    lens_orders = relationship("LensOrder", back_populates="supplier")


# =========================================================
# ITEMS / CATEGORIES
# =========================================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    items = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    category_id = Column(Integer, ForeignKey("categories.id"))

    brand = Column(String(100))
    model = Column(String(100))
    color = Column(String(50))
    size = Column(String(50))

    # Supplier information
    supplier_name = Column(String(200), nullable=True)
    supplier_gst = Column(String(50), nullable=True)
    supplier_contact = Column(String(50), nullable=True)
    supplier_address = Column(Text, nullable=True)

    # Tax and pricing information
    barcode = Column(String(100))
    hsn_code = Column(String(20))

    cost_price = Column(Numeric)
    purchase_price = Column(Numeric)
    selling_price = Column(Numeric)
    gst_percent = Column(Numeric)

    stock_qty = Column(Integer)
    reorder_level = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", back_populates="items")


# =========================================================
# INVENTORY
# =========================================================

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    change_qty = Column(Integer)
    movement_type = Column(String(50))
    reference_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


# =========================================================
# PURCHASES
# =========================================================

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    invoice_no = Column(String(100))
    date = Column(Date)
    total = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now())

    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    qty = Column(Integer)
    price = Column(Numeric)
    gst_percent = Column(Numeric)

    purchase = relationship("Purchase", back_populates="items")


# =========================================================
# SALES
# =========================================================

from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer_name = Column(String(200))
    customer_phone = Column(String(20))

    total = Column(Numeric)
    paid = Column(Numeric)
    balance = Column(Numeric)

    status = Column(String(50), default="COMPLETED")

    created_by = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Advance / balance payment tracking
    advance_amount = Column(Numeric(10, 2), nullable=False, server_default="0")
    advance_payment_mode = Column(String(50), nullable=True)
    advance_payment_date = Column(TIMESTAMP, nullable=True)

    balance_amount = Column(Numeric(10, 2), nullable=False, server_default="0")
    balance_payment_mode = Column(String(50), nullable=True)
    balance_payment_date = Column(TIMESTAMP, nullable=True)

    payment_status = Column(String(50), nullable=False, server_default="pending")
    delivery_status = Column(String(50), nullable=False, server_default="pending")

    # RELATIONSHIPS

    customer = relationship("Customer", back_populates="sales")

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )

    prescriptions = relationship(
        "Prescription",
        back_populates="sale",
        cascade="all, delete-orphan"
    )

    lens_orders = relationship(
        "LensOrder",
        back_populates="sale",
        cascade="all, delete-orphan"
    )

    # THIS FIXES YOUR ERROR
    payments = relationship(
        "Payment",
        back_populates="sale",
        cascade="all, delete-orphan"
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)

    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    qty = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # =============================
    # STORED GST FIELDS (IMPORTANT)
    # =============================

    gst_percent = Column(Numeric(5, 2), nullable=True)
    gst_amount = Column(Numeric(10, 2), nullable=True)
    cgst = Column(Numeric(10, 2), nullable=True)
    sgst = Column(Numeric(10, 2), nullable=True)
    taxable_value = Column(Numeric(10, 2), nullable=True)

    # =============================
    # RELATIONSHIPS
    # =============================

    sale = relationship("Sale", back_populates="items")
    item = relationship("Item")

    # =============================
    # SAFE HELPER PROPERTIES
    # =============================

    @property
    def gross_value(self):
        return float(self.qty or 0) * float(self.price or 0)

    @property
    def effective_taxable_value(self):
        if self.taxable_value is not None:
            return float(self.taxable_value)
        return self.gross_value

    @property
    def effective_gst_percent(self):
        if self.gst_percent is not None:
            return float(self.gst_percent)
        return float(getattr(self.item, "gst_percent", 0) or 0)

    @property
    def effective_gst_amount(self):
        if self.gst_amount is not None:
            return float(self.gst_amount)
        return self.effective_taxable_value * self.effective_gst_percent / 100

    @property
    def effective_cgst(self):
        if self.cgst is not None:
            return float(self.cgst)
        return self.effective_gst_amount / 2

    @property
    def effective_sgst(self):
        if self.sgst is not None:
            return float(self.sgst)
        return self.effective_gst_amount / 2

    @property
    def total_value(self):
        return self.effective_taxable_value + self.effective_gst_amount



class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    sale_id = Column(Integer, ForeignKey("sales.id"))

    amount = Column(Numeric)

    method = Column(String(50))

    created_at = Column(TIMESTAMP, server_default=func.now())

    sale = relationship("Sale", back_populates="payments")



# =========================================================
# DELIVERY
# =========================================================

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    expected_date = Column(Date)
    delivered = Column(Boolean)
    delivered_at = Column(TIMESTAMP)


# =========================================================
# PRESCRIPTIONS
# =========================================================

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True)

    sale_id = Column(Integer, ForeignKey("sales.id"))

    sphere_r = Column(Numeric)
    cyl_r = Column(Numeric)
    axis_r = Column(Integer)
    add_r = Column(Numeric)

    sphere_l = Column(Numeric)
    cyl_l = Column(Numeric)
    axis_l = Column(Integer)
    add_l = Column(Numeric)

    pd = Column(Numeric)
    notes = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())

    sale = relationship("Sale", back_populates="prescriptions")

    lens_orders = relationship(
        "LensOrder",
        back_populates="prescription"
    )

# =========================================================
# LENS ORDERS
# =========================================================

class LensOrder(Base):
    __tablename__ = "lens_orders"

    id = Column(Integer, primary_key=True)

    sale_id = Column(Integer, ForeignKey("sales.id"))
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))

    lens_type = Column(String(100))
    index_value = Column(String(50))
    coating = Column(String(100))
    tint = Column(String(100))

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    order_date = Column(Date)
    expected_date = Column(Date)

    status = Column(String(50))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # RELATIONSHIPS
    sale = relationship("Sale", back_populates="lens_orders")

    prescription = relationship(
        "Prescription",
        back_populates="lens_orders"
    )

    supplier = relationship(
        "Supplier",
        back_populates="lens_orders"
    )

    logs = relationship(
        "LensOrderStatusLog",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class LensOrderStatusLog(Base):
    __tablename__ = "lens_order_status_log"

    id = Column(Integer, primary_key=True)
    lens_order_id = Column(Integer, ForeignKey("lens_orders.id"))
    status = Column(String(50))
    changed_at = Column(TIMESTAMP, server_default=func.now())
    changed_by = Column(Integer, ForeignKey("users.id"))

    order = relationship("LensOrder", back_populates="logs")
