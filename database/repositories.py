from database.models import Order, Vehicle, Client, WarehouseZone, User
from sqlalchemy.orm import Session

class Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, model):
        return self.db.query(model).all()

    def add(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self):
        self.db.commit()

    def delete(self, obj):
        self.db.delete(obj)
        self.db.commit()