# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QMainWindow, QDesktopWidget
from ui.MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 加载UI
        ui = Ui_MainWindow()
        ui.setupUi(self)

        # 使窗口居中
        self.center()

    def center(self):
        screen_g = QDesktopWidget().screenGeometry()
        window_g = self.geometry()
        left = int((screen_g.width() - window_g.width()) / 2)
        up = int((screen_g.height() - window_g.height()) / 2)
        self.move(left, up)
