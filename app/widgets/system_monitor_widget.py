import psutil
import pyqtgraph as pg
import subprocess

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
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
        layout = QVBoxLayout(self)

        # Barra stato compatta (una riga)
        self.status_label = QLabel("Loading...")
        self.status_label.setStyleSheet("font-size:14px; color:#cbd5e1;")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setTextFormat(Qt.RichText)  # per colorare solo la temp
        layout.addWidget(self.status_label)

        # Grafico CPU
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
            if "cpu_thermal" in temps and temps["cpu_thermal"]:
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

    def temp_color(self, temp_c):
        if temp_c is None:
            return "#cbd5e1"  # default
        if temp_c < 55:
            return "#22c55e"  # green
        if temp_c < 70:
            return "#f59e0b"  # orange
        return "#ef4444"      # red

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        temp = self.get_cpu_temperature()

        # Grafico CPU
        self.cpu_series.append(cpu)
        if len(self.cpu_series) > 60:
            self.cpu_series.pop(0)
        self.curve.setData(self.cpu_series)

        # Rete (se WiFi -> mostra WiFi%, se Ethernet -> ETH: IP)
        device, dev_type = self.get_active_network()

        if dev_type == "wifi":
            sig = self.get_wifi_signal_percent()
            net_info = f"WiFi: {sig}%" if sig is not None else "WiFi"
        elif dev_type == "ethernet":
            ip = self.get_ipv4(device) if device else self.get_ipv4("eth0")
            net_info = f"ETH: {ip}" if ip else "ETH"
        else:
            net_info = "Offline"

        # Velocità rete (totale)
        net = psutil.net_io_counters()
        if self.net_sent_prev is None:
            self.net_sent_prev = net.bytes_sent
            self.net_recv_prev = net.bytes_recv
            return

        up_kb = (net.bytes_sent - self.net_sent_prev) / 1024.0
        down_kb = (net.bytes_recv - self.net_recv_prev) / 1024.0
        self.net_sent_prev = net.bytes_sent
        self.net_recv_prev = net.bytes_recv

        # Temperatura con colore
        if temp is None:
            temp_txt = "TEMP: N/A"
        else:
            temp_txt = f"TEMP: {temp:.1f}°C"
        tcol = self.temp_color(temp)

        # Barra compatta (HTML per colorare solo la temp)
        status_html = (
            f"CPU {cpu:.0f}%  |  RAM {ram:.0f}%  |  "
            f"<span style='color:{tcol}; font-weight:600;'>{temp_txt}</span>  |  "
            f"{net_info}  |  "
            f"{down_kb:.0f} KB/s ↓  {up_kb:.0f} KB/s ↑"
        )
        self.status_label.setText(status_html)