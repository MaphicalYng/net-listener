# -*- coding: utf-8 -*-
"""
这个工具类用来对局域网络进行嗅探。
"""
import re
import socket
import struct
import binascii
import threading
from tools.other_tool_function_set import OtherToolFunctionSet
from PySide2.QtGui import QStandardItem


class NetSnifferTool(object):
    def __init__(self):
        self._not_show_ips = [
            '0.0.0.0', '255.255.255.255'
        ]
        self._not_show_macs = [
            'ff:ff:ff:ff:ff:ff'
        ]
        self._status = True
        self._known_hosts = []
        self._sniffer_thread = None

    def get_sniffer_status(self):
        return self._status

    def start_sniffer_thread(self, table_view_model, table_view, status_bar, start_button, stop_button):
        """
        启动嗅探线程。
        """
        # 启动线程
        def _sniffer_thread():
            """
            线程嗅探逻辑
            """
            print(threading.current_thread().name + '：嗅探线程已启动。')
            # 获得网关的和本机的MAC地址
            status_bar.showMessage('准备嗅探……')
            running_card = OtherToolFunctionSet.get_running_card_name()
            addresses = OtherToolFunctionSet.get_localhost_gateway_mac(running_card)
            localhost_mac = addresses[0]
            gateway_mac = addresses[1]

            status_bar.showMessage('正在嗅探……')

            def __turn_mac_style(mac_raw):
                return mac_raw[0:2] + ':' + mac_raw[2:4] + ':' + mac_raw[4:6]\
                       + ':' + mac_raw[6:8] + ':' + mac_raw[8:10] + ':' + mac_raw[10:12]

            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
            while self._status:
                # 接收所有的数据帧
                data = s.recvfrom(2048)
                pack = data[0]
                frame_header_b = pack[0:14]
                ip_header_b = pack[14:34]
                frame_header_s = struct.unpack('!6s6s2s', frame_header_b)
                ip_header_s = struct.unpack('!12s4s4s', ip_header_b)
                source_mac_row = binascii.hexlify(frame_header_s[0])
                dest_mac_row = binascii.hexlify(frame_header_s[1])
                source_mac = __turn_mac_style(str(source_mac_row)[2:])
                dest_mac = __turn_mac_style(str(dest_mac_row)[2:])
                source_ip = socket.inet_ntoa(ip_header_s[1])
                dest_ip = socket.inet_ntoa(ip_header_s[2])

                # 组播地址正则表达式
                reg = '^224\.0\.0\..+$'
                reg_com = re.compile(reg)

                # 判定数据帧中的mac和ip是否符合收录条件
                # 判断这些MAC是否是网关或本机
                if source_mac != localhost_mac and source_mac != gateway_mac:
                    if not self._not_show_ips.__contains__(source_ip) \
                            and not self._not_show_macs.__contains__(source_mac):
                        # 去除组播地址
                        if not reg_com.match(source_ip):
                            target_new_source = {source_ip: source_mac}
                            if not self._known_hosts.__contains__(target_new_source):
                                self._known_hosts.append(target_new_source)
                                # 将新收录的地址加入界面
                                table_view_model.appendRow([QStandardItem(source_ip), QStandardItem(source_mac)])

                if dest_mac != localhost_mac and dest_mac != gateway_mac:
                    if not self._not_show_ips.__contains__(dest_ip) \
                            and not self._not_show_macs.__contains__(dest_mac):
                        if not reg_com.match(dest_ip):
                            target_new_dest = {dest_ip: dest_mac}
                            if not self._known_hosts.__contains__(target_new_dest):
                                self._known_hosts.append(target_new_dest)
                                # 将新收录的地址加入界面
                                table_view_model.appendRow([QStandardItem(dest_ip), QStandardItem(dest_mac)])

                table_view.resizeColumnsToContents()

            # 关闭网卡混杂模式
            OtherToolFunctionSet.turn_net_card_promisc(False)
            # 修改控件状态
            start_button.setEnabled(True)
            stop_button.setEnabled(False)
            status_bar.showMessage('嗅探已停止，网卡混杂模式已关闭。')
            print(threading.current_thread().name + '：嗅探线程已停止。')

        self._sniffer_thread = threading.Thread(target=_sniffer_thread, name='Sniffer-Thread')
        self._sniffer_thread.start()

    def stop_sniffer_thread(self):
        """
        停止嗅探线程
        """
        self._status = False
