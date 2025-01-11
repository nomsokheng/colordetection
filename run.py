import sys
from PyQt6.QtWidgets import QApplication

from app.color_reader import ColorReader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorReader()
    window.show()
    sys.exit(app.exec())
