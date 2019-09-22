# encoding=utf-8

"""

"""

# -*- coding:utf-8 -*-
'''
    filename : winapi.py
'''
from ctypes import *
import win32con

__all__ = ['flash']

FlashWindowEx = windll.user32.FlashWindowEx


class FLASHWINFO(Structure):
    _fields_ = [('cbSize', c_uint),
                ('hwnd', c_uint),
                ('dwFlags', c_uint),
                ('uCount', c_uint),
                ('dwTimeout', c_uint)]


def flash(hwnd):
    '''Flash a window with caption and tray.'''
    info = FLASHWINFO(0, hwnd, win32con.FLASHW_ALL | win32con.FLASHW_TIMERNOFG, 0, 0)
    info.cbSize = sizeof(info)
    FlashWindowEx(byref(info))