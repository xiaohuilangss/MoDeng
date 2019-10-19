# encoding=utf-8


import wx


class KeyEvent(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        panel = wx.Panel(self, -1)
        # panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        panel.SetFocus()
        self.nb = wx.Notebook(self)
        self.nb.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.Centre()
        self.Show(True)

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_F1:
            self.SetPosition((0, 0))
            self.SetSize(wx.DisplaySize())
        else:
            event.Skip()


app = wx.App()
KeyEvent(None, -1, 'keyevent.py')
app.MainLoop()