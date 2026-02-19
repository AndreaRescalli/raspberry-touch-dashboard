import psutil
import pyqtgraph as pg
import subprocess

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt

from app.widgets.wifi_strength_widget import WifiStrengthWidget
from app.database.db_manager import DBManager


class SystemMonitorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.cpu_series = []
        self.net_sent_prev = None
        self.net_recv_prev = None

        self._build_ui()
        self._start_timer()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()

        self.cpu_label = QLabel("CPU: --%")
        self.ram_label = QLabel("RAM: --%")
        self.temp_label = QLabel("TEMP: --°C")

        self.net_kind_label = QLabel("NET:")
        self.net_kind_label.setStyleSheet("font-size:16px; color:#94a3b8;")

        self.wifi_bars = WifiStrengthWidget()
        self.net_detail_label = QLabel("")  # es: Ethernet: 192.168.50.2 o "WiFi"
        self.net_detail_label.setStyleSheet("font-size:16px;")

        self.net_speed_label = QLabel("0 KB/s ↑ / 0 KB/s ↓")
        self.net_speed_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for lab in (self.cpu_label, self.ram_label, self.temp_label, self.net_speed_label):
            lab.setStyleSheet("font-size: 16px;")

        top.addWidget(self.cpu_label)
        top.addWidget(self.ram_label)
        top.addWidget(self.temp_label)
        top.addSpacing(10)
        top.addWidget(self.net_kind_label)
        top.addWidget(self.wifi_bars)
        top.addWidget(self.net_detail_label)
        top.addStretch(1)
        top.addWidget(self.net_speed_label)

        layout.addLayout(top)

        self.graph = pg.PlotWidget()
        self.graph.setYRange(0, 100)
        self.graph.showGrid(x=True, y=True, alpha=0.25)
        self.graph.setLabel("left", "CPU %")
        self.curve = self.graph.plot([], pen=pg.mkPen(width=2))
        layout.addWidget(self.graph)

    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def get_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            if "cpu_thermal" in temps:
                return temps["cpu_thermal"][0].current
        except Exception:
            pass
        return None

    def get_active_network(self):
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
                stderr=subprocess.DEVNULL,
            ).decode()
            for line in out.splitlines():
                device, dev_type, state = line.split(":")
                if state == "connected":
                    return device, dev_type
        except Exception:
            pass
        return None, None

    def get_wifi_signal_percent(self):
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "IN-USE,SIGNAL", "dev", "wifi"],
                stderr=subprocess.DEVNULL,
            ).decode()
            for line in out.splitlines():
                if line.startswith("*:"):
                    return int(line.split(":")[1])
        except Exception:
            pass
        return None

    def get_ipv4(self, iface):
        addrs = psutil.net_if_addrs().get(iface, [])
        for a in addrs:
            if a.family == 2:  # AF_INET
                return a.address
        return ""

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        temp = self.get_cpu_temperature()

        self.cpu_label.setText(f"CPU: {cpu:.0f}%")
        self.ram_label.setText(f"RAM: {ram:.0f}%")

        if temp is not None:
            self.temp_label.setText(f"TEMP: {temp:.1f}°C")
            if temp < 55:
                self.temp_label.setStyleSheet("font-size:16px; color:#22c55e;")
            elif temp < 70:
                self.temp_label.setStyleSheet("font-size:16px; color:#f59e0b;")
            else:
                self.temp_label.setStyleSheet("font-size:16px; color:#ef4444;")
        else:
            self.temp_label.setText("TEMP: N/A")

        self.cpu_series.append(cpu)
        if len(self.cpu_series) > 60:
            self.cpu_series.pop(0)
        self.curve.setData(self.cpu_series)

        device, dev_type = self.get_active_network()

        if dev_type == "wifi":
            sig = self.get_wifi_signal_percent()
            self.wifi_bars.set_signal(sig)
            self.net_detail_label.setText("WiFi")
        elif dev_type == "ethernet":
            self.wifi_bars.set_signal(None)
            ip = self.get_ipv4(device) if device else self.get_ipv4("eth0")
            self.net_detail_label.setText(f"Ethernet: {ip}")
        else:
            self.wifi_bars.set_signal(None)
            self.net_detail_label.setText("disconnesso")

        # Velocità rete totale (tutte le interfacce)
        net = psutil.net_io_counters()
        if self.net_sent_prev is None:
            self.net_sent_prev = net.bytes_sent
            self.net_recv_prev = net.bytes_recv
            self.net_speed_label.setText("0 KB/s ↑ / 0 KB/s ↓")
            return

        up_bps = net.bytes_sent - self.net_sent_prev
        down_bps = net.bytes_recv - self.net_recv_prev
        self.net_sent_prev = net.bytes_sent
        self.net_recv_prev = net.bytes_recv

        up_kb = up_bps / 1024.0
        down_kb = down_bps / 1024.0
        self.net_speed_label.setText(f"{up_kb:.0f} KB/s ↑ / {down_kb:.0f} KB/s ↓")

        # salva su SQLite
        self.db.insert(cpu=cpu, ram=ram, temp=(temp if temp is not None else -1), up_kb=up_kb, down_kb=down_kb)