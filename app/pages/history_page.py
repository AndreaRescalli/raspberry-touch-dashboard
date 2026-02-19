from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from app.database.db_manager import DBManager


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager()

        layout = QVBoxLayout(self)

        title = QLabel("Storico (ultimi minuti)")
        title.setStyleSheet("font-size:22px; font-weight:600;")
        layout.addWidget(title)

        self.graph = pg.PlotWidget()
        self.graph.showGrid(x=True, y=True, alpha=0.25)
        self.graph.setLabel("left", "Valore")
        self.cpu_curve = self.graph.plot([], pen=pg.mkPen(width=2), name="CPU")
        self.ram_curve = self.graph.plot([], pen=pg.mkPen(width=2, style=pg.QtCore.Qt.DashLine), name="RAM")

        layout.addWidget(self.graph)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)

        self.refresh()

    def refresh(self):
        rows = self.db.last_n(300)  # ~5 min a 1Hz
        if not rows:
            return
        # ts,cpu,ram,temp,up,down
        cpu = [r[1] for r in rows]
        ram = [r[2] for r in rows]
        x = list(range(len(rows)))

        self.cpu_curve.setData(x, cpu)
        self.ram_curve.setData(x, ram)
        self.graph.setYRange(0, 100)