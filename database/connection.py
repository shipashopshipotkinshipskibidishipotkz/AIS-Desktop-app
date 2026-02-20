from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database.models import Base, User, Client, Vehicle, WarehouseZone, Order, SystemLog
import hashlib
import random

# Создаем движок
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    return SessionLocal()

def init_db():
    Base.metadata.create_all(bind=engine)

