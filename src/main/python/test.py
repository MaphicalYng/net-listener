# -*- coding: utf-8 -*-
import socket
import struct
import binascii

s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
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
print('Source mac = ', source_mac)
print('Dest mac = ', dest_mac)
print('Source ip = ', source_ip)
print('Dest ip = ', dest_ip)
s.close()
