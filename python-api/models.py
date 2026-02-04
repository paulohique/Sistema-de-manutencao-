from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Computer(Base):
    __tablename__ = "computers"
    
    id = Column(Integer, primary_key=True, index=True)
    glpi_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity = Column(String(255))
    patrimonio = Column(String(100), index=True)
    serial = Column(String(255))
    location = Column(String(255))
    status = Column(String(50))
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    glpi_data = Column(JSON)  # Dados completos do GLPI
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    components = relationship("ComputerComponent", back_populates="computer", cascade="all, delete-orphan")
    maintenance_history = relationship("MaintenanceHistory", back_populates="computer", cascade="all, delete-orphan")
    notes = relationship("ComputerNote", back_populates="computer", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_computer_name_entity', 'name', 'entity'),
    )


class ComputerComponent(Base):
    __tablename__ = "computer_components"
    
    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"), nullable=False, index=True)
    component_type = Column(String(50), nullable=False)  # CPU, RAM, HD, etc
    name = Column(String(255))
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial = Column(String(255))
    capacity = Column(String(100))  # Para RAM, HD
    component_data = Column(JSON)  # Dados adicionais do componente
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    computer = relationship("Computer", back_populates="components")


class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"
    
    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"), nullable=False, index=True)
    maintenance_type = Column(String(20), nullable=False)  # Preventiva ou Corretiva
    description = Column(Text)
    performed_at = Column(DateTime, nullable=False)
    technician = Column(String(255))
    next_due = Column(DateTime)  # Próxima manutenção agendada
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    computer = relationship("Computer", back_populates="maintenance_history")
    
    __table_args__ = (
        Index('idx_maintenance_type_date', 'maintenance_type', 'performed_at'),
    )


class ComputerNote(Base):
    __tablename__ = "computer_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id", ondelete="CASCADE"), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    computer = relationship("Computer", back_populates="notes")
