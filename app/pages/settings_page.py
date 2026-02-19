from pathlib import Path
import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
    QPushButton, QMessageBox, QCheckBox
)
from PyQt5.QtCore import pyqtSignal

from app.settings_store import load_settings, save_settings
from app.database.db_manager import DBManager


def make_touch_combo(combo: QComboBox):
    combo.setMinimumHeight(48)
    combo.setStyleSheet("""
        QComboBox { font-size: 18px; padding: 6px 12px; }
        QComboBox::drop-down { width: 48px; }
        QAbstractItemView::item { min-height: 52px; font-size: 18px; }
    """)
    combo.setMaxVisibleItems(6)
    return combo


class SettingsPage(QWidget):
    settings_applied = pyqtSignal(dict)

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

        # Refresh dashboard
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Refresh dashboard:"))
        self.refresh_combo = make_touch_combo(QComboBox())
        self.refresh_combo.addItems(["1s", "2s", "5s"])
        row1.addWidget(self.refresh_combo)
        row1.addStretch(1)
        layout.addLayout(row1)

        # Fullscreen toggle
        row_fs = QHBoxLayout()
        self.fullscreen_chk = QCheckBox("Fullscreen (kiosk)")
        self.fullscreen_chk.setStyleSheet("font-size:18px;")
        row_fs.addWidget(self.fullscreen_chk)
        row_fs.addStretch(1)
        layout.addLayout(row_fs)

        # Retention
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Retention DB (giorni):"))
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 365)
        self.retention_spin.setMinimumHeight(48)
        self.retention_spin.setStyleSheet("font-size:18px;")
        row2.addWidget(self.retention_spin)
        row2.addStretch(1)
        layout.addLayout(row2)

        # Export CSV
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Export CSV:"))
        self.export_combo = make_touch_combo(QComboBox())
        self.export_combo.addItems(["5 min", "30 min", "2 ore", "12 ore"])
        self.btn_export = QPushButton("Esporta")
        self.btn_export.setMinimumHeight(48)
        self.btn_export.setStyleSheet("font-size:18px;")
        row3.addWidget(self.export_combo)
        row3.addWidget(self.btn_export)
        row3.addStretch(1)
        layout.addLayout(row3)

        # Save/apply
        row4 = QHBoxLayout()
        self.btn_save = QPushButton("Salva e Applica")
        self.btn_save.setMinimumHeight(56)
        self.btn_save.setStyleSheet("font-size:18px;")
        row4.addStretch(1)
        row4.addWidget(self.btn_save)
        layout.addLayout(row4)

        layout.addStretch(1)

        self._load_into_controls()

        self.btn_save.clicked.connect(self.save_and_apply)
        self.btn_export.clicked.connect(self.export_csv)

    def _load_into_controls(self):
        refresh_ms = int(self.settings.get("dashboard_refresh_ms", 1000))
        if refresh_ms <= 1000:
            self.refresh_combo.setCurrentText("1s")
        elif refresh_ms <= 2000:
            self.refresh_combo.setCurrentText("2s")
        else:
            self.refresh_combo.setCurrentText("5s")

        self.fullscreen_chk.setChecked(bool(self.settings.get("fullscreen", True)))
        self.retention_spin.setValue(int(self.settings.get("retention_days", 7)))

    def save_and_apply(self):
        refresh_map = {"1s": 1000, "2s": 2000, "5s": 5000}
        refresh_ms = refresh_map[self.refresh_combo.currentText()]

        self.settings["dashboard_refresh_ms"] = refresh_ms
        self.settings["fullscreen"] = bool(self.fullscreen_chk.isChecked())
        self.settings["retention_days"] = int(self.retention_spin.value())

        save_settings(self.settings)
        self.settings_applied.emit(self.settings)

        QMessageBox.information(self, "OK", "Impostazioni salvate e applicate.")

    def export_csv(self):
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