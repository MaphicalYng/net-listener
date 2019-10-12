#!/usr/bin/env python3.6
# coding: utf-8
from scapy.all import srp, Ether, ARP

subnet = '192.168.3.0/24'
ether = Ether(dst="FF:FF:FF:FF:FF:FF")
arp = ARP(pdst=subnet)
(ans, unans) = srp(ether / arp, timeout=2)
for (send, rcv) in ans:
    addr_info = rcv.sprintf("%ARP.psrc%---%Ether.src%")
    print(addr_info)
