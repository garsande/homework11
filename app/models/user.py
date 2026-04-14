# app/models/user.py
#This module defines the User model which represents users in the system.

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    
    #User model representing a user in the system.
    
    
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid4,nullable=False  )
    username = Column(String(50),unique=True,nullable=False,index=True)
    email = Column(String(100),unique=True,nullable=False,index=True)
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # Relationship to calculations
    # back_populates creates a bidirectional relationship
    # cascade="all, delete-orphan" ensures calculations are deleted
    # when user is deleted
    calculations = relationship("Calculation",back_populates="user",cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
