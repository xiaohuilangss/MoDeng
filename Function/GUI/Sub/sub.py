# encoding=utf-8
import wx
import wx.xrc
import wx.grid


def text_append_color(tc, text, color=wx.GREEN):
    """
    wxpython textctrl控件， 显示绿色字体的内容
    :return:
    """
    tc.SetDefaultStyle(wx.TextAttr(color))
    tc.AppendText(text)
    tc.SetDefaultStyle(wx.TextAttr(wx.RED))