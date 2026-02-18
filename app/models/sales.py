from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total = Column(Numeric)
    paid = Column(Numeric)
    balance = Column(Numeric)
    status = Column(String)
