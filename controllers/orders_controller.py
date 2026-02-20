from sqlalchemy.orm import joinedload
from database.connection import get_db
from database.models import Order, Client, Vehicle, SystemLog, WarehouseZone
from services.business_service import BusinessService

class OrdersController:
    def get_all(self):
        db = get_db()
        try:
            return db.query(Order).options(
                joinedload(Order.client), 
                joinedload(Order.vehicle).joinedload(Vehicle.driver),
                joinedload(Order.warehouse_zone)
            ).order_by(Order.id.desc()).all()
        finally:
            db.close()

    def add(self, zone_id, client_id, weight, volume, start, end, vehicle_id):
        db = get_db()
        if float(weight) <= 0: return False, "Вес груза должен быть больше 0."
        if float(volume) <= 0: return False, "Объем груза должен быть больше 0."
        try:
            zone = db.query(WarehouseZone).get(zone_id)
            if not zone:
                return False, "Зона склада не найдена"
            
            if zone.occupied < weight:
                return False, f"На складе недостаточно груза! (Доступно: {zone.occupied} кг)"

            zone.occupied -= weight

            dist, auto_cost = BusinessService.calculate_route_stats(start, end)
            v_id = vehicle_id if vehicle_id != -1 else None
            desc_text = zone.cargo_type or zone.name 

            new_order = Order(
                description=desc_text, 
                warehouse_zone_id=zone_id, 
                cost=auto_cost,     
                distance=dist,      
                client_id=client_id, 
                status="Новый",
                weight=weight,
                volume=volume,
                route_start=start,
                route_end=end,
                vehicle_id=v_id
            )
            db.add(new_order)

            db.add(SystemLog(
                event_type="Order", 
                description=f"Создан заказ на {weight}кг ({desc_text}). Со склада списано."
            ))
            
            db.commit()
            return True, "Заказ создан, груз списан со склада!"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def update(self, order_id, cost, status, vehicle_id, start, end):
        db = get_db()
        try:
            order = db.query(Order).get(order_id)
            if order:
                old_status = order.status
                order.cost = cost
                order.status = status
                order.vehicle_id = vehicle_id if vehicle_id != -1 else None
                order.route_start = start
                order.route_end = end
                
                if old_status != status:
                    db.add(SystemLog(event_type="Order", description=f"Заказ #{order_id}: Статус {status}"))
                    
                    if status == "Доставлен" and order.vehicle_id:
                        v = db.query(Vehicle).get(order.vehicle_id)
                        v.total_mileage += order.distance
                        v.trips_since_service += 1

                db.commit()
                return True, "Обновлено"
            return False, "Не найдено"
        finally:
            db.close()
            
    def delete(self, order_id):
        db = get_db()
        try:
            order = db.query(Order).get(order_id)
            if order:
                db.delete(order)
                db.commit()
        finally:
            db.close()
            
    def get_clients(self):
        db = get_db()
        try: return db.query(Client).all()
        finally: db.close()

    def get_vehicles(self):
        db = get_db()
        try: return db.query(Vehicle).all()
        finally: db.close()

    def get_warehouse_zones(self):
        db = get_db()
        try: return db.query(WarehouseZone).all()
        finally: db.close()