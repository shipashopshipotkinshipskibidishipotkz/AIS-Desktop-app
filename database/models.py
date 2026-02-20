from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) 
    role = Column(String, nullable=False)
    name = Column(String)
    surname = Column(String)

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    orders = relationship("Order", back_populates="client")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False)
    model = Column(String)
    
    # НОВЫЕ ПОЛЯ ИЗ ТЕХНИЧЕСКОГО ПРОЕКТА:
    vehicle_type = Column(String, default="Грузовой") 
    capacity = Column(Float, default=0.0)             
    
    status = Column(String, default="Свободен") 
    total_mileage = Column(Float, default=0.0) 
    trips_since_service = Column(Integer, default=0) 
    
    driver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    driver = relationship("User") 
    orders = relationship("Order", back_populates="vehicle")

class WarehouseZone(Base):
    __tablename__ = 'warehouse_zones'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    capacity = Column(Float)
    occupied = Column(Float, default=0.0)
    cargo_type = Column(String, nullable=True)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    status = Column(String, default="Новый")
    weight = Column(Float)
    volume = Column(Float)
    route_start = Column(String)
    route_end = Column(String)
    distance = Column(Float, default=0.0)
    cost = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    client_id = Column(Integer, ForeignKey('clients.id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=True)
    warehouse_zone_id = Column(Integer, ForeignKey('warehouse_zones.id'), nullable=True)
    client = relationship("Client", back_populates="orders")
    vehicle = relationship("Vehicle", back_populates="orders")
    warehouse_zone = relationship("WarehouseZone")

class SystemLog(Base):
    __tablename__ = 'system_logs'
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String) 
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)