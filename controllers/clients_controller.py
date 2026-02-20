from database.connection import get_db
from database.models import Client, Order
from sqlalchemy.orm import joinedload
from services.business_service import BusinessService

class ClientsController:
    def get_all(self):
        db = get_db()
        try: return db.query(Client).all()
        finally: db.close()

    def get_client_orders(self, client_id):
        db = get_db()
        try:
            # Подгружаем историю заказов клиента
            return db.query(Order).options(joinedload(Order.vehicle)).filter(Order.client_id == client_id).all()
        finally:
            db.close()

    def add(self, name, phone, email, address):
        if not BusinessService.validate_client_name(name): return False, "Название/ФИО должно быть от 2 до 150 символов."
        if not BusinessService.validate_phone(phone): return False, "Неверный формат телефона. Пример: +7 999 123-45-67"
        if email and not BusinessService.validate_email(email): return False, "Некорректный Email."
        if address and not BusinessService.validate_address(address): return False, "Адрес не должен превышать 200 символов."

        db = get_db()
        try:
            db.add(Client(name=name, phone=phone, email=email, address=address))
            db.commit()
            return True, "Клиент добавлен."
        except:
            db.rollback()
            return False, "Ошибка базы данных."
        finally:
            db.close()

    def update(self, client_id, name, phone, email, address):
        if not BusinessService.validate_client_name(name): return False, "Название/ФИО должно быть от 2 до 150 символов."
        if not BusinessService.validate_phone(phone): return False, "Неверный формат телефона."
        if email and not BusinessService.validate_email(email): return False, "Некорректный Email."
        
        db = get_db()
        try:
            c = db.query(Client).get(client_id)
            if c:
                c.name = name; c.phone = phone; c.email = email; c.address = address
                db.commit()
                return True, "Обновлено."
            return False, "Клиент не найден."
        finally: db.close()
    
    def delete(self, client_id):
        db = get_db()
        try:
            c = db.query(Client).filter(Client.id == client_id).first()
            if c:
                db.delete(c)
                db.commit()
        finally:
            db.close()