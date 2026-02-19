from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTabWidget
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

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


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager()

        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Storico")
        title.setStyleSheet("font-size:22px; font-weight:600;")
        header.addWidget(title)
        header.addStretch(1)

        self.range_combo = make_touch_combo(QComboBox())
        self.range_combo.addItems(["5 min", "30 min", "2 ore", "12 ore"])
        header.addWidget(QLabel("Intervallo: "))
        header.addWidget(self.range_combo)

        layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #334155; border-radius: 12px; }
            QTabBar::tab { min-height: 48px; min-width: 140px; font-size: 18px; padding: 8px; }
        """)
        layout.addWidget(self.tabs)

        # ---- Tab Sistema (CPU/RAM + TEMP dual axis) ----
        self.system_plot = pg.PlotWidget()
        self.system_plot.showGrid(x=True, y=True, alpha=0.25)
        self.system_plot.setLabel("left", "CPU/RAM %")
        self.system_plot.setLabel("bottom", "tempo (campioni)")
        self.system_plot.addLegend(offset=(10, 10))

        self.cpu_curve = self.system_plot.plot([], pen=pg.mkPen(width=2), name="CPU %")
        self.ram_curve = self.system_plot.plot([], pen=pg.mkPen(width=2, style=pg.QtCore.Qt.DashLine), name="RAM %")

        self.temp_vb = pg.ViewBox()
        self.system_plot.showAxis("right")
        self.system_plot.setLabel("right", "TEMP °C")
        self.system_plot.scene().addItem(self.temp_vb)
        self.system_plot.getAxis("right").linkToView(self.temp_vb)
        self.temp_vb.setXLink(self.system_plot)

        self.temp_curve = pg.PlotDataItem([], pen=pg.mkPen(width=2), name="TEMP °C")
        self.temp_vb.addItem(self.temp_curve)
        self.system_plot.getViewBox().sigResized.connect(self._update_system_views)

        self.tabs.addTab(self.system_plot, "Sistema")

        # ---- Tab Rete (Download/Upload) ----
        self.net_plot = pg.PlotWidget()
        self.net_plot.showGrid(x=True, y=True, alpha=0.25)
        self.net_plot.setLabel("left", "KB/s")
        self.net_plot.setLabel("bottom", "tempo (campioni)")
        self.net_plot.addLegend(offset=(10, 10))

        self.down_curve = self.net_plot.plot([], pen=pg.mkPen(width=2), name="Download (↓)")
        self.up_curve = self.net_plot.plot([], pen=pg.mkPen(width=2, style=pg.QtCore.Qt.DashLine), name="Upload (↑)")

        self.tabs.addTab(self.net_plot, "Rete")

        self.range_combo.currentIndexChanged.connect(self.refresh)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)  # storico non dipende dal refresh dashboard

        self.refresh()

    def _update_system_views(self):
        self.temp_vb.setGeometry(self.system_plot.getViewBox().sceneBoundingRect())
        self.temp_vb.linkedViewChanged(self.system_plot.getViewBox(), self.temp_vb.XAxis)

    def _rows_for_range(self):
        choice = self.range_combo.currentText()
        if choice == "5 min":
            return 5 * 60
        if choice == "30 min":
            return 30 * 60
        if choice == "2 ore":
            return 2 * 60 * 60
        if choice == "12 ore":
            return 12 * 60 * 60
        return 5 * 60

    def refresh(self):
        n = self._rows_for_range()
        rows = self.db.last_n(n)
        if not rows:
            return

        x = list(range(len(rows)))
        cpu, ram, temp, up, down = [], [], [], [], []

        for r in rows:
            # r: ts,cpu,ram,temp,up_kb,down_kb
            cpu.append(r[1] if r[1] is not None else 0)
            ram.append(r[2] if r[2] is not None else 0)

            t = r[3]
            if t is None or (isinstance(t, (int, float)) and t < 0):
                temp.append(float("nan"))
            else:
                temp.append(t)

            up.append(r[4] if r[4] is not None else 0)
            down.append(r[5] if r[5] is not None else 0)

        # Sistema
        self.cpu_curve.setData(x, cpu)
        self.ram_curve.setData(x, ram)
        self.temp_curve.setData(x, temp)

        self.system_plot.setYRange(0, 100)
        valid_t = [t for t in temp if t == t]
        if valid_t:
            tmin, tmax = min(valid_t), max(valid_t)
            pad = max(2.0, (tmax - tmin) * 0.15)
            self.temp_vb.setYRange(tmin - pad, tmax + pad)
        self._update_system_views()

        # Rete
        self.down_curve.setData(x, down)
        self.up_curve.setData(x, up)

        # range rete “auto” ma con un minimo ragionevole
        vmax = max(down + up) if (down or up) else 10
        self.net_plot.setYRange(0, max(10, vmax * 1.2))