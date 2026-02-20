from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QLineEdit, QDialog, QFormLayout, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from controllers.clients_controller import ClientsController

class ClientsTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user  
        self.controller = ClientsController()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("База контрагентов")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout.addWidget(header)

        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск клиента по названию или Email...")
        self.search_input.setFixedWidth(400)
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Телефон", "Email", "Адрес"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(45) 
        layout.addWidget(self.table)

        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Добавить клиента")
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self.open_add_dialog)
        
        self.btn_edit = QPushButton("✏ Редактировать")
        self.btn_edit.setObjectName("SecondaryButton")
        self.btn_edit.clicked.connect(self.open_edit_dialog)

        # НОВАЯ КНОПКА ИСТОРИИ ИЗ ТЕХНИЧЕСКОГО ПРОЕКТА
        self.btn_history = QPushButton("📜 История заказов")
        self.btn_history.setObjectName("SecondaryButton")
        self.btn_history.clicked.connect(self.show_history)
        
        self.btn_del = QPushButton("🗑 Удалить")
        self.btn_del.setObjectName("DangerButton")
        self.btn_del.clicked.connect(self.delete_client)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_history)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_del)
        
        layout.addLayout(btn_layout)

        self.apply_permissions() 
        self.setLayout(layout)
        self.load_data()

    def apply_permissions(self):
        if self.user.role != 'logist':
            self.btn_add.hide(); self.btn_edit.hide(); self.btn_del.hide()

    def load_data(self):
        clients = self.controller.get_all()
        filter_txt = self.search_input.text().lower()
        filtered = [c for c in clients if filter_txt in c.name.lower() or filter_txt in (c.email or "").lower()]
        
        self.table.setRowCount(len(filtered))
        for i, c in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(str(c.id)))
            n_item = QTableWidgetItem(c.name)
            n_item.setForeground(Qt.GlobalColor.blue)
            self.table.setItem(i, 1, n_item)
            self.table.setItem(i, 2, QTableWidgetItem(c.phone))
            self.table.setItem(i, 3, QTableWidgetItem(c.email))
            self.table.setItem(i, 4, QTableWidgetItem(c.address))

    def show_history(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Внимание", "Выберите клиента в таблице")
        c_id = int(self.table.item(row, 0).text())
        client_name = self.table.item(row, 1).text()
        
        orders = self.controller.get_client_orders(c_id)
        
        d = QDialog(self)
        d.setWindowTitle(f"История заказов: {client_name}")
        d.resize(700, 450)
        l = QVBoxLayout(d)
        
        t = QTableWidget(len(orders), 5)
        t.setHorizontalHeaderLabels(["№", "Дата", "Маршрут", "Стоимость", "Статус"])
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.verticalHeader().setVisible(False)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setAlternatingRowColors(True)
        
        for i, o in enumerate(orders):
            t.setItem(i, 0, QTableWidgetItem(f"А{o.id:05d}"))
            date_str = o.created_at.strftime('%d.%m.%Y') if o.created_at else "-"
            t.setItem(i, 1, QTableWidgetItem(date_str))
            t.setItem(i, 2, QTableWidgetItem(f"{o.route_start} - {o.route_end}"))
            t.setItem(i, 3, QTableWidgetItem(f"{o.cost or 0} руб."))
            t.setItem(i, 4, QTableWidgetItem(o.status))
            
        l.addWidget(t)
        d.exec()

    def open_add_dialog(self):
        d = QDialog(self); d.setWindowTitle("Новый клиент"); f = QFormLayout(d)
        name = QLineEdit(); phone = QLineEdit(); email = QLineEdit(); addr = QLineEdit()
        f.addRow("Название/ФИО:", name); f.addRow("Телефон:", phone); f.addRow("Email:", email); f.addRow("Адрес:", addr)
        btn = QPushButton("Сохранить"); btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda: self.save_client(d, name.text(), phone.text(), email.text(), addr.text()))
        f.addRow(btn); d.exec()

    def save_client(self, d, name, phone, email, addr):
        if name:
            success, message = self.controller.add(name, phone, email, addr)
            if success:
                d.close()
                self.load_data()
            else: QMessageBox.warning(self, "Ошибка валидации", message)
        else: QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым")

    def open_edit_dialog(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Внимание", "Выберите клиента")
        c_id = int(self.table.item(row, 0).text())
        client = next((c for c in self.controller.get_all() if c.id == c_id), None)
        if not client: return

        d = QDialog(self); d.setWindowTitle("Редактирование"); f = QFormLayout(d)
        name = QLineEdit(client.name); phone = QLineEdit(client.phone); email = QLineEdit(client.email); addr = QLineEdit(client.address)
        f.addRow("Название/ФИО:", name); f.addRow("Телефон:", phone); f.addRow("Email:", email); f.addRow("Адрес:", addr)
        btn = QPushButton("Обновить"); btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda: self.update_client(d, c_id, name.text(), phone.text(), email.text(), addr.text()))
        f.addRow(btn); d.exec()

    def update_client(self, d, c_id, name, phone, email, addr):
        success, message = self.controller.update(c_id, name, phone, email, addr)
        if success: d.close(); self.load_data()
        else: QMessageBox.warning(self, "Ошибка", message)

    def delete_client(self):
        row = self.table.currentRow()
        if row >= 0:
            if QMessageBox.question(self, "Удаление", "Удалить клиента?") == QMessageBox.StandardButton.Yes:
                self.controller.delete(int(self.table.item(row, 0).text()))
                self.load_data()