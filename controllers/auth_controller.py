from database.connection import get_db
from database.models import User
from services.security_service import SecurityService
from services.business_service import BusinessService
class AuthController:
    def login(self, login, password):
        db = get_db()
        try:
            user = db.query(User).filter(User.login == login).first()
            if user and SecurityService.verify_password(password, user.password):
                return user
            return None
        finally:
            db.close()

    def register(self, name, surname, login, password, role):
        if not BusinessService.validate_password(password):
            return False, "Пароль должен содержать от 6 до 32 символов!"
        if len(login) < 4:
            return False, "Логин должен содержать минимум 4 символа."

        db = get_db()
        try:
            existing = db.query(User).filter(User.login == login).first()
            if existing: return False, "Такой логин уже занят"

            hashed_pw = SecurityService.hash_password(password)
            new_user = User(login=login, password=hashed_pw, role=role, name=name, surname=surname)
            db.add(new_user)
            db.commit()
            return True, "Пользователь успешно зарегистрирован"
        except Exception as e:
            db.rollback()
            return False, f"Ошибка: {str(e)}"
        finally:
            db.close()