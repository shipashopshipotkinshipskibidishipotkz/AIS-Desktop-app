from database.connection import get_db
from database.models import WarehouseZone

class WarehouseController:
    def get_all(self):
        db = get_db()
        try:
            return db.query(WarehouseZone).all()
        finally:
            db.close()

    def add(self, name, capacity, type):
        if not name or len(name) > 50: return False, "Название зоны до 50 символов."
        if float(capacity) <= 0: return False, "Вместимость должна быть больше 0."

        db = get_db()
        try:
            z = WarehouseZone(name=name, capacity=float(capacity), occupied=0, cargo_type=type)
            db.add(z)
            db.commit()
            return True, "Зона создана."
        except:
            return False, "Ошибка базы данных."
        finally: db.close()
        
    def update_load(self, zone_id, new_load):
        if float(new_load) < 0: return False, "Загрузка не может быть отрицательной."
        db = get_db()
        try:
            z = db.query(WarehouseZone).filter(WarehouseZone.id == zone_id).first()
            if z:
                if new_load > z.capacity: return False, "Загрузка не может превышать вместимость."
                z.occupied = float(new_load)
                db.commit()
                return True, "Остатки обновлены."
            return False, "Зона не найдена."
        finally: db.close()

    def delete(self, z_id):
        db = get_db()
        try:
            z = db.query(WarehouseZone).filter(WarehouseZone.id == z_id).first()
            if z:
                db.delete(z)
                db.commit()
        finally:
            db.close()