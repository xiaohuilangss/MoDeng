# coding = utf-8
import win32api
import win32gui
import win32con
import win32clipboard as clipboard
import time
#from pynput.mouse import Button, Controller as mController
from pynput.keyboard import Key, Controller as kController
from PIL import Image
from io import BytesIO #python3,新增字节流

#mouse = mController()
keyboard = kController()
#print(type(keyboard))

#####################以下为QQ发送消息部分==============
#
#定义指定图片文件复制到剪贴板函数

def pic_ctrl_c(pathfile):
    img = Image.open(pathfile)
    output = BytesIO()                              # 如是StringIO分引起TypeError: string argument expected, got 'bytes'
    img.convert("RGB").save(output, "BMP")          # 以BMP格式保存流
    data = output.getvalue()[14:]                   # bmp文件头14个字节丢弃
    output.close()
    clipboard.OpenClipboard()                           # 打开剪贴板
    clipboard.EmptyClipboard()                          # 先清空剪贴板
    clipboard.SetClipboardData(win32con.CF_DIB, data)   # 将图片放入剪贴板
    clipboard.CloseClipboard()
    return


# 查找QQ(TIM)窗口，发送人双击，激活为单独窗口
title_name = '天空'
win = win32gui.FindWindow('TXGuiFoundation',title_name)
print("找到句柄：%x" % win)
if win!=0:
    left, top, right, bottom = win32gui.GetWindowRect(win)
    print(left, top, right, bottom)     # 最小化为负数,有时可以发
    win32gui.SetForegroundWindow(win)
else:
    print('请注意：找不到【%s】这个人（或群），请激活窗口！' % title_name)
#
# #定义文本信息
str1 = '你好，这是QQ文本自动发送测试。'
# clipboard.OpenClipboard()#将信息缓存入剪贴板
# clipboard.EmptyClipboard()
# clipboard.SetClipboardData(win32con.CF_UNICODETEXT,str1)
# clipboard.CloseClipboard()

# #读取BMP图片文件发送,只读bmp可以用
# from ctypes import windll
# filename='D:/2018bigdata/test2.bmp'
# bmp_id= windll.user32.LoadImageW(0, filename, win32con.IMAGE_BITMAP, 0, 0, win32con.LR_LOADFROMFILE)
# print(filename,type(bmp_id),bmp_id)
# if bmp_id != 0:  ## 由于图片编码问题  图片载入失败的话  bmp_id就等于0
#     clipboard.OpenClipboard()
#     clipboard.EmptyClipboard()
#     clipboard.SetClipboardData(win32con.CF_BITMAP, bmp_id)
#     clipboard.CloseClipboard()
# time.sleep(1)#缓冲时间

# 粘贴到发送区域
input_file = 'D:/2018bigdata/jz2018tv.png'                  # 要发送的图片文件
pic_ctrl_c(input_file)
time.sleep(1)
win32api.PostMessage(win, win32con.WM_PASTE, 0, 0)          # 相当于CTRL V
keyboard.type(str1)                                         # 发送字符串消息,需要pip install pynput
time.sleep(1)                                               # 缓冲时间

# 如果QQ回车发送，以下单独回车
# win32gui.SendMessage(win,win32con.WM_KEYDOWN,win32con.VK_RETURN,0)
# 以下为“CTRL+回车”组合键发送

win32api.keybd_event(17, 0, 0, 0)                           # 有效，按下CTRL
time.sleep(1)                                               # 需要延时
win32gui.SendMessage(win, win32con.WM_KEYDOWN, 13, 0)       # 窗口回车代码：win32con.VK_RETURN
win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)    # 放开CTRL


# 其它
# win32api.keybd_event(8,0,0,0)#代表当前环境，有效
# win32api.keybd_event(8,0,win32con.KEYEVENTF_KEYUP,0)
# #win32api.keybd_event(13,0,0,0)#当前环境回车有效
#####################################################QQ发送结束======

############################################其它资料##############
#   键盘键与虚拟键码对照表
#
# 字母和数字键   数字小键盘的键    功能键             其它键 
# 键　　 键码　  　键　　 键码　　　 键　　 键码 　　  键　　　　键码 
# A　　　65　　   0 　　96 　　　　F1 　　112 　　Backspace 　　　8 
# B　　　66　　   1　　 97 　　　　F2 　　113　　 Tab             9 
# C　　　67 　　  2 　　98 　  　　F3 　　114　　  Clear 　　12 
# D　　　68　　　3　　 99 　　　　F4 　　115　　Enter 　　　　　13 
# E　　　69 　　  4 　　100　　　　F5 　　116　　Shift　　　　　 16 
# F　　　70 　　  5 　　101　　　　F6 　　117　　Control 　　　　17 
# G　　　71 　　  6　　 102　　　　F7 　　118 　　Alt          18 
# H　　　72 　　　7 　　103　 　　F8 　　119　　Caps Lock 　　　20 
# I　　　73 　　　8 　　104　　　　F9 　　120　　Esc             27 
# J　　　74 　　　9　　 105　　　　F10　　121　　Spacebar　　　　32 
# K　　　75 　　　* 　　106　  　　F11　　122　　Page Up　　　　 33 
# L　　　76 　　　+ 　　107　　  　F12　　123　　Page Down 　　　34 
# M　　　77 　　　Enter 108　　　　-- 　　--　　　End             35 
# N　　　78 　　　-　　 109　　　　-- 　　-- 　　　Home           36 
# O　　　79 　　　. 　　110　　　　--　　 -- 　　 　Left Arrow　　　37 
# P　　　80 　　　/ 　　111　　　　--　　 -- 　　 　Up Arrow　　　　38 
# Q　　　81 　　　-- 　　--　　　 　--　　 -- 　　 　Right Arrow 　　39 
# R　　　82 　　　-- 　　--　　　　--　　 -- 　　 　　Down Arrow 　　 40 
# S　　　83 　　　-- 　　--　　　　　-- 　　-- 　　 　Insert 　　　　 45 
# T　　　84 　　　-- 　　--　　　　　--　　 -- 　　 　Delete 　　　　 46 
# U　　　85 　　　-- 　　--　　　 　-- 　　-- 　　 　Help 　　　　　 47 
# V　　　86 　　　--　　 --　　　　-- 　　-- 　　 　Num Lock 　　　 144 
# W　　　87 　　　
# X　　　88 　　　　　
# Y　　　89 　　　　　
# Z　　　90 　　　　　
# 0　　　48 　　　　　
# 1　　　49 　　　　　
# 2　　　50
# 3　　　51
# 4　　　52
# 5　　　53
# 6　　　54
# 7　　　55
# 8　　　56
# 9　　　57 　
#########################################
