# encoding=utf-8

import win32gui, win32con

# 2. win32gui.FindWindow找到目标程序：
win = win32gui.FindWindow(None, u'新建文本文档.txt - 记事本')

# 3. 使用win32gui.FindWindowEx找到目标文本框：

tid = win32gui.FindWindowEx(win, None, 'Edit', None)

# 4.使用win32gui.SendMessage发送文本到目标文本框：
win32gui.SendMessage(tid, win32con.WM_SETTEXT, None, 'hello')

# 输入中文

win32gui.SendMessage(tid, win32con.WM_SETTEXT, None, u'你好'.encode('gbk'))


# 当然了，可以继续找到下一个文本框：
username = win32gui.FindWindowEx(win, tid, 'Edit', None)

# 发送回车的方法
win32gui.SendMessage(tid, win32con.WM_SETTEXT, None, 'hello')
win32gui.PostMessage(tid, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
win32gui.PostMessage(tid, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

