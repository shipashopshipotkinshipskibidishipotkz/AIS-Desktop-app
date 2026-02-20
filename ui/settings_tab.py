from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QComboBox, QFormLayout

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        header = QLabel("Настройки системы")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)

        form = QFormLayout()
        
        self.theme_cb = QComboBox()
        self.theme_cb.addItems(["Светлая", "Темная (в разработке)"])
        
        self.notif_chk = QCheckBox("Включить уведомления о новых заказах")
        self.notif_chk.setChecked(True)
        
        self.sound_chk = QCheckBox("Звуковые оповещения")
        
        self.update_chk = QCheckBox("Автоматически проверять обновления")
        self.update_chk.setChecked(True)

        form.addRow("Тема оформления:", self.theme_cb)
        form.addRow("", self.notif_chk)
        form.addRow("", self.sound_chk)
        form.addRow("", self.update_chk)

        layout.addLayout(form)
        layout.addStretch()
        
        btn_save = QPushButton("Сохранить настройки")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedWidth(200)
        layout.addWidget(btn_save)

        self.setLayout(layout)