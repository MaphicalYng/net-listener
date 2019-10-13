# -*- coding: utf-8 -*-
"""
主窗口实现
"""
from PySide2.QtWidgets import QMainWindow, QDesktopWidget, QMessageBox
from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QStandardItemModel, QCloseEvent
from ui.MainWindow import Ui_MainWindow
from tools.localhost_net_info_tool import LocalhostNetInfoTool
from tools.net_sniffer_tool import NetSnifferTool
from tools.port_scanning_tool import PortScanningTool
from tools.other_tool_function_set import OtherToolFunctionSet


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 声明工具对象
        self._sniffer_tool = None
        self._scan_tool = None

        # 初始化嗅探IP表格数据源
        self._table_model = QStandardItemModel()
        self._scan_table_model = QStandardItemModel()

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
        self.ui.scan_start_button.clicked.connect(self.start_scan_thread)
        self.ui.scan_stop_button.clicked.connect(self.stop_scan_thread)

        # 初始化控件状态
        self.ui.sniffer_stop_button.setEnabled(False)
        self.ui.scan_stop_button.setEnabled(False)

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
        self.ui.local_refresh_button.setEnabled(False)
        self.statusBar().clearMessage()
        self.statusBar().showMessage('正在读取网络配置……')
        tool = LocalhostNetInfoTool()
        tool.start_local_info_thread(self.ui.device_info_label, self.ui.scroll_area_widget_contents,
                                     self.statusBar(), self.ui.local_refresh_button)

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
            if not OtherToolFunctionSet.turn_net_card_promisc(True):
                QMessageBox.information(self, '开启结果', '开启混杂模式失败。', QMessageBox.Yes, QMessageBox.Yes)
                return
        else:
            self.statusBar().showMessage('停止嗅探，需要开启网卡混杂模式。')
            return

        self.ui.sniffer_tip_label.setHidden(True)

        # 设置表格数据源
        self._table_model.clear()
        self.ui.sniffer_table.setModel(self._table_model)
        self._table_model.setHorizontalHeaderLabels(['IP', 'MAC'])
        self._table_model.setColumnCount(2)

        # 开启嗅探线程
        self._sniffer_tool = NetSnifferTool()
        self._sniffer_tool.start_sniffer_thread(self._table_model, self.ui.sniffer_table, self.statusBar())

        # 修改控件状态
        self.ui.sniffer_stop_button.setEnabled(True)
        self.ui.sniffer_start_button.setEnabled(False)

    def stop_sniffer_thread(self):
        """
        关闭嗅探线程
        """
        # 关闭嗅探线程
        if self._sniffer_tool is not None:
            self._sniffer_tool.stop_sniffer_thread()

        # 修改控件状态
        self.ui.sniffer_start_button.setEnabled(True)
        self.ui.sniffer_stop_button.setEnabled(False)

        # 关闭网卡混杂模式
        OtherToolFunctionSet.turn_net_card_promisc(False)
        self.statusBar().showMessage('已停止。网卡混杂模式已关闭。')

    def start_scan_thread(self):
        """
        扫描给定IP的给定端口
        """
        target_ip = self.ui.scan_target_ip_edit.text()
        target_port_start = self.ui.scan_start_port_edit.text()
        target_port_stop = self.ui.scan_stop_port_edit.text()
        scan_timeout = self.ui.scan_timeout_edit.text()

        self._scan_tool = PortScanningTool(target_ip, target_port_start,
                                           target_port_stop, scan_timeout, self.statusBar())

        # 启动扫描线程
        self.statusBar().showMessage('正在扫描……')
        print('启动端口扫描：')

        # 设置表格模型
        self.ui.scan_result_table.setModel(self._scan_table_model)
        self._scan_table_model.clear()
        self._scan_table_model.setHorizontalHeaderLabels(['端口', '状态'])
        self._scan_table_model.setColumnCount(2)

        # 开始扫描
        self._scan_tool.start_scan_thread(self._scan_table_model, self.ui.scan_result_table,
                                          self.ui.scan_start_button, self.ui.scan_stop_button)

        # 修改控件状态
        self.ui.scan_stop_button.setEnabled(True)
        self.ui.scan_start_button.setEnabled(False)

    def stop_scan_thread(self):
        """
        停止端口扫描线程
        """
        if self._scan_tool is not None:
            self._scan_tool.stop_scan_thread()

        # 修改控件状态
        self.ui.scan_start_button.setEnabled(True)
        self.ui.scan_stop_button.setEnabled(False)
        self.statusBar().showMessage('端口扫描已停止。')

    def closeEvent(self, event: QCloseEvent):
        """
        窗口关闭回调，用于关闭工作线程。
        :param event: 关闭事件
        """
        # 关闭嗅探线程
        self.stop_sniffer_thread()
        # 关闭端口扫描线程
        self.stop_scan_thread()
