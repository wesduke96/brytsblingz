"""
Database models for Bryt Piercing Studio
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Client(Base):
    """Client/customer model"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="client")


class Service(Base):
    """Piercing service model"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, default="Ear")  # Ear, Nose, Face, Oral, Body, Other
    description = Column(Text)
    price = Column(Float, nullable=False)  # Single piercing price
    pair_price = Column(Float, nullable=True)  # Pair price (if applicable)
    duration_minutes = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="service")


class Appointment(Base):
    """Appointment booking model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    quantity = Column(Integer, default=1)  # 1 = single, 2 = pair (second half off)
    status = Column(String(20), default="pending")  # pending, confirmed, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    
    @property
    def total_price(self):
        """Calculate total price with second-half-off discount"""
        if self.quantity == 1:
            return self.service.price
        elif self.quantity == 2:
            return self.service.price + (self.service.price / 2)
        else:
            # For 3+, first full price, rest half off
            return self.service.price + ((self.quantity - 1) * (self.service.price / 2))


class EarCreation(Base):
    """Ear creation product model (for shop)"""
    __tablename__ = "ear_creations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    amazon_url = Column(String(500))  # Link to Amazon storefront
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContactMessage(Base):
    """Contact form submissions"""
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CurationRequest(Base):
    """Curation / jewelry styling requests"""
    __tablename__ = "curation_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    socials = Column(String(255), default="")
    area = Column(String(50), nullable=False)   # ear, face, full-body
    metal = Column(String(50), nullable=False)  # gold, silver, mixed
    notes = Column(Text, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminUser(Base):
    """Admin user with bcrypt-hashed password"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


class AdminSession(Base):
    """Persistent admin sessions stored in DB"""
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

