import sys
from PySide6.QtWidgets import QApplication
from aWidget import AWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AWidget()
    window.showMaximized()
    sys.exit(app.exec())
