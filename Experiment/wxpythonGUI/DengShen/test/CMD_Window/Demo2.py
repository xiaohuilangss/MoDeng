# coding=utf-8

import wx
import os


class DengShen(wx.Frame):
    def __init__(self, parent, title):
        super(DengShen, self).__init__(parent, title=title, size=(700, 500))

        panel = wx.Panel(self)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.t3 = wx.TextCtrl(panel, size=(600, 1000), style=wx.TE_MULTILINE)

        hbox3.Add(self.t3, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

        self.t3.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPressed)
        self.t3.SetBackgroundColour('Black'), self.t3.SetForegroundColour('Green')
        panel.SetSizer(hbox3)

        self.Centre()
        self.Show()
        self.Fit()

    def OnKeyTyped(self, event):
        print(event.GetString())

    def OnEnterPressed(self, event):
        self.t3.AppendText(event.GetString())
        # result = os.popen(event.GetString())
        # res = result.read()
        # for line in res.splitlines():
            # print(line)
            # self.t3.AppendText(line)

    def OnMaxLen(self, event):
        print("Maximum length reached")


app = wx.App()
DengShen(None, '灯神')
app.MainLoop()
