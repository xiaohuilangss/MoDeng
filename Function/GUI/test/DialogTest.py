import wx
import pyqtgraph.examples

if __name__ == "__main__":
    pyqtgraph.examples.run()
    app = wx.App()
    dialog = wx.DirDialog(None, "请选择生成报告的存放路径:",
                          style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    dialog.Destroy()
