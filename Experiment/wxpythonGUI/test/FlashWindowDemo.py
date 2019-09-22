# encoding=utf-8
import wx
import win32gui

from Experiment.wxpythonGUI.MyCode.IconFlashSub import flash


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="wx.Timer")
        self.Show()
        end = 0

        # 配置和创建小时图片更新定时器
        self.timer_pic = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER,
            self.OnTimer,
            self.timer_pic)
        self.timer_pic.Start(1000 * 7)

    def OnTimer(self, evt):
        """
        定时器响应函数
        :return:
        """
        win32gui.FlashWindowEx(self.GetHandle(), 2, 3, 400)


app = wx.App()
frm = MyFrame()
frm.Show()

flash(frm.GetHandle())
app.MainLoop()