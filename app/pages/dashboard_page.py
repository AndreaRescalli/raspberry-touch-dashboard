from PyQt5.QtWidgets import QWidget, QVBoxLayout
from app.widgets.system_monitor_widget import SystemMonitorWidget

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(SystemMonitorWidget())