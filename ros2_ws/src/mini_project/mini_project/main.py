from PySide6.QtWidgets import QApplication
from mini_project.ui.menu import MainMenu
import sys
def main(args=None):
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
