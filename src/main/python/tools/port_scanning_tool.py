# -*- coding: utf-8 -*-
"""
This class is used to scan the giving ports of the giving host.
"""
import socket


class PortScanningTool(object):
    def __init__(self, host, start_port, end_port, timeout=3):
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
