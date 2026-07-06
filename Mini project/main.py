from PySide6.QtWidgets import QApplication
from ui.menu import MainMenu
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())
