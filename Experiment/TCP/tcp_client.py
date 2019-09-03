# encoding=utf-8

from socket import *
import json
import time

HOST ='localhost'

PORT = 4012

BUFFSIZE=2048

ADDR = (HOST,PORT)

tctimeClient = socket(AF_INET,SOCK_STREAM)

tctimeClient.connect(ADDR)
print('连接成功！')
time.sleep(2)

data = json.dumps({'name': 'yang', 'age': 12, 'area': 'china', 'note':"""The rock carvings - known as petroglyphs - have been discovered in their thousands atop hillocks in the Konkan region of western Maharashtra.

Mostly discovered in the Ratnagiri and Rajapur areas, a majority of the images etched on the rocky, flat hilltops remained unnoticed for thousands of years.

Most of them were hidden beneath layers of soil and mud. But a few were in the open - these were considered holy and worshipped by locals in some areas.

The sheer variety of the rock carvings have stunned experts - animals, birds, human figures and geometrical designs are all depicted.

The way the petroglyphs have been drawn, and their similarity to those found in other parts of the world, have led experts to believe that they were created in prehistoric times and are possibly among the oldest ever discovered.

"Our first deduction from examining these petroglyphs is that they were created around 10,000BC," the director of the Maharashtra state archaeology department, Tejas Garge, told the BBC.

The credit for their discovery goes to a group of explorers led by Sudhir Risbood and Manoj Marathe, who began searching for the images in earnest after observing a few in the area. Many were found in village temples and played a part in local folklore.

"We walked thousands of kilometres. People started sending photographs to us and we even enlisted schools in our efforts to find them. We made students ask their grandparents and other village elders if they knew about any other engravings. This provided us with a lot of valuable information," Mr Risbood told the BBC.

Together they found petroglyphs in and around 52 villages in the area. But only around five villages were aware that the images even existed."""})

data_multi = data+'$'+data+'$'+data+'$'

perface = json.dumps({'type':1, 'frage_size':20, 'total_size':123})

data = perface

i = 0
while True:
    # data = input(">")
    data_temp = data_multi[i:i+100]
    if not data_temp:
        break
    tctimeClient.send(data_temp.encode())
    data_temp = tctimeClient.recv(BUFFSIZE).decode()
    if not data_temp:
        break
    print(data_temp)
    i = i+100
    time.sleep(0.2)
tctimeClient.close()