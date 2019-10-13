# -*- coding: utf-8 -*-
"""
这个工具类用来对目标主机进行端口扫描。
TODO 将此工具类对端口的扫描改为多线程
"""
import socket
import threading
from PySide2.QtGui import QStandardItem


class PortScanningTool(object):
    def __init__(self, host, start_port, end_port, timeout, status_bar):
        """
        构造函数。
        :param host: 目标主机IP
        :param start_port: 扫描起始端口号（包括）
        :param end_port: 扫描结束端口号（包括）
        :param timeout: 端口响应超时时间
        """
        self._status = True
        self._host = host
        self._start_port = int(start_port)
        self._end_port = int(end_port)
        self._timeout = int(timeout)
        self._status_bar = status_bar

    def start_scan_thread(self, table_view_model, table_view, scan_start_button, scan_stop_button):
        """
        开启扫描线程。
        :param table_view_model: 界面列表视图模型
        :param table_view: 界面列表视图
        """
        def _scan_thread():
            print(threading.current_thread().name + '：端口扫描线程已启动。')
            for port in range(self._start_port, self._end_port + 1):
                if not self._status:
                    break
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self._timeout)
                self._status_bar.showMessage('正在扫描端口' + str(port) + '……')
                print('正在扫描端口' + str(port) + '……')
                result_code = s.connect_ex((self._host, port))
                if result_code == 0:
                    table_view_model.appendRow([QStandardItem(str(port)), QStandardItem('开放')])
                else:
                    table_view_model.appendRow([QStandardItem(str(port)), QStandardItem('关闭')])
                table_view.resizeColumnsToContents()
                s.close()
            # 修改控件状态
            scan_start_button.setEnabled(True)
            scan_stop_button.setEnabled(False)
            self._status_bar.showMessage('扫描已停止。')
            print(threading.current_thread().name + '：扫描线程已停止。')

        scan_thread = threading.Thread(target=_scan_thread, name='Scan-Thread')
        scan_thread.start()

    def stop_scan_thread(self):
        """
        停止扫描线程
        """
        self._status = False
