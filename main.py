import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
from app.styles.theme import DARK_QSS

def main():
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()