import psutil
import pyqtgraph as pg

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt


class SystemMonitorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.cpu_series = []
        self.net_sent_prev = None
        self.net_recv_prev = None

        self._build_ui()
        self._start_timer()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Riga valori
        top = QHBoxLayout()
        self.cpu_label = QLabel("CPU: -- %")
        self.ram_label = QLabel("RAM: -- %")
        self.net_label = QLabel("NET: -- ↑ / -- ↓")

        for lab in (self.cpu_label, self.ram_label, self.net_label):
            lab.setStyleSheet("font-size: 18px;")
        self.net_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        top.addWidget(self.cpu_label)
        top.addWidget(self.ram_label)
        top.addStretch(1)
        top.addWidget(self.net_label)
        layout.addLayout(top)

        # Grafico CPU
        self.graph = pg.PlotWidget()
        self.graph.setYRange(0, 100)
        self.graph.showGrid(x=True, y=True, alpha=0.3)
        self.graph.setLabel("left", "CPU %")
        self.graph.setLabel("bottom", "tempo")
        self.curve = self.graph.plot([])

        layout.addWidget(self.graph)
        self.setLayout(layout)

    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        self.cpu_label.setText(f"CPU: {cpu:.0f} %")
        self.ram_label.setText(f"RAM: {ram:.0f} %")

        # Serie CPU (ultimi 60 punti)
        self.cpu_series.append(cpu)
        if len(self.cpu_series) > 60:
            self.cpu_series.pop(0)
        self.curve.setData(self.cpu_series)

        # Rete (bytes/sec -> KB/sec)
        net = psutil.net_io_counters()
        if self.net_sent_prev is None:
            self.net_sent_prev = net.bytes_sent
            self.net_recv_prev = net.bytes_recv
            self.net_label.setText("NET: 0 KB/s ↑ / 0 KB/s ↓")
            return

        up_bps = net.bytes_sent - self.net_sent_prev
        down_bps = net.bytes_recv - self.net_recv_prev
        self.net_sent_prev = net.bytes_sent
        self.net_recv_prev = net.bytes_recv

        up_kb = up_bps / 1024.0
        down_kb = down_bps / 1024.0
        self.net_label.setText(f"NET: {up_kb:.0f} KB/s ↑ / {down_kb:.0f} KB/s ↓")