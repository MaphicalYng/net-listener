# -*- coding: utf-8 -*-
import socket
import struct
import binascii

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
try:
    while True:
        data = s.recvfrom(2048)
        pack = data[0]
        frame_header_b = pack[0:14]
        ip_header_b = pack[14:34]
        frame_header_s = struct.unpack('!6s6s2s', frame_header_b)
        ip_header_s = struct.unpack('!12s4s4s', ip_header_b)
        source_mac = binascii.hexlify(frame_header_s[0])
        dest_mac = binascii.hexlify(frame_header_s[1])
        source_ip = socket.inet_ntoa(ip_header_s[1])
        dest_ip = socket.inet_ntoa(ip_header_s[2])
        mac_raw = str(source_mac)[2:-1]
        mac = mac_raw[0:2] + ':' + mac_raw[2:4] + ':' + mac_raw[4:6] + ':' + mac_raw[6:8] + ':' + mac_raw[8:10] + ':' + mac_raw[10:12]
        print(mac)
        print('Source mac = ', source_mac)
        print('Dest mac = ', dest_mac)
        print('Source ip = ', source_ip)
        print('Dest ip = ', dest_ip)
        print(type(source_mac))
except BaseException as e:
    s.close()
    print('Socket closed.\r\nClose cause: ', str(type(e)))
