# -*- coding: utf-8 -*-
"""
主窗口实现
"""
from PySide2.QtWidgets import QMainWindow, QDesktopWidget, QMessageBox
from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QStandardItemModel
from ui.MainWindow import Ui_MainWindow
from tools.localhost_net_info_tool import LocalhostNetInfoTool
from tools.net_sniffer_tool import NetSnifferTool
from tools.port_scanning_tool import PortScanningTool
from tools.other_tool_function_set import OtherToolFunctionSet


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 声明嗅探工具对象
        self._sniffer_tool = None

        # 初始化嗅探IP表格数据源
        self._table_model = QStandardItemModel()

        # 声明嗅探列表刷新线程
        self._table_refresh_thread = None

        # 加载UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 使窗口居中
        self.center()

        # 连接信号和槽
        self.ui.action_about.triggered.connect(self.about)
        self.ui.local_refresh_button.clicked.connect(self.load_local_net_config)
        self.ui.sniffer_start_button.clicked.connect(self.start_sniffer_thread)
        self.ui.sniffer_stop_button.clicked.connect(self.stop_sniffer_thread)
        self.ui.scan_start_button.clicked.connect(self.scan_port_of_ip)

        # 初始化控件状态
        self.ui.sniffer_stop_button.setEnabled(False)

        # 初始化完成
        self.statusBar().showMessage('准备就绪。')

    def center(self):
        """
        使窗口居中
        """
        screen_g = QDesktopWidget().screenGeometry()
        window_g = self.geometry()
        left = int((screen_g.width() - window_g.width()) / 2)
        up = int((screen_g.height() - window_g.height()) / 2)
        self.move(left, up)

    def about(self):
        """
        显示软件关于信息
        """
        QMessageBox.information(self, '关于Net Listener', '本软件用来进行网络嗅探、端口扫描，\
以发现局域网中的主机或任何主机的端口开放情况，使用全部功能需要使用ROOT权限运行', QMessageBox.Yes, QMessageBox.Yes)

    def load_local_net_config(self):
        """
        程序被第一次打开，加载本地网络配置
        """
        self.ui.device_tip_label.setHidden(True)
        self.statusBar().clearMessage()
        self.statusBar().showMessage('正在读取网络配置……')
        tool = LocalhostNetInfoTool()
        running_card = tool.get_running_card_name()
        info = tool.get_info()
        addresses = OtherToolFunctionSet.get_localhost_gateway_mac()

        # 解析info数组
        result_string = ''
        result_string += '当前接通的网卡为：\r\n\t' + running_card + '\r\n'
        result_string += '\r\n网关IP地址：\r\n\t' + addresses[2] + '\r\n'
        result_string += '\r\n网关MAC地址：\r\n\t' + addresses[1] + '\r\n'
        for item in info:
            for device_name, detail_list in item.items():
                # 打印设备名称
                result_string += '\r\n设备名：' + device_name + '\r\n'
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

    def start_sniffer_thread(self):
        """
        开启嗅探线程
        """
        # 测试当前是否是root用户
        if not OtherToolFunctionSet.test_root_permission():
            user_input = QMessageBox.information(self, '需要ROOT权限', '请以ROOT权限重启程序以运行嗅探功能。',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if user_input == QMessageBox.Yes:
                # 退出应用程序
                QCoreApplication.instance().quit()
            else:
                return

        # 开启网卡混杂模式
        if_turn_promisc_on = QMessageBox.question(self, '需要开启网卡混杂模式', '嗅探功能需要开启网卡混杂模式，是否开启？',
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if if_turn_promisc_on == QMessageBox.Yes:
            if OtherToolFunctionSet.turn_net_card_promisc(True):
                QMessageBox.information(self, '开启结果', '开启混杂模式成功。', QMessageBox.Yes, QMessageBox.Yes)
            else:
                QMessageBox.information(self, '开启结果', '开启混杂模式失败。', QMessageBox.Yes, QMessageBox.Yes)
                return
        else:
            self.statusBar().showMessage('停止嗅探，需要开启网卡混杂模式。')
            return

        self.ui.sniffer_tip_label.setHidden(True)
        self.statusBar().showMessage("正在嗅探……")

        # 设置表格数据源
        self._table_model.clear()
        self.ui.sniffer_table.setModel(self._table_model)
        self._table_model.setHorizontalHeaderLabels(['IP', 'MAC'])
        self._table_model.setColumnCount(2)

        # 开启嗅探线程
        self._sniffer_tool = NetSnifferTool()
        self._sniffer_tool.start_sniffer_thread(self._table_model, self.ui.sniffer_table)

        # 修改控件状态
        self.ui.sniffer_stop_button.setEnabled(True)
        self.ui.sniffer_start_button.setEnabled(False)

    def stop_sniffer_thread(self):
        """
        关闭嗅探线程
        """
        self.statusBar().showMessage('正在停止……')

        # 关闭嗅探线程
        if self._sniffer_tool is not None:
            self._sniffer_tool.stop_sniffer_thread()

        # 修改控件状态
        self.ui.sniffer_start_button.setEnabled(True)
        self.ui.sniffer_stop_button.setEnabled(False)

        # 关闭网卡混杂模式
        OtherToolFunctionSet.turn_net_card_promisc(False)
        self.statusBar().showMessage('已停止。网卡混杂模式已关闭。')

    def scan_port_of_ip(self):
        """
        扫描给定IP的给定端口
        """
        target_ip = self.ui.scan_target_ip_edit.text()
        target_port_start = self.ui.scan_start_port_edit.text()
        target_port_stop = self.ui.scan_stop_port_edit.text()
        scan_timeout = self.ui.scan_timeout_edit.text()

        scan_tool = PortScanningTool(target_ip, target_port_start, target_port_stop, scan_timeout, self.statusBar())

        # 启动扫描线程
        print('启动端口扫描')
        scan_tool.scan()
