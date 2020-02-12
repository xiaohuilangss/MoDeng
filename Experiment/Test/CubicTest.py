import wx
import wx.adv

import wx.adv
import time


def create_splash():
    # create a welcome screen
    screen = wx.Image("file.png").ConvertToBitmap()
    wx.adv.SplashScreen(screen, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT, 1000, None, -1)
    time.sleep(1)


class TaskBarIcon(wx.adv.TaskBarIcon):
    ID_EXIT = wx.NewId()

    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        # self.SetIcon(wx.Icon(name='favicon.ico', type=wx.BITMAP_TYPE_ICO), 'TaskBarIcon!')
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnExit, id=self.ID_EXIT)

    # 双击托盘图标打开界面
    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def OnExit(self, event):
        self.Destroy()

    # override
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_EXIT, 'Exit')
        return menu


class Frame(wx.Frame):
    def __init__(
            self, parent=None, id=wx.ID_ANY, title='TaskBarIcon', pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
    ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # 在init中创建一个系统托盘实例即可
        self.taskBarIcon = TaskBarIcon(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    app.locale = wx.Locale(wx.LANGUAGE_CHINESE_SIMPLIFIED)
    frame = Frame()
    app.MainLoop()
