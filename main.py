import sys
import os

os.environ['LC_ALL'] = 'en_US.UTF-8' 

from PyQt6.QtWidgets import QApplication
from database.connection import init_db
from ui.login_window import LoginWindow

if __name__ == "__main__":

    print("Инициализация базы данных...")
    init_db()
    
    app = QApplication(sys.argv)
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec())