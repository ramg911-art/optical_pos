from sqlalchemy import Column, Integer, String, ForeignKey, Date
from app.core.database import Base

class LensOrder(Base):
    __tablename__ = "lens_orders"

    id = Column(Integer, primary_key=True)

    sale_id = Column(Integer, ForeignKey("sales.id"))
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))

    lens_type = Column(String)
    index_value = Column(String)
    coating = Column(String)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    order_date = Column(Date)
    expected_date = Column(Date)
    status = Column(String)
