from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QLineEdit, QComboBox, QDialog, QFormLayout, 
                             QDoubleSpinBox, QMessageBox, QLabel, QFrame, QMenu)
from PyQt6.QtCore import Qt
from controllers.orders_controller import OrdersController
import os

class OrdersTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.controller = OrdersController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header = QLabel("Реестр заказов")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        layout.addWidget(header)

        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Номер заказа, клиент, пункт...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.load_data)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все статусы", "Новый", "В пути", "Доставлен", "Отменен"])
        self.status_filter.setFixedWidth(150)
        self.status_filter.currentTextChanged.connect(self.load_data)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Клиент", "Маршрут", "Транспорт", "Статус", "Стоимость", "Действия"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(45) 
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Создать заказ")
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self.open_add_dialog)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setObjectName("SecondaryButton")
        self.btn_refresh.clicked.connect(self.load_data)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        if self.user.role == 'driver':
            self.btn_add.hide()
        elif self.user.role == 'director':
            self.btn_add.hide()

        self.setLayout(layout)
        self.load_data()

    def create_status_badge(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setObjectName("StatusBadge")
        
        status_map = {
            "Новый": "New",
            "В пути": "Work",
            "Доставлен": "Done",
            "Отменен": "Error"
        }
        lbl.setProperty("status", status_map.get(text, "New")) 
        
        widget = QWidget()
        l = QHBoxLayout(widget)
        l.setContentsMargins(10, 2, 10, 2)
        l.addWidget(lbl)
        return widget

    def load_data(self):
        orders = self.controller.get_all()
        search_txt = self.search_input.text().lower()
        status_flt = self.status_filter.currentText()
        
        filtered = []
        for o in orders:
            if self.user.role == 'driver':
                if not o.vehicle or o.vehicle.driver_id != self.user.id:
                    continue
            
            full_text = f"{o.id} {o.client.name if o.client else ''} {o.description}".lower()
            if search_txt and search_txt not in full_text:
                continue

            if status_flt != "Все статусы" and o.status != status_flt:
                continue
                
            filtered.append(o)

        self.table.setRowCount(len(filtered))
        for i, o in enumerate(filtered):
            id_item = QTableWidgetItem(f"#{o.id}")
            id_item.setForeground(Qt.GlobalColor.blue)
            self.table.setItem(i, 0, id_item)
            
            self.table.setItem(i, 1, QTableWidgetItem(o.client.name if o.client else "-"))
            route = f"{o.route_start} → {o.route_end}" if o.route_start else "-"
            self.table.setItem(i, 2, QTableWidgetItem(route))
            
            veh = f"{o.vehicle.model}" if o.vehicle else "Не назначен"
            self.table.setItem(i, 3, QTableWidgetItem(veh))
            
            self.table.setCellWidget(i, 4, self.create_status_badge(o.status))
            
            self.table.setItem(i, 5, QTableWidgetItem(f"{o.cost or 0:,.0f} ₽"))
            
            btn_action = QPushButton("Действия")
            btn_action.setObjectName("SecondaryButton")
            btn_action.clicked.connect(lambda _, row=i, oid=o.id: self.show_context_menu(row, oid))
            
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0,0,0,0)
            l.addWidget(btn_action)
            self.table.setCellWidget(i, 6, w)

    def show_context_menu(self, row, order_id):
        menu = QMenu()
        act_edit = menu.addAction("✏ Редактировать")
        act_docs = menu.addMenu("📄 Документы")
        act_waybill = act_docs.addAction("Маршрутный лист (Driver)")
        act_receipt = act_docs.addAction("Квитанция (Client)")
        
        if self.user.role == 'logist':
            menu.addSeparator()
            act_del = menu.addAction("🗑 Удалить")
        
        action = menu.exec(self.cursor().pos())
        
        if action == act_edit:
            self.open_edit_dialog(order_id)
        elif action == act_waybill:
            self.generate_doc(order_id, 'waybill')
        elif action == act_receipt:
            self.generate_doc(order_id, 'receipt')
        elif self.user.role == 'logist' and action == act_del:
            self.delete_order(order_id)

    def generate_doc(self, order_id, doc_type):
        order = next((o for o in self.controller.get_all() if o.id == order_id), None)
        if not order: return
        
        filename = f"{doc_type}_{order.id}.pdf"
        try:
            from services.pdf_service import PDFService
            pdf = PDFService()
            
            if doc_type == 'waybill':
                pdf.generate_waybill(order, filename)
            elif doc_type == 'receipt':
                pdf.generate_receipt(order, filename)
                
            QMessageBox.information(self, "Готово", f"Документ успешно сохранен!")
            os.startfile(filename) 
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

    def open_add_dialog(self):
        self.open_edit_dialog(None)

    def open_edit_dialog(self, order_id=None):
        d = QDialog(self)
        d.setWindowTitle("Карточка заказа")
        d.setMinimumWidth(450)
        layout = QFormLayout(d)
        
        order = None
        if order_id:
            order = next((o for o in self.controller.get_all() if o.id == order_id), None)

        cmb_zone = QComboBox()
        zones = self.controller.get_warehouse_zones()
        
        if not order:
            for z in zones:
                cmb_zone.addItem(f"{z.name} ({z.cargo_type}) | Доступно: {z.occupied} кг", z.id)
        else:
            current_z_name = order.warehouse_zone.name if order.warehouse_zone else "Удалена"
            cmb_zone.addItem(f"{current_z_name} (Зафиксировано)", order.warehouse_zone_id)
            cmb_zone.setDisabled(True)

        inp_start = QLineEdit(order.route_start if order else "")
        inp_end = QLineEdit(order.route_end if order else "")
        
        inp_weight = QDoubleSpinBox(); inp_weight.setMaximum(100000) 
        if order: 
            inp_weight.setValue(order.weight or 0)
            inp_weight.setDisabled(True) 
        
        inp_volume = QDoubleSpinBox(); inp_volume.setMaximum(10000)
        if order: inp_volume.setValue(order.volume or 0)
            
        inp_cost = QDoubleSpinBox(); inp_cost.setMaximum(10000000)
        if order: 
            inp_cost.setValue(order.cost or 0)
        else:
            inp_cost.setDisabled(True) 
            inp_cost.setSpecialValueText("Авторасчет")
        
        lbl_dist = QLabel(f"{order.distance} км" if order else "Авторасчет")
        
        cmb_client = QComboBox()
        for c in self.controller.get_clients():
            cmb_client.addItem(c.name, c.id)
        if order and order.client_id:
            idx = cmb_client.findData(order.client_id)
            cmb_client.setCurrentIndex(idx)

        cmb_status = QComboBox()
        cmb_status.addItems(["Новый", "В пути", "Доставлен", "Отменен"])
        if order: cmb_status.setCurrentText(order.status)

        cmb_vehicle = QComboBox()
        cmb_vehicle.addItem("Автоподбор", -1)
        for v in self.controller.get_vehicles():
            cmb_vehicle.addItem(f"{v.plate_number} ({v.model})", v.id)
        if order and order.vehicle_id:
            idx = cmb_vehicle.findData(order.vehicle_id)
            cmb_vehicle.setCurrentIndex(idx)

        if self.user.role == 'driver':
            cmb_zone.setDisabled(True)
            inp_start.setDisabled(True)
            inp_end.setDisabled(True)
            inp_weight.setDisabled(True)
            inp_volume.setDisabled(True)
            inp_cost.setDisabled(True)
            cmb_client.setDisabled(True)
            cmb_vehicle.setDisabled(True)

        layout.addRow("Груз со склада:", cmb_zone)
        layout.addRow("Вес (кг):", inp_weight)
        layout.addRow("Объем (м3):", inp_volume)
        layout.addRow("Клиент:", cmb_client)
        layout.addRow("Откуда:", inp_start)
        layout.addRow("Куда:", inp_end)
        layout.addRow("Расстояние:", lbl_dist)
        layout.addRow("Стоимость:", inp_cost)
        layout.addRow("Транспорт:", cmb_vehicle)
        layout.addRow("Статус:", cmb_status)
        
        btn_save = QPushButton("Сохранить")
        btn_save.setObjectName("PrimaryButton")
        
        btn_save.clicked.connect(lambda: self.save_order(d, order_id, {
            "zone_id": cmb_zone.currentData(), 
            "cost": inp_cost.value(),
            "client_id": cmb_client.currentData(),
            "status": cmb_status.currentText(),
            "vehicle_id": cmb_vehicle.currentData(),
            "start": inp_start.text(),
            "end": inp_end.text(),
            "weight": inp_weight.value(),
            "volume": inp_volume.value()
        }))
        layout.addRow(btn_save)
        d.exec()

    def save_order(self, d, oid, data):
        if not oid:
            success, msg = self.controller.add(
                data['zone_id'], data['client_id'], 
                data['weight'], data['volume'], data['start'], data['end'], data['vehicle_id']
            )
            if success:
                QMessageBox.information(self, "Успех", msg)
                d.close()
            else:
                QMessageBox.warning(self, "Ошибка склада", msg)
        else:
            success, msg = self.controller.update(
                oid, data['cost'], data['status'], data['vehicle_id'],
                data['start'], data['end']
            )
            if success: d.close()
            
        self.load_data()

    def delete_order(self, order_id):
        order = next((o for o in self.controller.get_all() if o.id == order_id), None)
        if not order: 
            return
        if order.status in ["В пути", "Новый"]:
            QMessageBox.warning(self, "Блокировка удаления", "Нельзя удалить активный заказ!")
            return

        reply = QMessageBox.question(self, "Удаление", f"Вы уверены, что хотите удалить заказ #{order.id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                     
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete(order_id)
            self.load_data()