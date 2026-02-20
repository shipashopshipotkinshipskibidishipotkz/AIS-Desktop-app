from fpdf import FPDF
from datetime import datetime
import os

class PDFService(FPDF):
    def __init__(self):
        super().__init__()
        font_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        times_path = os.path.join(font_dir, 'times.ttf')
        times_bd_path = os.path.join(font_dir, 'timesbd.ttf')
        
        if os.path.exists(times_path):
            self.add_font('TimesNewRoman', '', times_path, uni=True)
            self.add_font('TimesNewRoman', 'B', times_bd_path, uni=True)
            self.set_font("TimesNewRoman", size=14)
        else:
            self.add_font('Arial', '', os.path.join(font_dir, 'arial.ttf'), uni=True)
            self.add_font('Arial', 'B', os.path.join(font_dir, 'arialbd.ttf'), uni=True)
            self.set_font("Arial", size=14)

    def draw_header_and_title(self, title):
        self.add_page()
        self.set_font("TimesNewRoman", size=14)
        self.cell(0, 8, "ООО «ЛогистТранс».", ln=True, align="L")
        date_str = datetime.now().strftime('%d.%m.%Y')
        self.cell(0, 8, f"{date_str} Тепловодская Вероника Антоновна", ln=True, align="L")
        self.ln(10)
        
        self.set_font("TimesNewRoman", 'B', 14)
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(5)

    def draw_signatures(self):
        self.ln(15)
        self.set_font("TimesNewRoman", size=14)
        self.cell(0, 8, "Подтверждено Генеральным директором", ln=True, align="R")
        self.cell(0, 8, "Тепловодская.В.А____________________________", ln=True, align="R")
        self.cell(0, 8, f"«____» ____________ 2026 года", ln=True, align="R")

    # --- Приложение А: Доходы за период ---
    def generate_income_report(self, orders, filepath, date_start=None, date_end=None):
        self.draw_header_and_title("Отчёт «Доходы за период»")

        self.set_font("TimesNewRoman", size=12)
        w = [30, 30, 50, 45, 35]
        self.cell(w[0], 8, "Номер заказа", "LTR", 0, 'C')
        self.cell(w[1], 8, "Дата", "LTR", 0, 'C')
        self.cell(w[2], 8, "Название", "LTR", 0, 'C')
        self.cell(w[3], 8, "Маршрут", "LTR", 0, 'C')
        self.cell(w[4], 8, "Стоимость", "LTR", 1, 'C')
        
        self.cell(w[0], 8, "", "LBR", 0, 'C')
        self.cell(w[1], 8, "выполнения", "LBR", 0, 'C')
        self.cell(w[2], 8, "компании-клиента", "LBR", 0, 'C')
        self.cell(w[3], 8, "", "LBR", 0, 'C')
        self.cell(w[4], 8, "услуги", "LBR", 1, 'C')

        total = 0
        for o in orders:
            self.cell(w[0], 10, f"А{o.id:05d}", 1, 0, 'C')
            
            date_val = o.created_at.strftime('%d.%m.%Y') if o.created_at else "-"
            self.cell(w[1], 10, date_val, 1, 0, 'C')
            
            client_name = o.client.name if o.client else "-"
            if len(client_name) > 25: client_name = client_name[:22] + "..."
            self.cell(w[2], 10, client_name, 1, 0, 'C')
            
            route = f"{o.route_start}-{o.route_end}" if o.route_start else "-"
            if len(route) > 22: route = route[:19] + "..."
            self.cell(w[3], 10, route, 1, 0, 'C')
            
            self.cell(w[4], 10, f"{int(o.cost or 0)}", 1, 1, 'C')
            total += (o.cost or 0)

        self.ln(10)
        self.set_font("TimesNewRoman", size=14)
        total_str = f"{int(total):,}".replace(',', ' ')
        self.cell(0, 10, f"ОБЩАЯ СУММА: {total_str} руб.", ln=True, align="R")
        self.draw_signatures()
        self.output(filepath)

    # --- Приложение B: Количество доставленных грузов ---
    def generate_delivered_report(self, orders, filepath):
        self.draw_header_and_title("Отчёт «Количество доставленных грузов»")

        total_weight = sum(o.weight for o in orders if o.weight)
        total_vol = sum(o.volume for o in orders if o.volume)

        self.set_font("TimesNewRoman", size=14)
        self.cell(0, 8, f"Выполнено заказов: {len(orders)}", ln=True)
        self.cell(0, 8, f"Общий вес: {total_weight} кг", ln=True)
        self.cell(0, 8, f"Общий объём: {total_vol} м3", ln=True)
        self.ln(5)

        self.set_font("TimesNewRoman", size=12)
        w = [30, 50, 30, 30, 50]
        
        self.cell(w[0], 10, "Номер заказа", 1, 0, 'C')
        self.cell(w[1], 10, "Тип груза", 1, 0, 'C')
        self.cell(w[2], 10, "Вес груза", 1, 0, 'C')
        self.cell(w[3], 10, "Объём груза", 1, 0, 'C')
        self.cell(w[4], 10, "Статус заказа", 1, 1, 'C')

        for o in orders:
             self.cell(w[0], 10, f"А{o.id:05d}", 1, 0, 'C')
             desc = o.description[:25] if o.description else "-"
             self.cell(w[1], 10, desc, 1, 0, 'C')
             self.cell(w[2], 10, f"{o.weight or 0} кг", 1, 0, 'C')
             self.cell(w[3], 10, f"{o.volume or 0} м3", 1, 0, 'C')
             self.cell(w[4], 10, o.status, 1, 1, 'C')
        
        self.draw_signatures()
        self.output(filepath)

    # --- Приложение C: Загрузка транспорта ---
    def generate_transport_load_report(self, vehicles, filepath):
        self.draw_header_and_title("Отчёт «Загрузка транспорта»")
        
        self.set_font("TimesNewRoman", size=11)
        w = [35, 40, 30, 25, 30, 30]
        
        self.cell(w[0], 6, "Номер машины", "LTR", 0, 'C')
        self.cell(w[1], 6, "ФИО", "LTR", 0, 'C')
        self.cell(w[2], 6, "Текущее", "LTR", 0, 'C')
        self.cell(w[3], 6, "Количество", "LTR", 0, 'C')
        self.cell(w[4], 6, "Общий пробег", "LTR", 0, 'C')
        self.cell(w[5], 6, "Процент", "LTR", 1, 'C')
        
        self.cell(w[0], 6, "и модель", "LBR", 0, 'C')
        self.cell(w[1], 6, "водителя", "LBR", 0, 'C')
        self.cell(w[2], 6, "состояние", "LBR", 0, 'C')
        self.cell(w[3], 6, "рейсов", "LBR", 0, 'C')
        self.cell(w[4], 6, "за период", "LBR", 0, 'C')
        self.cell(w[5], 6, "загрузки", "LBR", 1, 'C')

        for v in vehicles:
            self.cell(w[0], 10, f"{v.plate_number}", 1, 0, 'C')
            
            d_name = "Нет"
            if v.driver:
                surname = v.driver.surname or ""
                name_chr = v.driver.name[0] + "." if v.driver.name else ""
                d_name = f"{surname} {name_chr}".strip()
                
            self.cell(w[1], 10, d_name, 1, 0, 'C')
            self.cell(w[2], 10, v.status, 1, 0, 'C')
            
            # РЕАЛЬНЫЕ ДАННЫЕ ИЗ БАЗЫ: считаем привязанные к машине заказы
            real_trips = len(v.orders) if hasattr(v, 'orders') else 0
            self.cell(w[3], 10, str(real_trips), 1, 0, 'C')
            
            # Динамический расчет пробега (в среднем 600км на 1 заказ)
            mileage = real_trips * 600
            self.cell(w[4], 10, f"{mileage:,} км".replace(',', ' '), 1, 0, 'C')
            
            perc = "100%" if v.status != "Свободен" else "0%"
            self.cell(w[5], 10, perc, 1, 1, 'C')

        self.draw_signatures()
        self.output(filepath)

    # --- Приложение D: Маршрутный лист ---
    def generate_waybill(self, order, filepath):
        self.add_page()
        self.set_font("TimesNewRoman", 'B', 14)
        self.cell(0, 10, f"Отчёт «Маршрутный лист» - Документация для водителя", ln=True, align="C")
        self.ln(5)
        
        self.set_font("TimesNewRoman", size=14)
        v_info = f"{order.vehicle.model} (госномер {order.vehicle.plate_number})" if order.vehicle else "Не назначен"
        d_info = f"{order.vehicle.driver.surname} {order.vehicle.driver.name}" if (order.vehicle and order.vehicle.driver) else "-"

        self.cell(0, 8, f"Транспорт: {v_info}", ln=True)
        self.cell(0, 8, f"Водитель: {d_info}", ln=True)
        self.ln(5)

        self.set_font("TimesNewRoman", size=12)
        w = [35, 45, 40, 40, 30]
        
        self.cell(w[0], 10, "Этап маршрута", 1, 0, 'C')
        self.cell(w[1], 10, "Адрес", 1, 0, 'C')
        self.cell(w[2], 10, "Контактное лицо", 1, 0, 'C')
        self.cell(w[3], 10, "Груз и условия", 1, 0, 'C')
        self.cell(w[4], 10, "Подпись", 1, 1, 'C')
        
        self.cell(w[0], 15, "Отправка(склад)", 1, 0, 'C')
        self.cell(w[1], 15, order.route_start or "Склад", 1, 0, 'C')
        self.cell(w[2], 15, "Диспетчер склада", 1, 0, 'C')
        self.cell(w[3], 15, f"{order.weight or 0} кг", 1, 0, 'C')
        self.cell(w[4], 15, "________", 1, 1, 'C')

        self.cell(w[0], 15, "Доставка(клиент)", 1, 0, 'C')
        addr = order.client.address if order.client else order.route_end
        if addr and len(addr) > 20: addr = addr[:18]+"..."
        self.cell(w[1], 15, addr or "-", 1, 0, 'C')
        
        contact = order.client.name if order.client else "Клиент"
        if len(contact) > 18: contact = contact[:15]+"..."
        self.cell(w[2], 15, contact, 1, 0, 'C')
        
        desc = order.description if order.description else "Груз"
        if len(desc) > 15: desc = desc[:12]+"..."
        self.cell(w[3], 15, desc, 1, 0, 'C')
        self.cell(w[4], 15, "________", 1, 1, 'C')

        self.draw_signatures()
        self.output(filepath)

    # --- Приложение E: Квитанция ---
    def generate_receipt(self, order, filepath):
        self.add_page()
        self.set_font("TimesNewRoman", size=14)
        self.cell(0, 8, "ООО «ЛогистТранс».", ln=True, align="L")
        date_str = datetime.now().strftime('%d.%m.%Y')
        self.cell(0, 8, f"{date_str} Тепловодская Вероника Антоновна", ln=True, align="L")
        self.ln(10)
        
        self.set_font("TimesNewRoman", 'B', 14)
        self.cell(0, 8, f"Отчёт «Квитанция для клиента»", ln=True, align="C")
        self.cell(0, 8, f"КВИТАНЦИЯ К ЗАКАЗУ № {order.id}", ln=True, align="C")
        self.ln(5)
        
        self.set_font("TimesNewRoman", size=14)
        self.cell(0, 8, f"Исполнитель: ООО «ЛогистТранс», ИНН 7700123456, г. Москва, ул. Промышленная 10.", ln=True)
        client_name = order.client.name if order.client else "Частное лицо"
        self.cell(0, 8, f"Заказчик: {client_name}", ln=True)
        self.ln(5)
        
        self.cell(0, 8, f"Описание услуги:", ln=True)
        desc = order.description if order.description else "Транспортная перевозка груза."
        self.cell(0, 8, f"Груз: {desc}", ln=True)
        self.cell(0, 8, f"Маршрут: {order.route_start} — {order.route_end}", ln=True)
        self.ln(5)
        
        self.cell(0, 8, f"Финансовый блок:", ln=True)
        cost_str = f"{int(order.cost or 0):,}".replace(',', ' ')
        self.cell(0, 8, f"Стоимость услуги: {cost_str} руб.", ln=True)
        self.ln(10)
        
        self.cell(0, 8, "Подтверждение:", ln=True)
        self.cell(0, 8, "Груз принят в полном объеме, претензий к качеству перевозки не имею.", ln=True)
        self.cell(0, 8, "Подписи сторон:", ln=True)
        self.cell(0, 8, "От перевозчика: _________ / Иванов И.И. /", ln=True)
        self.cell(0, 8, "От клиента:       _________ / Смирнов А.П. /", ln=True)
        
        self.draw_signatures()
        self.output(filepath)