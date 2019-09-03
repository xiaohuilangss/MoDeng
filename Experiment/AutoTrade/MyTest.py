# encoding = utf-8


import tkinter.messagebox,os
from tkinter import *
from tkinter.ttk import *
from tkinter import Menu
import datetime
import threading
import pickle
import time
import tushare as ts
import pywinauto
import pywinauto.clipboard
import pywinauto.application


app = pywinauto.application.Application()
app.connect(title='金太阳')

main_hwnd = pywinauto.findwindows.find_window(title=U'金太阳')
trade_hwnd = pywinauto.findwindows.find_windows(top_level_only=False, title=U'交易面板框架', parent=main_hwnd)[0]

trade_window = app.window_(handle=trade_hwnd)

rect = trade_window

x = rect.width()  // 8
y = rect.height() // 2

trade_hwnd.CCustomTabCtrl.ClickInput(coords=(x, y))

time.sleep(0.5)