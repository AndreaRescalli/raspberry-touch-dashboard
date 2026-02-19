from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt

from app.widgets.system_monitor_widget import SystemMonitorWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Raspberry Dashboard")
        # Vuoi la X classica: usa showMaximized (fullscreen spesso nasconde la X)
        self.showMaximized()

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout()

        header = QLabel("Raspberry Dashboard")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; font-weight: 600;")
        root.addWidget(header)

        root.addWidget(SystemMonitorWidget())

        # barra in basso
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        exit_btn = QPushButton("Esci")
        exit_btn.setMinimumHeight(70)
        exit_btn.setStyleSheet("font-size: 20px;")
        exit_btn.clicked.connect(self.close)  # triggera closeEvent -> safe quit
        bottom.addWidget(exit_btn)

        root.addLayout(bottom)
        self.setLayout(root)

    def closeEvent(self, event):
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