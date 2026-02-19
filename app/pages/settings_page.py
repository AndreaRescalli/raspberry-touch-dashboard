from pathlib import Path
import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import pyqtSignal

from app.settings_store import load_settings, save_settings
from app.database.db_manager import DBManager


class SettingsPage(QWidget):
    settings_applied = pyqtSignal(dict)  # notifichiamo MainWindow/monitor

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.settings = load_settings()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Settings")
        title.setStyleSheet("font-size:22px; font-weight:600;")
        layout.addWidget(title)

        # Sampling
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Sampling:"))
        self.sampling_combo = QComboBox()
        self.sampling_combo.addItems(["1s", "2s", "5s"])
        self.sampling_combo.setMinimumHeight(40)
        self.sampling_combo.setStyleSheet("font-size:16px;")
        row1.addWidget(self.sampling_combo)
        row1.addStretch(1)
        layout.addLayout(row1)

        # Retention
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Retention DB (giorni):"))
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 365)
        self.retention_spin.setMinimumHeight(40)
        self.retention_spin.setStyleSheet("font-size:16px;")
        row2.addWidget(self.retention_spin)
        row2.addStretch(1)
        layout.addLayout(row2)

        # Export CSV
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Export CSV:"))
        self.export_combo = QComboBox()
        self.export_combo.addItems(["5 min", "30 min", "2 ore", "12 ore"])
        self.export_combo.setMinimumHeight(40)
        self.export_combo.setStyleSheet("font-size:16px;")
        self.btn_export = QPushButton("Esporta")
        self.btn_export.setMinimumHeight(44)
        self.btn_export.setStyleSheet("font-size:16px;")
        row3.addWidget(self.export_combo)
        row3.addWidget(self.btn_export)
        row3.addStretch(1)
        layout.addLayout(row3)

        # Save/apply
        row4 = QHBoxLayout()
        self.btn_save = QPushButton("Salva e Applica")
        self.btn_save.setMinimumHeight(54)
        self.btn_save.setStyleSheet("font-size:18px;")
        row4.addStretch(1)
        row4.addWidget(self.btn_save)
        layout.addLayout(row4)

        layout.addStretch(1)

        # init values
        self._load_into_controls()

        # signals
        self.btn_save.clicked.connect(self.save_and_apply)
        self.btn_export.clicked.connect(self.export_csv)

    def _load_into_controls(self):
        sampling_ms = int(self.settings.get("sampling_ms", 1000))
        if sampling_ms <= 1000:
            self.sampling_combo.setCurrentText("1s")
        elif sampling_ms <= 2000:
            self.sampling_combo.setCurrentText("2s")
        else:
            self.sampling_combo.setCurrentText("5s")

        self.retention_spin.setValue(int(self.settings.get("retention_days", 7)))

    def save_and_apply(self):
        sampling_map = {"1s": 1000, "2s": 2000, "5s": 5000}
        sampling_ms = sampling_map[self.sampling_combo.currentText()]

        self.settings["sampling_ms"] = sampling_ms
        self.settings["retention_days"] = int(self.retention_spin.value())

        save_settings(self.settings)
        self.settings_applied.emit(self.settings)

        QMessageBox.information(self, "OK", "Impostazioni salvate e applicate.")

    def export_csv(self):
        # righe ~ 1Hz; se sampling cambia, l’export è “a campioni”
        choice = self.export_combo.currentText()
        sec_map = {"5 min": 300, "30 min": 1800, "2 ore": 7200, "12 ore": 43200}
        n = sec_map.get(choice, 300)

        rows = self.db.last_n(n)
        if not rows:
            QMessageBox.warning(self, "Vuoto", "Nessun dato nel database.")
            return

        exports_dir = Path.home() / "touchui" / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)

        fname = exports_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with fname.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ts", "cpu", "ram", "temp", "up_kb", "down_kb"])
            for r in rows:
                w.writerow(r)

        QMessageBox.information(self, "Export completato", f"Creato:\n{fname}")