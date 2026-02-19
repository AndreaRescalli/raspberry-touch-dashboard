from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt


class TouchPicker(QDialog):
    def __init__(self, title: str, options: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._choice = None

        self.setStyleSheet("""
            QDialog { background-color: #0f172a; }
            QLabel { color: white; }
            QPushButton {
                background-color: #1e293b;
                color: white;
                border-radius: 10px;
            }
            QPushButton:pressed {
                background-color: #334155;
            }
        """)

        layout = QVBoxLayout(self)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size:22px; font-weight:600;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        for opt in options:
            b = QPushButton(opt)
            b.setMinimumHeight(70)
            b.setStyleSheet("font-size:22px;")
            b.clicked.connect(lambda _, o=opt: self._select(o))
            layout.addWidget(b)

        cancel = QPushButton("Annulla")
        cancel.setMinimumHeight(60)
        cancel.setStyleSheet("font-size:20px;")
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

    def _select(self, opt: str):
        self._choice = opt
        self.accept()

    @property
    def choice(self):
        return self._choice