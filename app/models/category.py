#  SQLAlchemy model (struttura tabella database)

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db_connection import Base

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "ecommerce"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    # relazione con Product
    products = relationship("Product", back_populates="category")
