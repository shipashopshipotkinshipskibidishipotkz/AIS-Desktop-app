from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QDialog, QFormLayout, QLineEdit, 
                             QMessageBox, QComboBox, QHBoxLayout, QLabel, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from controllers.transport_controller import TransportController

class TransportTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.controller = TransportController()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("Управление транспортом")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout.addWidget(header)

        # Фильтры
        filter_layout = QHBoxLayout()
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все типы", "Грузовой", "Легковой", "Спецтехника"])
        self.type_filter.currentTextChanged.connect(self.load_data)
        self.type_filter.setFixedWidth(150)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все статусы", "Свободен", "В работе", "На ремонте"])
        self.status_filter.currentTextChanged.connect(self.load_data)
        self.status_filter.setFixedWidth(150)
        
        filter_layout.addWidget(QLabel("Тип:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Госномер", "Модель", "Тип ТС", "Тоннаж", "Статус", "Водитель"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(45) 
        layout.addWidget(self.table)

        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Добавить ТС")
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self.open_add_dialog)
        
        self.btn_edit = QPushButton("✏ Редактировать")
        self.btn_edit.setObjectName("SecondaryButton")
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        
        self.btn_del = QPushButton("🗑 Удалить")
        self.btn_del.setObjectName("DangerButton")
        self.btn_del.clicked.connect(self.delete_transport)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_del)
        
        layout.addLayout(btn_layout)

        self.apply_permissions()
        self.setLayout(layout)
        self.load_data()

    def apply_permissions(self):
        if self.user.role != 'logist':
            self.btn_add.hide()
            self.btn_edit.hide()
            self.btn_del.hide()

    def create_status_badge(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setObjectName("StatusBadge")
        status_map = {"Свободен": "Done", "В работе": "Work", "На ремонте": "Error"}
        lbl.setProperty("status", status_map.get(text, "New")) 
        widget = QWidget()
        l = QHBoxLayout(widget)
        l.setContentsMargins(10, 2, 10, 2)
        l.addWidget(lbl)
        return widget

    def load_data(self):
        vehicles = self.controller.get_all()
        status_filter = self.status_filter.currentText()
        type_filter = self.type_filter.currentText()
        
        filtered = []
        for v in vehicles:
            if (status_filter == "Все статусы" or v.status == status_filter) and \
               (type_filter == "Все типы" or v.vehicle_type == type_filter):
                filtered.append(v)
        
        self.table.setRowCount(len(filtered))
        for i, v in enumerate(filtered):
            self.table.setItem(i, 0, QTableWidgetItem(str(v.id)))
            
            plate_item = QTableWidgetItem(v.plate_number)
            plate_item.setForeground(Qt.GlobalColor.blue)
            self.table.setItem(i, 1, plate_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(v.model))
            self.table.setItem(i, 3, QTableWidgetItem(v.vehicle_type or "Грузовой"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{v.capacity or 0.0} т."))
            
            self.table.setCellWidget(i, 5, self.create_status_badge(v.status))
            
            d_name = f"{v.driver.surname} {v.driver.name}" if v.driver else "Не назначен"
            self.table.setItem(i, 6, QTableWidgetItem(d_name))

    def open_add_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Новый транспорт")
        f = QFormLayout(d)
        
        plate = QLineEdit()
        model = QLineEdit()
        
        v_type = QComboBox()
        v_type.addItems(["Грузовой", "Легковой", "Спецтехника"])
        
        capacity = QDoubleSpinBox()
        capacity.setMaximum(100.0)
        
        status = QComboBox()
        status.addItems(["Свободен", "В работе", "На ремонте"])
        
        driver_cb = QComboBox()
        driver_cb.addItem("Не назначен", -1)
        drivers = self.controller.get_drivers()
        for dr in drivers:
            driver_cb.addItem(f"{dr.surname} {dr.name}", dr.id)
            
        f.addRow("Госномер:", plate)
        f.addRow("Модель:", model)
        f.addRow("Тип ТС:", v_type)
        f.addRow("Грузоподъемность (т):", capacity)
        f.addRow("Статус:", status)
        f.addRow("Водитель:", driver_cb)
        
        btn = QPushButton("Сохранить")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda: self.save_transport(d, plate.text(), model.text(), v_type.currentText(), capacity.value(), status.currentText(), driver_cb.currentData()))
        f.addRow(btn)
        d.exec()

    def save_transport(self, d, plate, model, v_type, cap, status, driver_id):
        success, msg = self.controller.add(plate, model, v_type, cap, status, driver_id)
        if success:
            d.close()
            self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка валидации", msg)

    def open_edit_dialog(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Внимание", "Выберите строку для редактирования")
            
        v_id = int(self.table.item(row, 0).text())
        vehicle = next((v for v in self.controller.get_all() if v.id == v_id), None)
        if not vehicle: return

        d = QDialog(self)
        d.setWindowTitle("Редактирование ТС")
        f = QFormLayout(d)
        
        plate = QLineEdit(vehicle.plate_number)
        model = QLineEdit(vehicle.model)
        
        v_type = QComboBox()
        v_type.addItems(["Грузовой", "Легковой", "Спецтехника"])
        v_type.setCurrentText(vehicle.vehicle_type or "Грузовой")
        
        capacity = QDoubleSpinBox()
        capacity.setMaximum(100.0)
        capacity.setValue(vehicle.capacity or 0.0)
        
        status = QComboBox()
        status.addItems(["Свободен", "В работе", "На ремонте"])
        status.setCurrentText(vehicle.status)
        
        driver_cb = QComboBox()
        driver_cb.addItem("Не назначен", -1)
        drivers = self.controller.get_drivers()
        for dr in drivers:
            driver_cb.addItem(f"{dr.surname} {dr.name}", dr.id)
        
        if vehicle.driver_id:
            idx = driver_cb.findData(vehicle.driver_id)
            if idx >= 0: driver_cb.setCurrentIndex(idx)
            
        f.addRow("Госномер:", plate)
        f.addRow("Модель:", model)
        f.addRow("Тип ТС:", v_type)
        f.addRow("Грузоподъемность (т):", capacity)
        f.addRow("Статус:", status)
        f.addRow("Водитель:", driver_cb)
        
        btn = QPushButton("Обновить")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda: self.update_transport(d, v_id, plate.text(), model.text(), v_type.currentText(), capacity.value(), status.currentText(), driver_cb.currentData()))
        f.addRow(btn)
        d.exec()

    def update_transport(self, d, v_id, plate, model, v_type, cap, status, driver_id):
        success, msg = self.controller.update(v_id, plate, model, v_type, cap, status, driver_id)
        if success:
            d.close()
            self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка валидации", msg)

    def delete_transport(self):
        row = self.table.currentRow()
        if row >= 0:
            if QMessageBox.question(self, "Удаление", "Удалить транспорт?") == QMessageBox.StandardButton.Yes:
                self.controller.delete(int(self.table.item(row, 0).text()))
                self.load_data()