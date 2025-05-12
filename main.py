from gui.main_gui import MainWindow
from PySide6.QtWidgets import QApplication
import sys

def start_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start_app()