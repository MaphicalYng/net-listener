# -*- coding: utf-8 -*-
"""
This class is used to get info about net device of localhost.
"""
import psutil


class LocalhostNetInfoTool(object):
    def __init__(self):
        self._raw = psutil.net_if_addrs()

    def get_info(self):
        raw = self._raw
        result = []
        for name, item in raw.items():
            device_info = []
            for info in item:
                i = {'AddressFamily': info.family, 'Address': info.address, 'Netmask': info.netmask}
                device_info.append(i)
            device = {name: device_info}
            result.append(device)
        return result
