import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Touch UI")
        # NIENTE FramelessWindowHint -> torna la finestra con la X
        self.showMaximized()

        self.count = 0
        self.init_ui()
        self.update_counter_label()

    def init_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("BUONGIORNO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px;")
        main_layout.addWidget(title)

        self.counter_label = QLabel("")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 40px; font-weight: bold;")
        main_layout.addWidget(self.counter_label)

        row = QHBoxLayout()

        self.inc_btn = QPushButton("Incrementa")
        self.inc_btn.setMinimumHeight(110)
        self.inc_btn.setStyleSheet("font-size: 24px;")
        self.inc_btn.clicked.connect(self.increment)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumHeight(110)
        self.reset_btn.setStyleSheet("font-size: 24px;")
        self.reset_btn.clicked.connect(self.reset)

        row.addWidget(self.inc_btn)
        row.addWidget(self.reset_btn)
        main_layout.addLayout(row)

        self.setLayout(main_layout)

    def update_counter_label(self):
        self.counter_label.setText(f"Conteggio: {self.count}")

    def increment(self):
        self.count += 1
        self.update_counter_label()

    def reset(self):
        self.count = 0
        self.update_counter_label()

    def closeEvent(self, event):
        """Intercetta la chiusura (X / Alt+F4 / close()) e chiede conferma."""
        reply = QMessageBox.question(
            self,
            "Conferma uscita",
            "Sei sicuro di voler uscire?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()