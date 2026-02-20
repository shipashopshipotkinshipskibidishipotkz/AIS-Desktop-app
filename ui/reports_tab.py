from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QMessageBox, QFileDialog, QLabel, QGridLayout, QDateEdit, QFrame)
from PyQt6.QtCore import QDate, Qt
from controllers.orders_controller import OrdersController
from controllers.transport_controller import TransportController
from services.pdf_service import PDFService
import os

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

        btn_income = QPushButton("📊 Отчет по доходам (Приложение А)")
        btn_income.setObjectName("PrimaryButton")
        btn_income.setFixedHeight(45)
        btn_income.clicked.connect(lambda: self.gen_report('income'))
        
        btn_delivered = QPushButton("📦 Доставленные грузы (Приложение B)")
        btn_delivered.setObjectName("PrimaryButton")
        btn_delivered.setFixedHeight(45)
        btn_delivered.clicked.connect(lambda: self.gen_report('delivered'))
        
        btn_trans = QPushButton("🚛 Загрузка транспорта (Приложение C)")
        btn_trans.setObjectName("PrimaryButton")
        btn_trans.setFixedHeight(45)
        btn_trans.clicked.connect(lambda: self.gen_report('transport'))

        grid.addWidget(btn_income, 0, 0)
        grid.addWidget(btn_delivered, 0, 1)
        grid.addWidget(btn_trans, 0, 2)
        layout.addLayout(grid)
        layout.addSpacing(30)
        
        info_frame = QFrame()
        info_frame.setObjectName("InfoBlock")
        info_layout = QVBoxLayout(info_frame)
        info_lbl = QLabel(
            "ℹ️ <b>Примечание:</b><br><br>"
            "Глобальные отчеты (Приложения А, B, C) генерируются кнопками выше.<br><br>"
            "Индивидуальные документы:<br>"
            "• <b>Маршрутный лист (Приложение D)</b><br>"
            "• <b>Квитанция (Приложение E)</b><br>"
            "Формируются индивидуально для каждого заказа во вкладке <b>«Заказы»</b> "
            "(кнопка «Действия» -> «Документы»)."
        )
        info_lbl.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.5;")
        info_lbl.setWordWrap(True)
        info_layout.addWidget(info_lbl)
        
        layout.addWidget(info_frame)
        layout.addStretch()
        self.setLayout(layout)

    def gen_report(self, r_type):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", f"report_{r_type}.pdf", "PDF (*.pdf)")
        if not file_path: return

        try:
            pdf = PDFService()
            start_date = self.date_from.date().toPyDate()
            end_date = self.date_to.date().toPyDate()
            
            if r_type == 'income':
                all_orders = OrdersController().get_all()
                filtered_orders = [
                    o for o in all_orders 
                    if o.created_at and start_date <= o.created_at.date() <= end_date
                ]
                pdf.generate_income_report(filtered_orders, file_path)
                
            elif r_type == 'delivered':
                all_orders = OrdersController().get_all()
                filtered_orders = [
                    o for o in all_orders 
                    if o.created_at and start_date <= o.created_at.date() <= end_date and o.status == "Доставлен"
                ]
                pdf.generate_delivered_report(filtered_orders, file_path)
                
            elif r_type == 'transport':
                vehicles = TransportController().get_all()
                pdf.generate_transport_load_report(vehicles, file_path)
            
            QMessageBox.information(self, "Готово", "Отчет успешно сформирован!")
            os.startfile(file_path) 
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета: {str(e)}")