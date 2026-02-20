from database.connection import get_db
from database.models import Order, Vehicle, WarehouseZone, User, SystemLog
from sqlalchemy import desc

class DashboardController:
    def get_stats(self, user_id, role):
        db = get_db()
        try:
            q_active = db.query(Order).filter(Order.status == "В пути")
            q_new = db.query(Order).filter(Order.status == "Новый")
            q_done = db.query(Order).filter(Order.status == "Доставлен")

            if role == 'driver':
                q_active = q_active.join(Vehicle).filter(Vehicle.driver_id == user_id)
                q_new = q_new.join(Vehicle).filter(Vehicle.driver_id == user_id)
                q_done = q_done.join(Vehicle).filter(Vehicle.driver_id == user_id)

            active_orders = q_active.count()
            new_orders = q_new.count()
            done_orders = q_done.count()
            
            free_vehicles = db.query(Vehicle).filter(Vehicle.status == "Свободен").count()
            
            zones = db.query(WarehouseZone).all()
            total_cap = sum(z.capacity for z in zones)
            total_occ = sum(z.occupied for z in zones)
            wh_percent = int((total_occ / total_cap * 100)) if total_cap > 0 else 0
            
            return active_orders, new_orders, done_orders, free_vehicles, wh_percent
        finally:
            db.close()

    def get_income_by_days(self):
        db = get_db()
        try:
            income = [0.0, 0.0, 0.0, 0.0, 0.0]
            orders = db.query(Order).all()
            for o in orders:
                if o.cost and o.created_at:
                    weekday = o.created_at.weekday()
                    if weekday < 5:
                        income[weekday] += (o.cost / 1000.0) 
            return income
        finally:
            db.close()

    def get_important_events(self):
        db = get_db()
        events = []
        try:
            broken = db.query(Vehicle).filter(Vehicle.status == "На ремонте").all()
            for v in broken:
                events.append({"text": f"⚠ Машина {v.plate_number} требует ТО ({v.trips_since_service} рейсов)", "type": "danger"})

            zones = db.query(WarehouseZone).all()
            for z in zones:
                if z.capacity > 0 and (z.occupied / z.capacity) > 0.9:
                    perc = int(z.occupied / z.capacity * 100)
                    events.append({"text": f"⚠ Зона {z.name} переполнена ({perc}%)", "type": "danger"})
            
            if not events:
                events.append({"text": "✅ Система работает штатно.", "type": "normal"})
            return events
        finally:
            db.close()

    def get_operations_log(self):
        db = get_db()
        logs = []
        try:
            sys_logs = db.query(SystemLog).order_by(desc(SystemLog.id)).limit(6).all()
            
            for l in sys_logs:
                time_str = l.created_at.strftime("%H:%M")
                
                prefix = ""
                if l.event_type == "Notification": prefix = "📧 "
                elif l.event_type == "Maintenance": prefix = "🔧 "
                elif l.event_type == "Order": prefix = "📦 "
                
                logs.append({
                    "id": l.id, 
                    "time": time_str, 
                    "text": f"{prefix}{l.description}"
                })

            return logs
        finally:
            db.close()