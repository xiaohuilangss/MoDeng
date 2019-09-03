# encoding=utf-8

from socket import *
from time import ctime

host = ''
port = 12345
buffsize = 2048
ADDR = (host, port)

tctime = socket(AF_INET, SOCK_STREAM)
tctime.bind(ADDR)
tctime.listen(3)

while True:
    print('Wait for connection ...')
    tctimeClient,addr = tctime.accept()
    print("Connection from :",addr)

    while True:
        data = tctimeClient.recv(buffsize).decode()
        if not data:
            break
        tctimeClient.send(('[%s] %s' % (ctime(),data)).encode())
    tctimeClient.close()

tctimeClient.close()