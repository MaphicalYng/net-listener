# -*- coding: utf-8 -*-
"""
这个工具类用来对目标主机进行端口扫描。
TODO 将此工具类对端口的扫描改为多线程
"""
import socket


class PortScanningTool(object):
    def __init__(self, host, start_port, end_port, timeout=3):
        """
        构造函数。
        :param host: 目标主机IP
        :param start_port: 扫描起始端口号（包括）
        :param end_port: 扫描结束端口号（包括）
        :param timeout: 端口响应超时时间
        """
        self._host = host
        self._start_port = start_port
        self._end_port = end_port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        self._result = []

    def scan(self):
        for port in range(self._start_port, self._end_port + 1):
            result_code = self._socket.connect_ex((self._host, port))
            if result_code == 0:
                self._result.append(port)

    def get_result_and_close(self):
        self._socket.close()
        return self._result
