# -*- coding: utf-8 -*-
"""
这个工具类用来读取本地网络配置信息
"""
import psutil
import socket
import threading
from tools.other_tool_function_set import OtherToolFunctionSet


class LocalhostNetInfoTool(object):
    ipv4 = socket.AF_INET
    ipv6 = socket.AF_INET6
    mac = socket.AF_PACKET

    def __init__(self):
        self._raw = psutil.net_if_addrs()

    def _get_info(self):
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

    def start_local_info_thread(self, device_info_label, scroll_area_widget_contents, status_bar, refresh_button):
        def _local_info_thread():
            print(threading.current_thread().name + '：配置读取线程已启动。')
            print(threading.current_thread().name + '：正在读取当前激活的网卡名称……')
            running_card = OtherToolFunctionSet.get_running_card_name()
            print(threading.current_thread().name + '：正在读取所有网卡的地址信息……')
            info = self._get_info()
            print(threading.current_thread().name + '：正在利用ARP外部命令读取网关和本机的MAC地址……')
            addresses = OtherToolFunctionSet.get_localhost_gateway_mac(running_card)

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
                        if address_family == self.ipv4:
                            result_string += '\tIPv4：\r\n'
                        if address_family == self.ipv6:
                            result_string += '\tIPv6：\r\n'
                        if address_family == self.mac:
                            result_string += '\tMAC：\r\n'
                        if address:
                            result_string += '\t\t地址：' + address + '\r\n'
                        if netmask:
                            result_string += '\t\t子网掩码：' + netmask + '\r\n'
            # print(result_string)
            device_info_label.setText(result_string)
            device_info_label.adjustSize()
            scroll_area_widget_contents.setMinimumHeight(device_info_label.geometry().height())
            print(threading.current_thread().name + '：读取解析完成。')
            # 修改控件状态
            refresh_button.setEnabled(True)
            status_bar.showMessage('网络配置读取完成。')
            print(threading.current_thread().name + '：配置读取线程已停止。')

        local_info_thread = threading.Thread(target=_local_info_thread, name='LocalInfo-Thread')
        local_info_thread.start()
