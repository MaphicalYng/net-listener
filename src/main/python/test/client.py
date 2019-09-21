# -*- coding: utf-8 -*-

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('maphical.cn', 8080))
print('Connected...')
while True:
    i = input('Input the data: ')
    s.send(i.encode('utf-8'))
    data = s.recv(1024)
    str_data = data.decode('utf-8')
    print('Received: ', str_data)
    if str_data == 'Shutdown server...':
        print('Server shutdown. Exit')
        break
s.close()
