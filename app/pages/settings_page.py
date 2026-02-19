from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Settings (arrivano tra poco): sampling, export CSV, kiosk, ecc.")
        label.setStyleSheet("font-size:20px;")
        layout.addWidget(label)
        layout.addStretch(1)