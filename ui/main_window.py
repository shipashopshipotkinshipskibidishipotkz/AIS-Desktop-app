from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QMessageBox, QFrame)
from PyQt6.QtCore import QFile, QTextStream, Qt
from config import STYLES_PATH

from ui.dashboard_tab import DashboardTab
from ui.orders_tab import OrdersTab
from ui.transport_tab import TransportTab
from ui.warehouse_tab import WarehouseTab
from ui.clients_tab import ClientsTab
from ui.reports_tab import ReportsTab
from ui.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"ЛогистТранс - {self.get_role_name()} | {user.surname} {user.name}")
        self.resize(1300, 850)
        self.load_styles()
        self.init_ui()

    def get_role_name(self):
        roles = {'logist': 'Логист', 'driver': 'Водитель', 'director': 'Руководитель'}
        return roles.get(self.user.role, self.user.role)

    def load_styles(self):
        file = QFile(STYLES_PATH)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            self.setStyleSheet(QTextStream(file).readAll())

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        main_widget.setLayout(layout)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        
        sb_layout = QVBoxLayout()
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)
        self.sidebar.setLayout(sb_layout)
        
        logo = QLabel("🚚 ЛогистТранс")
        logo.setObjectName("LogoLabel")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        sb_layout.addWidget(logo)
        
        nav_container = QWidget()
        nav_container.setStyleSheet("background-color: transparent;") 
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setContentsMargins(10, 20, 10, 20)
        self.nav_layout.setSpacing(8)
        nav_container.setLayout(self.nav_layout)
        sb_layout.addWidget(nav_container)
        
        self.stack = QStackedWidget()
        self.nav_buttons = []

        tabs_config = [
            ("📊 Главная", DashboardTab(self.user), ['all']),
            ("📦 Заказы", OrdersTab(self.user), ['logist', 'director']),
            ("📍 Маршруты", OrdersTab(self.user), ['driver']), 
            ("🚛 Транспорт", TransportTab(self.user), ['logist', 'director']),
            ("🏭 Склад", WarehouseTab(self.user), ['logist', 'director']),
            ("👥 Клиенты", ClientsTab(self.user), ['logist']),
            ("📑 Отчеты", ReportsTab(self.user), ['logist', 'director']),
            ("⚙ Настройки", SettingsTab(), ['all'])
        ]

        for title, widget, allowed_roles in tabs_config:
            if 'all' not in allowed_roles and self.user.role not in allowed_roles:
                continue
            
            index = self.stack.addWidget(widget)
            btn = QPushButton(title)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index, b=btn: self.switch_tab(idx, b))
            self.nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        profile_frame = QFrame()
        profile_frame.setObjectName("ProfileFrame") 
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setContentsMargins(20, 20, 20, 20)
        profile_layout.setSpacing(5)

        user_lbl = QLabel(f"{self.user.surname} {self.user.name}")
        user_lbl.setObjectName("ProfileName") 
        
        role_lbl = QLabel(self.get_role_name())
        role_lbl.setObjectName("ProfileRole")

        btn_logout = QPushButton("🚪 Выйти из системы")
        btn_logout.setObjectName("LogoutButton")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.logout)

        profile_layout.addWidget(user_lbl)
        profile_layout.addWidget(role_lbl)
        profile_layout.addWidget(btn_logout)
        
        sb_layout.addWidget(profile_frame)
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        if self.nav_buttons:
            self.switch_tab(0, self.nav_buttons[0])

    def switch_tab(self, idx, sender_btn):
        self.stack.setCurrentIndex(idx)
        for b in self.nav_buttons:
            b.setChecked(False)
        sender_btn.setChecked(True)
        
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()

    def logout(self):
        reply = QMessageBox.question(self, 'Выход', 'Сменить пользователя?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()