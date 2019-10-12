# -*- coding: utf-8 -*-
"""
这个工具类用来对目标主机进行端口扫描。
TODO 将此工具类对端口的扫描改为多线程
"""
import socket
import threading


class PortScanningTool(object):
    def __init__(self, host, start_port, end_port, timeout, status_bar):
        """
        构造函数。
        :param host: 目标主机IP
        :param start_port: 扫描起始端口号（包括）
        :param end_port: 扫描结束端口号（包括）
        :param timeout: 端口响应超时时间
        """
        self._host = host
        self._start_port = int(start_port)
        self._end_port = int(end_port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(int(timeout))
        self._result = []
        self._status_bar = status_bar

    def scan(self):
        def _scan_thread():
            for port in range(self._start_port, self._end_port + 1):
                self._status_bar.showMessage('正在扫描端口' + str(port))
                print('正在扫描端口' + str(port))
                result_code = self._socket.connect_ex((self._host, port))
                if result_code == 0:
                    self._result.append(port)
            self._socket.close()
            print('扫描结果：', self._result)

        scan_thread = threading.Thread(target=_scan_thread, name='Scan-Thread')
        scan_thread.start()
