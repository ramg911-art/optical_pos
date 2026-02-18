from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))

    brand = Column(String)
    barcode = Column(String)
    selling_price = Column(Numeric)
    gst_percent = Column(Numeric)
    stock_qty = Column(Integer)
