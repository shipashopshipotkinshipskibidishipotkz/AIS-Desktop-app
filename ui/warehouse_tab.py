from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QProgressBar, QHBoxLayout, 
                             QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from controllers.warehouse_controller import WarehouseController

class WarehouseTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.controller = WarehouseController()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Управление складом")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout.addWidget(header)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Зона", "Тип груза", "Загрузка (кг)", "Процент"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(45) 
        layout.addWidget(self.table)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Добавить зону")
        self.btn_add.setObjectName("PrimaryButton") 
        self.btn_add.clicked.connect(self.open_add_dialog)
        
        self.btn_upd = QPushButton("📦 Изменить остатки")
        self.btn_upd.setObjectName("SecondaryButton")
        self.btn_upd.clicked.connect(self.open_update_dialog)

        self.btn_del = QPushButton("🗑 Удалить")
        self.btn_del.setObjectName("DangerButton") 
        self.btn_del.clicked.connect(self.delete_zone)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_upd)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_del)
        
        layout.addLayout(btn_layout)

        self.apply_permissions()
        self.setLayout(layout)
        self.load_data()

    def apply_permissions(self):
        if self.user.role != 'logist':
            self.btn_add.hide()
            self.btn_upd.hide()
            self.btn_del.hide()

    def load_data(self):
        zones = self.controller.get_all()
        self.table.setRowCount(len(zones))
        for i, z in enumerate(zones):
            self.table.setItem(i, 0, QTableWidgetItem(str(z.id)))
            
            name_item = QTableWidgetItem(z.name)
            name_item.setForeground(Qt.GlobalColor.blue)
            name_item.setToolTip(f"Тип груза: {z.cargo_type or 'Пусто'}\nЗанято: {z.occupied} из {z.capacity} кг")
            self.table.setItem(i, 1, name_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(z.cargo_type or "-"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{z.occupied} / {z.capacity}"))
            
            pb = QProgressBar()
            perc = int((z.occupied / z.capacity) * 100) if z.capacity > 0 else 0
            pb.setValue(perc)
            pb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pb.setFormat(f"{perc}%")
            
            color = "#22C55E" if perc < 50 else "#EAB308" if perc < 90 else "#EF4444"
            pb.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid #E2E8F0; border-radius: 6px; text-align: center; color: black; background-color: #F8FAFC; height: 20px;}}
                QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}
            """)
            
            w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(10, 5, 10, 5); l.addWidget(pb)
            self.table.setCellWidget(i, 4, w)

    def open_add_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Новая складская зона")
        f = QFormLayout(d)
        name = QLineEdit(); cap = QDoubleSpinBox(); cap.setMaximum(1000000); type_ = QLineEdit()
        
        f.addRow("Название зоны:", name)
        f.addRow("Вместимость (кг):", cap)
        f.addRow("Тип груза:", type_)
        
        btn = QPushButton("Создать")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda: self.save_zone(d, name.text(), cap.value(), type_.text()))
        f.addRow(btn)
        d.exec()

    def save_zone(self, d, name, cap, type_):
        success, msg = self.controller.add(name, cap, type_)
        if success: 
            d.close()
            self.load_data()
        else: 
            QMessageBox.warning(self, "Ошибка валидации", msg)
        
    def open_update_dialog(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Внимание", "Выберите зону для изменения")
        z_id = int(self.table.item(row, 0).text())
        zone = next((z for z in self.controller.get_all() if z.id == z_id), None)
        if not zone: return

        d = QDialog(self)
        d.setWindowTitle("Обновление остатков")
        f = QFormLayout(d)
        val = QDoubleSpinBox(); val.setMaximum(zone.capacity); val.setValue(zone.occupied)
        
        f.addRow(f"Занято (Макс {zone.capacity}):", val)
        btn = QPushButton("Обновить")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(lambda: self.save_update(d, z_id, val.value()))
        f.addRow(btn)
        d.exec()

    def save_update(self, d, z_id, val):
        success, msg = self.controller.update_load(z_id, val)
        if success:
            d.close()
            self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def delete_zone(self):
        row = self.table.currentRow()
        if row >= 0:
            msg = QMessageBox.question(self, "Удаление", "Удалить зону?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if msg == QMessageBox.StandardButton.Yes:
                self.controller.delete(int(self.table.item(row, 0).text()))
                self.load_data()