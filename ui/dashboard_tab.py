from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QMargins
from controllers.dashboard_controller import DashboardController

class DashboardTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.controller = DashboardController()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        self.load_data()

    def load_data(self):
        """защита от дублирования графиков и поломок"""
        old_widget = self.scroll.takeWidget()
        if old_widget:
            old_widget.deleteLater()

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.build_ui(layout)
        
        self.scroll.setWidget(content_widget)

    def build_ui(self, layout):
        role_map = {'logist': 'Логист', 'driver': 'Водитель', 'director': 'Руководитель'}
        role_ru = role_map.get(self.user.role, self.user.role)
        
        header = QLabel(f"Главная панель | Добро пожаловать, {self.user.name} ({role_ru})")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        layout.addWidget(header)

        active_o, new_o, done_o, free_vehicles, wh_percent = self.controller.get_stats(self.user.id, self.user.role)

        # --- КАРТОЧКИ KPI ---
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        kpi_layout.addWidget(self.create_kpi_card("Активные заказы", str(active_o), "📦", "#3B82F6"))
        
        if self.user.role != 'driver':
            kpi_layout.addWidget(self.create_kpi_card("Свободный транспорт", f"{free_vehicles} шт", "🚛", "#10B981"))
            
            # Если склад заполнен > 90%, делаем текст красным
            wh_color = "#DC2626" if wh_percent > 90 else "#3B82F6" 
            kpi_layout.addWidget(self.create_kpi_card("Заполненность склада", f"{wh_percent}%", "🏭", wh_color))
        else:
            kpi_layout.addStretch()
            
        layout.addLayout(kpi_layout)

        # --- ГРАФИКИ И СПИСКИ ---
        if self.user.role != 'driver':
            grid = QGridLayout()
            grid.setSpacing(20)

            # Левая колонка
            left_layout = QVBoxLayout()
            left_layout.setSpacing(20)
            left_layout.addWidget(self.create_bar_chart())
            left_layout.addWidget(self.create_events_block())
            
            # Правая колонка
            right_layout = QVBoxLayout()
            right_layout.setSpacing(20)
            right_layout.addWidget(self.create_pie_chart(active_o, new_o, done_o))
            right_layout.addWidget(self.create_log_block())

            grid.addLayout(left_layout, 0, 0)
            grid.addLayout(right_layout, 0, 1)
            layout.addLayout(grid)
        else:
            info_lbl = QLabel("Перейдите в раздел «Маршруты» для просмотра текущих задач.")
            info_lbl.setStyleSheet("color: #64748B; font-size: 16px; margin-top: 40px;")
            info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_lbl)
        
        layout.addStretch()

    # --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

    def create_kpi_card(self, title, value, icon, value_color):
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedHeight(120)
        card.setMinimumWidth(250)
        layout = QVBoxLayout(card)
        
        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        
        val_lbl = QLabel(value)
        val_lbl.setObjectName("CardValue")
        val_lbl.setStyleSheet(f"color: {value_color};") 
        
        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        top_row.addWidget(val_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("CardTitle")
        
        layout.addLayout(top_row)
        layout.addWidget(title_lbl)
        return card

    def create_events_block(self):
        frame = QFrame()
        frame.setObjectName("InfoBlock")
        frame.setMinimumHeight(200)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Важные события")
        header.setObjectName("BlockHeader")
        layout.addWidget(header)
        
        events = self.controller.get_important_events()
        for e in events:
            lbl = QLabel(f"• {e['text']}")
            lbl.setObjectName("EventItem")
            lbl.setWordWrap(True)
            if e['type'] == 'danger':
                lbl.setProperty("danger", True)
            layout.addWidget(lbl)
            
        layout.addStretch()
        return frame

    def create_log_block(self):
        frame = QFrame()
        frame.setObjectName("InfoBlock")
        frame.setMinimumHeight(200)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Журнал операций")
        header.setObjectName("BlockHeader")
        layout.addWidget(header)
        
        logs = self.controller.get_operations_log()
        for log in logs:
            row = QHBoxLayout()
            time_lbl = QLabel(log['time'])
            time_lbl.setStyleSheet("color: #3B82F6; font-weight: bold; background: transparent;")
            time_lbl.setFixedWidth(55)
            
            text_lbl = QLabel(log['text'])
            text_lbl.setObjectName("EventItem")
            text_lbl.setWordWrap(True)
            
            row.addWidget(time_lbl)
            row.addWidget(text_lbl)
            layout.addLayout(row)
            
        layout.addStretch()
        return frame

    def create_pie_chart(self, active_o, new_o, done_o):
        """Создает круговую диаграмму на основе реальных данных из базы"""
        series = QPieSeries()
        
        if active_o > 0: series.append("В пути", active_o).setBrush(QColor("#3B82F6"))   
        if new_o > 0: series.append("Новые", new_o).setBrush(QColor("#10B981"))    
        if done_o > 0: series.append("Доставлено", done_o).setBrush(QColor("#64748B")) 
        
        # Защита от пустой базы:
        if active_o == 0 and new_o == 0 and done_o == 0:
            series.append("Нет данных", 1).setBrush(QColor("#CBD5E1"))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Статусы заказов")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        chart.setBackgroundRoundness(0)
        chart.setMargins(QMargins(0, 0, 0, 0))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet("background: transparent;")

        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(350)
        layout = QVBoxLayout(card)
        layout.addWidget(chart_view)
        return card

    def create_bar_chart(self):
        """Создает гистограмму на основе РЕАЛЬНЫХ расчетов доходов по дням"""
        bar_set = QBarSet("Доходы")
        
        income_data = self.controller.get_income_by_days()
        bar_set.append(income_data)
        bar_set.setColor(QColor("#818CF8")) 

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Прибыль (тыс. руб)")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundRoundness(0)
        chart.setMargins(QMargins(0, 0, 0, 0))

        categories = ["Пн", "Вт", "Ср", "Чт", "Пт"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        
        max_income = max(income_data) if income_data and max(income_data) > 0 else 100
        axis_y.setMax(max_income + (max_income * 0.2))
        
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        chart.legend().setVisible(False)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet("background: transparent;")

        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(350)
        layout = QVBoxLayout(card)
        layout.addWidget(chart_view)
        return card