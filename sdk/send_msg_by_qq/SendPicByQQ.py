# encoding=utf-8

from ctypes import *
import os
from PIL import Image
from io import BytesIO
from pylab import *
import win32con, win32clipboard
import win32gui
import win32clipboard as w
import time
import win32clipboard as clip



def setPic(aString):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_BITMAP, aString)
    # win32clipboard.SetClipboardData(win32con.CF_DIB, aString)
    win32clipboard.CloseClipboard()


def send_pic_qq(towho, fig):

    """
    发送qq消息
    to_who：qq消息接收人
    msg：需要发送的消息
    """

    output = BytesIO()  # BytesIO实现了在内存中读写byte
    buf_save = BytesIO()

    fig.savefig(output, dpi=800)
    output.seek(0)
    img = Image.open(output)  # Image.open可以打开网络图片与本地图片。
    # img = Image.open('11.bmp')

    img.convert("RGB").save(buf_save, "BMP")  # 以RGB模式保存图像
    data = buf_save.getvalue()[14:]
    buf_save.close()
    output.close()

    # 将消息写到剪贴板
    setImage(data)

    # 获取qq窗口句柄
    qq = win32gui.FindWindow(None, towho)
    print(qq)
    while qq == 0:
        qq = win32gui.FindWindow(None, towho)
    print(qq)

    # 投递剪贴板消息到QQ窗体
    win32gui.SendMessage(qq, 258, 22, 2080193)
    win32gui.SendMessage(qq, 770, 0, 0)

    # 模拟按下回车键
    win32gui.SendMessage(qq, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.SendMessage(qq, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


def send_pic_qq_data(towho, data):

    """
    发送qq消息
    to_who：qq消息接收人
    msg：需要发送的消息
    """

    # 将消息写到剪贴板
    setImage(data)

    # 获取qq窗口句柄
    qq = win32gui.FindWindow(None, towho)
    print(qq)
    while qq == 0:
        qq = win32gui.FindWindow(None, towho)
    print(qq)

    # 投递剪贴板消息到QQ窗体
    win32gui.SendMessage(qq, 258, 22, 2080193)
    win32gui.SendMessage(qq, 770, 0, 0)

    # 模拟按下回车键
    win32gui.SendMessage(qq, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.SendMessage(qq, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

def setImage(data):
    clip.OpenClipboard()                            # 打开剪贴板
    clip.EmptyClipboard()                           # 先清空剪贴板
    clip.SetClipboardData(win32con.CF_DIB, data)    # 将图片放入剪贴板
    clip.CloseClipboard()


if __name__ == '__main__':

    # im = Image.open('new.jpg')
    # im.save('11.bmp')
    # aString = windll.user32.LoadImageW(0, r"11.bmp", win32con.IMAGE_BITMAP, 0, 0, win32con.LR_LOADFROMFILE)
    fig = plt.figure()
    plt.title('Just a test!')

    send_pic_qq('影子2')
    plt.close()

    end = 0
