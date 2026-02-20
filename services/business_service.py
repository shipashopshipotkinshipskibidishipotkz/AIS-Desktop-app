import re
import random

class BusinessService:
    
    @staticmethod
    def calculate_route_stats(start_point, end_point):
        """Имитация расчета расстояния"""
        distance = random.randint(50, 2000)
        cost = (distance * 45) + 2000
        return distance, cost

    @staticmethod
    def check_maintenance_needed(vehicle):
        LIMIT_TRIPS = 10
        if vehicle.trips_since_service >= LIMIT_TRIPS:
            return True, "Превышен лимит рейсов"
        return False, "ОК"

    @staticmethod
    def validate_password(password):
        """ТП стр 8: Пароль [*] {6, 32}"""
        return 6 <= len(password) <= 32

    @staticmethod
    def validate_client_name(name):
        """ТП стр 8: Название компании/ФИО {2, 150}"""
        return 2 <= len(name.strip()) <= 150

    @staticmethod
    def validate_phone(phone):
        """ТП стр 8: Строгий формат телефона ^((8|\+7)[\- ]?)?..."""
        if not phone: return False
        pattern = r"^(8|\+7)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_email(email):
        """ТП стр 8: Формат name@domain.ru"""
        if not email: return True 
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_address(address):
        """ТП стр 9: Адрес до 200 символов"""
        return len(address) <= 200

    @staticmethod
    def validate_plate(plate):
        """ТП стр 9: Госномер Формат (А123ВС77)"""
        pattern = r"^[А-Яа-яA-Za-z]\d{3}[А-Яа-яA-Za-z]{2}\d{2,3}$"
        clean_plate = plate.replace(" ", "").upper()
        return re.match(pattern, clean_plate) is not None

    @staticmethod
    def validate_vehicle_model(model):
        """ТП стр 9: Модель авто до 50 символов"""
        return len(model) <= 50