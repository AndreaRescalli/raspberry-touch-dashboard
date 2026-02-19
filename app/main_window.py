from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget,
    QMessageBox, QLabel, QFrame, QStyle
)
from PyQt5.QtCore import Qt, QSize

from app.pages.dashboard_page import DashboardPage
from app.pages.history_page import HistoryPage
from app.pages.settings_page import SettingsPage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raspberry Industrial Dashboard")
        self.showMaximized()
        self._build_ui()

    def _btn(self, text, std_icon):
        b = QPushButton(text)
        b.setMinimumHeight(56)
        b.setStyleSheet("font-size:18px; text-align:left; padding-left:12px;")
        b.setIcon(self.style().standardIcon(std_icon))
        b.setIconSize(QSize(22, 22))
        return b

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # Sidebar
        sidebar = QFrame()
        sidebar.setStyleSheet("QFrame{background:#0b1220; border:1px solid #334155; border-radius:14px;}")
        s = QVBoxLayout(sidebar)
        s.setContentsMargins(12, 12, 12, 12)
        s.setSpacing(10)

        title = QLabel("MENU")
        title.setStyleSheet("font-size:14px; letter-spacing:2px; color:#94a3b8;")
        s.addWidget(title)

        self.btn_dash = self._btn("Dashboard", QStyle.SP_ComputerIcon)
        self.btn_hist = self._btn("Storico", QStyle.SP_FileDialogDetailedView)
        self.btn_sett = self._btn("Settings", QStyle.SP_FileDialogContentsView)
        self.btn_exit = self._btn("Esci", QStyle.SP_DialogCloseButton)

        s.addWidget(self.btn_dash)
        s.addWidget(self.btn_hist)
        s.addWidget(self.btn_sett)
        s.addStretch(1)
        s.addWidget(self.btn_exit)

        # Pages
        self.stack = QStackedWidget()
        self.page_dash = DashboardPage()
        self.page_hist = HistoryPage()
        self.page_sett = SettingsPage()

        self.stack.addWidget(self.page_dash)
        self.stack.addWidget(self.page_hist)
        self.stack.addWidget(self.page_sett)

        root.addWidget(sidebar, 1)
        root.addWidget(self.stack, 5)

        self.btn_dash.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_dash))
        self.btn_hist.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_hist))
        self.btn_sett.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_sett))
        self.btn_exit.clicked.connect(self.close)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Conferma uscita", "Sei sicuro di voler uscire?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        event.accept() if reply == QMessageBox.Yes else event.ignore()