# -*- coding: utf-8 -*-
"""
工具函数集合
"""
import os
import netifaces


class OtherToolFunctionSet(object):
    @staticmethod
    def test_root_permission():
        """
        测试程序是否以root身份运行
        """
        shell_result = os.popen('whoami').readlines()
        return shell_result[0] == 'root\n'

    @staticmethod
    def turn_net_card_promisc(if_on=False):
        """
        开启网卡混杂模式
        :return: 是否开启成功(boolean)
        """
        """
        # 获取网卡名称
        shell_result = os.popen("cat /proc/net/dev | awk '{i++; if(i>2){print $1}}'\
         | sed 's/^[\t]*//g' | sed 's/[:]*$//g'").readlines()
        """
        card_name = netifaces.gateways()['default'][netifaces.AF_INET][1]

        # 开启混杂模式
        if if_on:
            command = 'ifconfig ' + card_name + ' promisc'
        else:
            command = 'ifconfig ' + card_name + ' -promisc'
        print('执行外部Shell命令：' + command)
        return os.system(command) == 0

    @staticmethod
    def get_localhost_gateway_mac():
        """
        获取当前网卡的MAC地址和网关的MAC地址
        :return: 本机MAC地址、网关MAC地址和网关IP地址
        """
        card_name = netifaces.gateways()['default'][netifaces.AF_INET][1]
        gateway_ip_address = netifaces.gateways()['default'][netifaces.AF_INET][0]
        localhost_mac_address = netifaces.ifaddresses(card_name)[netifaces.AF_LINK][0]['addr']

        # 通过ARP获取网关MAC
        command = 'arp ' + gateway_ip_address
        shell_result = os.popen(command).readlines()[1]
        gateway_mac_address = shell_result.split()[2]
        return localhost_mac_address, gateway_mac_address, gateway_ip_address


