# -*- coding: utf-8 -*-

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 8080))
s.listen(1)
print('Waiting for connection...')
conn, addr = s.accept()
print('conn=', conn)
print('addr=', addr)
while True:
    str_byte = conn.recv(1024)
    str_data = str_byte.decode('utf-8')
    print('Received data: ', str_data)
    if str_data == 'end':
        conn.send('Shutdown server...'.encode('utf-8'))
        break
    else:
        conn.send(('Received data: ' + str_data).encode('utf-8'))
conn.close()
s.close()
