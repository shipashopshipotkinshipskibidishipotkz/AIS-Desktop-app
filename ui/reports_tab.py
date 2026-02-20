from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QMessageBox, QFileDialog, 
                             QLabel, QGridLayout, QDateEdit, QFrame, QDialog, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from controllers.orders_controller import OrdersController
from controllers.transport_controller import TransportController
from services.pdf_service import PDFService
import os
import csv  # ИМПОРТ ДЛЯ EXCEL

class PreviewDialog(QDialog):
    def __init__(self, parent, r_type, title, data):
        super().__init__(parent)
        self.r_type = r_type
        self.title = title
        self.data = data
        
        self.setWindowTitle("Предпросмотр отчета")
        self.resize(1000, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(f"📄 Предпросмотр: {self.title}")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout.addWidget(lbl_title)
        
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #F8FAFC;")
        layout.addWidget(self.table)
        
        self.fill_table()
        
        # Кнопки (с CSV экспортом)
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setObjectName("SecondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        btn_csv = QPushButton("💾 Выгрузить в Excel (CSV)")
        btn_csv.setObjectName("SecondaryButton")
        btn_csv.clicked.connect(self.export_csv)
        
        btn_print = QPushButton("🖨 Сохранить и Печать (PDF)")
        btn_print.setObjectName("PrimaryButton")
        btn_print.setFixedWidth(250)
        btn_print.clicked.connect(self.generate_pdf)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_csv)
        btn_layout.addWidget(btn_print)
        layout.addLayout(btn_layout)

    def fill_table(self):
        if self.r_type == 'income':
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Номер", "Дата", "Клиент", "Маршрут", "Стоимость"])
            self.table.setRowCount(len(self.data))
            total = 0
            
            for i, o in enumerate(self.data):
                self.table.setItem(i, 0, QTableWidgetItem(f"А{o.id:05d}"))
                date_val = o.created_at.strftime('%d.%m.%Y') if o.created_at else "-"
                self.table.setItem(i, 1, QTableWidgetItem(date_val))
                self.table.setItem(i, 2, QTableWidgetItem(o.client.name if o.client else "-"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{o.route_start}-{o.route_end}"))
                cost = o.cost or 0
                self.table.setItem(i, 4, QTableWidgetItem(f"{int(cost)}"))
                total += cost
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            item_total = QTableWidgetItem(f"ИТОГО: {int(total)} руб.")
            item_total.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.table.setItem(row, 4, item_total)

        elif self.r_type == 'delivered':
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Номер", "Тип груза", "Вес (кг)", "Объем (м3)", "Статус"])
            self.table.setRowCount(len(self.data))
            for i, o in enumerate(self.data):
                self.table.setItem(i, 0, QTableWidgetItem(f"А{o.id:05d}"))
                self.table.setItem(i, 1, QTableWidgetItem(o.description or "-"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{o.weight or 0}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{o.volume or 0}"))
                self.table.setItem(i, 4, QTableWidgetItem(o.status))

        elif self.r_type == 'transport':
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(["Номер машины", "Водитель", "Состояние", "Рейсов", "Пробег (км)", "Загрузка"])
            self.table.setRowCount(len(self.data))
            for i, v in enumerate(self.data):
                self.table.setItem(i, 0, QTableWidgetItem(v.plate_number))
                d_name = "Нет"
                if v.driver:
                    d_name = f"{v.driver.surname} {v.driver.name[0]}." if v.driver.name else v.driver.surname
                self.table.setItem(i, 1, QTableWidgetItem(d_name))
                self.table.setItem(i, 2, QTableWidgetItem(v.status))
                real_trips = len(v.orders) if hasattr(v, 'orders') else 0
                self.table.setItem(i, 3, QTableWidgetItem(str(real_trips)))
                self.table.setItem(i, 4, QTableWidgetItem(f"{real_trips * 600}"))
                self.table.setItem(i, 5, QTableWidgetItem("100%" if v.status != "Свободен" else "0%"))

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить Excel", f"report_{self.r_type}.csv", "CSV Files (*.csv)")
        if not file_path: return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)
                
                for row in range(self.table.rowCount()):
                    row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(self.table.columnCount())]
                    writer.writerow(row_data)
                    
            QMessageBox.information(self, "Успех", "Отчет успешно сохранен в формате Excel (CSV)!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def generate_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", f"report_{self.r_type}.pdf", "PDF (*.pdf)")
        if not file_path: return
        try:
            pdf = PDFService()
            if self.r_type == 'income': pdf.generate_income_report(self.data, file_path)
            elif self.r_type == 'delivered': pdf.generate_delivered_report(self.data, file_path)
            elif self.r_type == 'transport': pdf.generate_transport_load_report(self.data, file_path)
            
            QMessageBox.information(self, "Готово", "Отчет сохранен (PDF)!")
            os.startfile(file_path) 
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации PDF: {str(e)}")

class ReportsTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        title = QLabel("Аналитика и отчетность")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #1E293B;")
        layout.addWidget(title)

        if self.user.role not in ['director', 'logist']:
            error_lbl = QLabel("У вас нет прав для просмотра этого раздела.")
            error_lbl.setStyleSheet("color: #DC2626; font-size: 16px;")
            layout.addWidget(error_lbl)
            layout.addStretch()
            self.setLayout(layout)
            return

        date_layout = QGridLayout()
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        
        date_layout.addWidget(QLabel("Период с:"), 0, 0)
        date_layout.addWidget(self.date_from, 0, 1)
        date_layout.addWidget(QLabel("по:"), 0, 2)
        date_layout.addWidget(self.date_to, 0, 3)
        layout.addLayout(date_layout)
        layout.addSpacing(20)

        grid = QGridLayout()
        grid.setSpacing(15)

        btn_income = QPushButton("📊 Доходы (Приложение А)")
        btn_income.setObjectName("PrimaryButton")
        btn_income.setFixedHeight(45)
        btn_income.clicked.connect(lambda: self.show_preview('income', "Доходы за период"))
        
        btn_delivered = QPushButton("📦 Доставленные (Приложение B)")
        btn_delivered.setObjectName("PrimaryButton")
        btn_delivered.setFixedHeight(45)
        btn_delivered.clicked.connect(lambda: self.show_preview('delivered', "Доставленные грузы"))
        
        btn_trans = QPushButton("🚛 Транспорт (Приложение C)")
        btn_trans.setObjectName("PrimaryButton")
        btn_trans.setFixedHeight(45)
        btn_trans.clicked.connect(lambda: self.show_preview('transport', "Загрузка транспорта"))

        grid.addWidget(btn_income, 0, 0)
        grid.addWidget(btn_delivered, 0, 1)
        grid.addWidget(btn_trans, 0, 2)
        layout.addLayout(grid)
        layout.addSpacing(30)
        
        info_frame = QFrame()
        info_frame.setObjectName("InfoBlock")
        info_layout = QVBoxLayout(info_frame)
        info_lbl = QLabel("ℹ️ <b>Индивидуальные документы:</b><br>• Маршрутный лист<br>• Квитанция<br>Формируются индивидуально для каждого заказа во вкладке <b>«Заказы»</b>.")
        info_lbl.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.5;")
        info_layout.addWidget(info_lbl)
        
        layout.addWidget(info_frame)
        layout.addStretch()
        self.setLayout(layout)

    def show_preview(self, r_type, title):
        start_date = self.date_from.date().toPyDate()
        end_date = self.date_to.date().toPyDate()
        data = []
        if r_type == 'income':
            data = [o for o in OrdersController().get_all() if o.created_at and start_date <= o.created_at.date() <= end_date]
        elif r_type == 'delivered':
            data = [o for o in OrdersController().get_all() if o.created_at and start_date <= o.created_at.date() <= end_date and o.status == "Доставлен"]
        elif r_type == 'transport':
            data = TransportController().get_all()

        dialog = PreviewDialog(self, r_type, title, data)
        dialog.exec()