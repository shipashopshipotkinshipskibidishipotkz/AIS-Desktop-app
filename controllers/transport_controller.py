from sqlalchemy.orm import joinedload
from database.connection import get_db
from database.models import Vehicle, User
from services.business_service import BusinessService

class TransportController:
    def get_all(self):
        db = get_db()
        try:
            return db.query(Vehicle).options(
                joinedload(Vehicle.driver), 
                joinedload(Vehicle.orders)
            ).all()
        finally:
            db.close()
            
    def get_drivers(self):
        db = get_db()
        try:
            return db.query(User).filter(User.role == 'driver').all()
        finally:
            db.close()

    def add(self, plate, model, status, driver_id):
        if not BusinessService.validate_plate(plate): return False, "Неверный формат госномера (Пример: А123ВС77)."
        if not BusinessService.validate_vehicle_model(model): return False, "Модель не может быть пустой или длиннее 50 симв."

        db = get_db()
        try:
            d_id = driver_id if driver_id != -1 else None
            new_v = Vehicle(plate_number=plate.upper(), model=model, status=status, driver_id=d_id)
            db.add(new_v)
            db.commit()
            return True, "Транспорт добавлен."
        except:
            db.rollback()
            return False, "Ошибка: Госномер уже существует."
        finally: db.close()

    def update(self, v_id, plate, model, status, driver_id):
        if not BusinessService.validate_plate(plate): return False, "Неверный формат госномера."
        
        db = get_db()
        try:
            v = db.query(Vehicle).get(v_id)
            if v:
                v.plate_number = plate.upper()
                v.model = model
                v.status = status
                v.driver_id = driver_id if driver_id != -1 else None
                db.commit()
                return True, "Транспорт обновлен."
            return False, "ТС не найдено."
        finally: db.close()

    def delete(self, v_id):
        db = get_db()
        try:
            v = db.query(Vehicle).filter(Vehicle.id == v_id).first()
            if v:
                db.delete(v)
                db.commit()
        finally:
            db.close()