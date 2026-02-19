from pathlib import Path
import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QCheckBox, QSpinBox
)
from PyQt5.QtCore import pyqtSignal

from app.settings_store import load_settings, save_settings
from app.database.db_manager import DBManager
from app.widgets.touch_picker import TouchPicker


class SettingsPage(QWidget):
    settings_applied = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.settings = load_settings()
        self._refresh = "1s"
        self._export_range = "5 min"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Settings")
        title.setStyleSheet("font-size:22px; font-weight:600;")
        layout.addWidget(title)

        # Refresh dashboard
        row1 = QHBoxLayout()
        self.refresh_btn = QPushButton(f"Refresh dashboard: {self._refresh}")
        self.refresh_btn.setMinimumHeight(60)
        self.refresh_btn.setStyleSheet("font-size:20px;")
        self.refresh_btn.clicked.connect(self.pick_refresh)
        row1.addWidget(self.refresh_btn)
        row1.addStretch(1)
        layout.addLayout(row1)

        # Fullscreen
        row2 = QHBoxLayout()
        self.fullscreen_chk = QCheckBox("Fullscreen (kiosk)")
        self.fullscreen_chk.setStyleSheet("font-size:20px;")
        row2.addWidget(self.fullscreen_chk)
        row2.addStretch(1)
        layout.addLayout(row2)

        # Retention
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Retention DB (giorni):"))
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 365)
        self.retention_spin.setMinimumHeight(50)
        self.retention_spin.setStyleSheet("font-size:18px;")
        row3.addWidget(self.retention_spin)
        row3.addStretch(1)
        layout.addLayout(row3)

        # Export
        row4 = QHBoxLayout()
        self.export_btn = QPushButton(f"Export CSV: {self._export_range}")
        self.export_btn.setMinimumHeight(60)
        self.export_btn.setStyleSheet("font-size:20px;")
        self.export_btn.clicked.connect(self.pick_export)
        self.btn_export = QPushButton("Esporta")
        self.btn_export.setMinimumHeight(60)
        self.btn_export.setStyleSheet("font-size:20px;")
        self.btn_export.clicked.connect(self.export_csv)
        row4.addWidget(self.export_btn)
        row4.addWidget(self.btn_export)
        row4.addStretch(1)
        layout.addLayout(row4)

        # Save
        self.btn_save = QPushButton("Salva e Applica")
        self.btn_save.setMinimumHeight(70)
        self.btn_save.setStyleSheet("font-size:22px;")
        self.btn_save.clicked.connect(self.save_and_apply)
        layout.addWidget(self.btn_save)

        layout.addStretch(1)

        self._load_settings()

    def _load_settings(self):
        refresh_ms = self.settings.get("dashboard_refresh_ms", 1000)
        if refresh_ms <= 1000:
            self._refresh = "1s"
        elif refresh_ms <= 2000:
            self._refresh = "2s"
        else:
            self._refresh = "5s"

        self.refresh_btn.setText(f"Refresh dashboard: {self._refresh}")
        self.fullscreen_chk.setChecked(self.settings.get("fullscreen", True))
        self.retention_spin.setValue(self.settings.get("retention_days", 7))

    def pick_refresh(self):
        dlg = TouchPicker("Refresh dashboard", ["1s", "2s", "5s"], self)
        if dlg.exec_() and dlg.choice:
            self._refresh = dlg.choice
            self.refresh_btn.setText(f"Refresh dashboard: {self._refresh}")

    def pick_export(self):
        dlg = TouchPicker("Export intervallo", ["5 min", "30 min", "2 ore", "12 ore"], self)
        if dlg.exec_() and dlg.choice:
            self._export_range = dlg.choice
            self.export_btn.setText(f"Export CSV: {self._export_range}")

    def save_and_apply(self):
        refresh_map = {"1s": 1000, "2s": 2000, "5s": 5000}

        self.settings["dashboard_refresh_ms"] = refresh_map[self._refresh]
        self.settings["fullscreen"] = self.fullscreen_chk.isChecked()
        self.settings["retention_days"] = self.retention_spin.value()

        save_settings(self.settings)
        self.settings_applied.emit(self.settings)

        QMessageBox.information(self, "OK", "Impostazioni salvate e applicate.")

    def export_csv(self):
        sec_map = {"5 min": 300, "30 min": 1800, "2 ore": 7200, "12 ore": 43200}
        n = sec_map.get(self._export_range, 300)

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