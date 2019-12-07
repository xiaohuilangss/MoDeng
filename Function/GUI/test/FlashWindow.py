# coding=utf-8

__author__ = 'Administrator'

__doc__ = '''
pythonwin中win32gui的用法
本文件演如何使用win32gui来遍历系统中所有的顶层窗口，
并遍历所有顶层窗口中的子窗口
'''

import win32gui
from pprint import pprint


def gbk2utf8(s):
    return s.decode('gbk').encode('utf-8')


def show_window_attr(hWnd):
    '''
    显示窗口的属性
    :return:
    '''
    if not hWnd:
        return

    # 中文系统默认title是gb2312的编码
    title = win32gui.GetWindowText(hWnd)
    # title = gbk2utf8(title)
    clsname = win32gui.GetClassName(hWnd)

    print('窗口句柄:%s ' % (hWnd))

    print('窗口标题:%s' % (title))

    print('窗口类名:%s' % (clsname))

    print('')



def show_windows(hWndList):
    for h in hWndList:
        show_window_attr(h)


def demo_top_windows():
    '''
    演示如何列出所有的顶级窗口
    :return:
    '''
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)
    show_windows(hWndList)

    return hWndList


def demo_child_windows(parent):
    '''
    演示如何列出所有的子窗口
    :return:
    '''
    if not parent:
        return

    hWndChildList = []
    win32gui.EnumChildWindows(parent, lambda hWnd, param: param.append(hWnd), hWndChildList)
    show_windows(hWndChildList)
    return hWndChildList


hWndList = demo_top_windows()
assert len(hWndList)

parent = hWndList[20]

# 这里系统的窗口好像不能直接遍历，不知道是否是权限的问题
hWndChildList = demo_child_windows(parent)

print('-----top windows-----')
pprint(hWndList)

print('-----sub windows:from %s------' % (parent))
pprint(hWndChildList)
