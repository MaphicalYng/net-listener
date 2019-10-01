# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QMainWindow, QDesktopWidget
from ui.MainWindow import Ui_MainWindow
from tools.localhost_net_info_tool import LocalhostNetInfoTool


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 加载UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 使窗口居中
        self.center()
        self.ui.local_refresh_button.clicked.connect(self.load_local_net_config)
        self.statusBar().showMessage('准备就绪。')

    """
    使窗口居中
    """
    def center(self):
        screen_g = QDesktopWidget().screenGeometry()
        window_g = self.geometry()
        left = int((screen_g.width() - window_g.width()) / 2)
        up = int((screen_g.height() - window_g.height()) / 2)
        self.move(left, up)

    """
    程序被第一次打开，加载本地网络配置
    """
    def load_local_net_config(self):
        self.ui.device_tip_label.clear()
        self.statusBar().clearMessage()
        self.statusBar().showMessage('正在读取网络配置……')
        tool = LocalhostNetInfoTool()
        info = tool.get_info()
        # 解析info数组
        result_string = ''
        for item in info:
            for device_name, detail_list in item.items():
                # 打印设备名称
                result_string += '设备名：' + device_name + '\r\n'
                for detail in detail_list:
                    address = detail['Address']
                    address_family = detail['AddressFamily']
                    netmask = detail['Netmask']
                    if address_family == tool.ipv4:
                        result_string += '\tIPv4：\r\n'
                    if address_family == tool.ipv6:
                        result_string += '\tIPv6：\r\n'
                    if address_family == tool.mac:
                        result_string += '\tMAC：\r\n'
                    if address:
                        result_string += '\t\t地址：' + address + '\r\n'
                    if netmask:
                        result_string += '\t\t子网掩码：' + netmask + '\r\n'
        print(result_string)
        self.ui.device_info_label.setText(result_string)
        self.ui.device_info_label.adjustSize()
        self.ui.scrollAreaWidgetContents.setMinimumHeight(self.ui.device_info_label.geometry().height())
        self.statusBar().showMessage('网络配置读取完成。')
