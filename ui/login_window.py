from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame, QStackedWidget, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from controllers.auth_controller import AuthController

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛогистТранс - Вход")
        self.resize(1200, 800)
        self.controller = AuthController()
        
    
        self.setStyleSheet("""
            QWidget#MainWindow {
                background-color: #111827; /* Очень темный синий/серый */
            }
            QFrame#LoginCard {
                background-color: white;
                border-radius: 12px;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: #F9FAFB;
                color: #111827;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
                background-color: #FFFFFF;
            }
            QPushButton#PrimaryButton {
                background-color: #2563EB;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton#LinkButton {
                background-color: transparent;
                color: #2563EB;
                border: none;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton#LinkButton:hover {
                text-decoration: underline;
            }
            QLabel#InputLabel {
                color: #6B7280; /* Серый текст */
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 4px;
                margin-top: 10px;
            }
        """)
        
        self.setObjectName("MainWindow")
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Карточка
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setFixedSize(400, 700) 
        
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(40, 40, 40, 40)
        self.card_layout.setSpacing(10)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_login_page())
        self.stack.addWidget(self.create_register_page())
        
        self.card_layout.addWidget(self.stack)
        main_layout.addWidget(self.card)

    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Иконка и Заголовок
        icon_lbl = QLabel("🚚") 
        icon_lbl.setStyleSheet("font-size: 40px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("ЛогистТранс")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827; margin-top: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Вход в систему")
        subtitle.setStyleSheet("font-size: 14px; color: #6B7280; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(icon_lbl)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        # 2. Поля ввода
        layout.addWidget(QLabel("ЛОГИН", objectName="InputLabel"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("admin")
        layout.addWidget(self.login_input)
        
        layout.addWidget(QLabel("ПАРОЛЬ", objectName="InputLabel"))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.returnPressed.connect(self.auth)
        layout.addWidget(self.pass_input)
        
        layout.addSpacing(20)
        
        # 3. Кнопка
        btn_login = QPushButton("Войти")
        btn_login.setObjectName("PrimaryButton")
        btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_login.clicked.connect(self.auth)
        layout.addWidget(btn_login)
        
        layout.addSpacing(10)
        
        # 4. Ссылка на регистрацию
        btn_reg = QPushButton("Регистрация нового пользователя")
        btn_reg.setObjectName("LinkButton")
        btn_reg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_reg.clicked.connect(lambda: self.stack.setCurrentIndex(1)) 
        layout.addWidget(btn_reg, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return page

    def create_register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Регистрация")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #111827; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Поля
        self.reg_name = QLineEdit(); self.reg_name.setPlaceholderText("Имя")
        layout.addWidget(QLabel("ИМЯ", objectName="InputLabel"))
        layout.addWidget(self.reg_name)

        self.reg_surname = QLineEdit(); self.reg_surname.setPlaceholderText("Фамилия")
        layout.addWidget(QLabel("ФАМИЛИЯ", objectName="InputLabel"))
        layout.addWidget(self.reg_surname)
        
        self.reg_login = QLineEdit(); self.reg_login.setPlaceholderText("Логин")
        layout.addWidget(QLabel("ЛОГИН", objectName="InputLabel"))
        layout.addWidget(self.reg_login)

        self.reg_pass = QLineEdit(); self.reg_pass.setPlaceholderText("Пароль")
        self.reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("ПАРОЛЬ", objectName="InputLabel"))
        layout.addWidget(self.reg_pass)

        # Выбор роли
        self.reg_role = QComboBox()
        self.reg_role.addItems(["Логист (logist)", "Водитель (driver)", "Руководитель (director)"])

        self.role_map = {0: 'logist', 1: 'driver', 2: 'director'}
        
        layout.addWidget(QLabel("РОЛЬ", objectName="InputLabel"))
        layout.addWidget(self.reg_role)
        
        layout.addSpacing(20)
        
        btn_register = QPushButton("Создать аккаунт")
        btn_register.setObjectName("PrimaryButton")
        btn_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_register.clicked.connect(self.process_registration)
        layout.addWidget(btn_register)
        
        btn_back = QPushButton("← Вернуться ко входу")
        btn_back.setObjectName("LinkButton")
        btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0)) # Назад
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        return page

    def auth(self):
        login = self.login_input.text().strip()
        password = self.pass_input.text().strip()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        user = self.controller.login(login, password)
        
        if user:
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка входа", "Неверный логин или пароль.")

    def process_registration(self):
        name = self.reg_name.text().strip()
        surname = self.reg_surname.text().strip()
        login = self.reg_login.text().strip()
        password = self.reg_pass.text().strip()
        
        role_idx = self.reg_role.currentIndex()
        role_code = self.role_map[role_idx]
        
        if not name or not surname or not login or not password:
            QMessageBox.warning(self, "Внимание", "Заполните все поля!")
            return
            
        success, message = self.controller.register(name, surname, login, password, role_code)
        
        if success:
            QMessageBox.information(self, "Успех", message)
            self.stack.setCurrentIndex(0) 
            self.login_input.setText(login) 
            self.pass_input.setFocus()
        else:
            QMessageBox.critical(self, "Ошибка", message)