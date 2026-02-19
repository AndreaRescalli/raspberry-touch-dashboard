from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from app.database.db_manager import DBManager
from app.widgets.touch_picker import TouchPicker


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self._range = "5 min"

        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Storico")
        title.setStyleSheet("font-size:22px; font-weight:600;")
        header.addWidget(title)
        header.addStretch(1)

        self.range_btn = QPushButton(f"Intervallo: {self._range}")
        self.range_btn.setMinimumHeight(50)
        self.range_btn.setStyleSheet("font-size:18px;")
        self.range_btn.clicked.connect(self.pick_range)

        header.addWidget(self.range_btn)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                min-height: 50px;
                min-width: 140px;
                font-size: 18px;
            }
        """)
        layout.addWidget(self.tabs)

        # ---- SISTEMA TAB ----
        self.system_plot = pg.PlotWidget()
        self.system_plot.showGrid(x=True, y=True, alpha=0.25)
        self.system_plot.setLabel("left", "CPU/RAM %")
        self.system_plot.setLabel("bottom", "tempo")
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

        # ---- RETE TAB ----
        self.net_plot = pg.PlotWidget()
        self.net_plot.showGrid(x=True, y=True, alpha=0.25)
        self.net_plot.setLabel("left", "KB/s")
        self.net_plot.setLabel("bottom", "tempo")
        self.net_plot.addLegend(offset=(10, 10))

        self.down_curve = self.net_plot.plot([], pen=pg.mkPen(width=2), name="Download ↓")
        self.up_curve = self.net_plot.plot([], pen=pg.mkPen(width=2, style=pg.QtCore.Qt.DashLine), name="Upload ↑")

        self.tabs.addTab(self.net_plot, "Rete")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)

        self.refresh()

    def pick_range(self):
        dlg = TouchPicker(
            "Seleziona intervallo",
            ["5 min", "30 min", "2 ore", "12 ore"],
            self
        )
        if dlg.exec_() and dlg.choice:
            self._range = dlg.choice
            self.range_btn.setText(f"Intervallo: {self._range}")
            self.refresh()

    def _rows_for_range(self):
        mapping = {
            "5 min": 300,
            "30 min": 1800,
            "2 ore": 7200,
            "12 ore": 43200
        }
        return mapping.get(self._range, 300)

    def _update_system_views(self):
        self.temp_vb.setGeometry(self.system_plot.getViewBox().sceneBoundingRect())
        self.temp_vb.linkedViewChanged(self.system_plot.getViewBox(), self.temp_vb.XAxis)

    def refresh(self):
        n = self._rows_for_range()
        rows = self.db.last_n(n)
        if not rows:
            return

        x = list(range(len(rows)))
        cpu, ram, temp, up, down = [], [], [], [], []

        for r in rows:
            cpu.append(r[1] or 0)
            ram.append(r[2] or 0)

            t = r[3]
            if t is None or (isinstance(t, (int, float)) and t < 0):
                temp.append(float("nan"))
            else:
                temp.append(t)

            up.append(r[4] or 0)
            down.append(r[5] or 0)

        self.cpu_curve.setData(x, cpu)
        self.ram_curve.setData(x, ram)
        self.temp_curve.setData(x, temp)

        self.system_plot.setYRange(0, 100)

        valid_t = [t for t in temp if t == t]
        if valid_t:
            tmin, tmax = min(valid_t), max(valid_t)
            pad = max(2.0, (tmax - tmin) * 0.15)
            self.temp_vb.setYRange(tmin - pad, tmax + pad)

        self.down_curve.setData(x, down)
        self.up_curve.setData(x, up)

        vmax = max(down + up) if (down or up) else 10
        self.net_plot.setYRange(0, max(10, vmax * 1.2))