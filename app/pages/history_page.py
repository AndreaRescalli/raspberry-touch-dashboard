from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from app.database.db_manager import DBManager


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

        self.range_combo = QComboBox()
        self.range_combo.addItems(["5 min", "30 min", "2 ore", "12 ore"])
        self.range_combo.setMinimumHeight(40)
        self.range_combo.setStyleSheet("font-size:16px;")
        header.addWidget(QLabel("Intervallo: "))
        header.addWidget(self.range_combo)

        layout.addLayout(header)

        # Grafico principale (CPU/RAM)
        self.plot = pg.PlotWidget()
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setLabel("left", "CPU/RAM %")
        self.plot.setLabel("bottom", "tempo (campioni)")
        self.plot.addLegend(offset=(10, 10))
        layout.addWidget(self.plot)

        # Curve CPU/RAM (asse sinistro)
        self.cpu_curve = self.plot.plot([], pen=pg.mkPen(width=2), name="CPU %")
        self.ram_curve = self.plot.plot([], pen=pg.mkPen(width=2, style=pg.QtCore.Qt.DashLine), name="RAM %")

        # ---- Asse destro + ViewBox per TEMP ----
        self.temp_vb = pg.ViewBox()
        self.plot.showAxis("right")
        self.plot.setLabel("right", "TEMP °C")
        self.plot.scene().addItem(self.temp_vb)
        self.plot.getAxis("right").linkToView(self.temp_vb)
        self.temp_vb.setXLink(self.plot)

        # Curve TEMP sul ViewBox destro
        self.temp_curve = pg.PlotDataItem([], pen=pg.mkPen(width=2), name="TEMP °C")
        self.temp_vb.addItem(self.temp_curve)

        # Aggiorna geometria viewbox quando cambia dimensione
        self.plot.getViewBox().sigResized.connect(self._update_views)

        self.range_combo.currentIndexChanged.connect(self.refresh)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)

        self.refresh()

    def _update_views(self):
        self.temp_vb.setGeometry(self.plot.getViewBox().sceneBoundingRect())
        self.temp_vb.linkedViewChanged(self.plot.getViewBox(), self.temp_vb.XAxis)

    def _rows_for_range(self):
        # DB ~ 1 Hz => N righe ~ secondi
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
        cpu = []
        ram = []
        temp = []

        for r in rows:
            # r: ts,cpu,ram,temp,up_kb,down_kb
            cpu.append(r[1] if r[1] is not None else 0)
            ram.append(r[2] if r[2] is not None else 0)

            t = r[3]
            # gestisce anche eventuali vecchi -1
            if t is None or (isinstance(t, (int, float)) and t < 0):
                temp.append(float("nan"))
            else:
                temp.append(t)

        self.cpu_curve.setData(x, cpu)
        self.ram_curve.setData(x, ram)
        self.temp_curve.setData(x, temp)

        # Range sinistro (CPU/RAM)
        self.plot.setYRange(0, 100)

        # Range destro (TEMP) calcolato su valori validi
        valid_t = [t for t in temp if t == t]  # NaN check
        if valid_t:
            tmin = min(valid_t)
            tmax = max(valid_t)
            pad = max(2.0, (tmax - tmin) * 0.15)
            self.temp_vb.setYRange(tmin - pad, tmax + pad)

        self._update_views()