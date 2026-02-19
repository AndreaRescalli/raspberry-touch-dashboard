from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class WifiStrengthWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._signal = None  # 0-100 oppure None
        self.setMinimumHeight(18)
        self.setMinimumWidth(120)

    def set_signal(self, signal):
        self._signal = signal
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        bars = 5
        gap = 6
        h = self.height()
        w = self.width()

        bar_w = int((w - gap * (bars - 1)) / bars)
        if bar_w <= 0:
            return

        for i in range(bars):
            x = i * (bar_w + gap)

            # tacche orizzontali (rettangoli)
            if self._signal is None:
                color = QColor(80, 80, 80)
            else:
                threshold = (i + 1) * 20
                color = QColor(34, 197, 94) if self._signal >= threshold else QColor(80, 80, 80)

            p.setBrush(color)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(x, 0, bar_w, h, 4, 4)