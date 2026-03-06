from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from decimal import Decimal
from app.database.session import Base
from datetime import datetime


class Product(Base):
    """Product model representing items in the e-commerce system."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    image = Column(String(500))
    sku = Column(String(50), unique=True, nullable=False, index=True)
    price = Column(Decimal(10, 2), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', title='{self.title[:30]}')>"