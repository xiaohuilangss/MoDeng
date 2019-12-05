import wx

class Myframe(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1)
        nb=wx.Notebook(self)
        pane1_1=wx.Panel(nb,-1)
        wx.StaticText(pane1_1, label='i am pane1_1')
        pane1_2 = wx.Panel(nb, -1)
        wx.StaticText(pane1_2, label='i am pane1_2')
        pane1_3 = wx.Panel(nb, -1)
        wx.StaticText(pane1_3, label='i am pane1_3')
        map(nb.AddPage,[pane1_1,pane1_2,pane1_3],["pane1_1","pane1_2","pane1_3"])

app=wx.App()
frame=Myframe()
frame.Show(True)
app.MainLoop()