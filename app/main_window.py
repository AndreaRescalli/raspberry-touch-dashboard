from PyQt5.QtWidgets import QWidget, QVBoxLayout
from app.widgets.counter_widget import CounterWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raspberry Dashboard")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.addWidget(CounterWidget())
        self.setLayout(layout)