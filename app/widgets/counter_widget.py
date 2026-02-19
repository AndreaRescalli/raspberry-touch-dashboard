from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class CounterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.count = 0

        layout = QVBoxLayout()

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 30px;")

        row = QHBoxLayout()

        self.btn_inc = QPushButton("Incrementa")
        self.btn_inc.clicked.connect(self.increment)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset)

        row.addWidget(self.btn_inc)
        row.addWidget(self.btn_reset)

        layout.addWidget(self.label)
        layout.addLayout(row)

        self.setLayout(layout)
        self.update_label()

    def update_label(self):
        self.label.setText(f"Conteggio: {self.count}")

    def increment(self):
        self.count += 1
        self.update_label()

    def reset(self):
        self.count = 0
        self.update_label()