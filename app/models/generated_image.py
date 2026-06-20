from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("brand_assets.id"), nullable=True)
    prompt = Column(String(500), nullable=False)
    negative_prompt = Column(String(500), nullable=True)
    filepath = Column(String(500), nullable=False)
    url = Column(String(500), nullable=True)
    steps = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="generated_images")
    asset = relationship("BrandAsset")
