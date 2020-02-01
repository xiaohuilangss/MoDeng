# encoding=utf-8

import wx

from Experiment.ConfigDialog.StudentInfoGridTable import StudentInfoGridTable


class DataManager(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.Title = '数据管理'
        self.Size = (800, 600)
        self.panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        menu_box = wx.BoxSizer(wx.HORIZONTAL)

        btn_insert_none = wx.Button(self.panel, label='插入')
        self.Bind(wx.EVT_BUTTON, self.onClick1, btn_insert_none)
        menu_box.Add(btn_insert_none)

        btn_insert_data = wx.Button(self.panel, label='添加指定数据')
        self.Bind(wx.EVT_BUTTON, self.onClick2, btn_insert_data)
        menu_box.Add(btn_insert_data)

        btn_del = wx.Button(self.panel, label='删除')
        self.Bind(wx.EVT_BUTTON, self.onClick3, btn_del)
        menu_box.Add(btn_del)

        gridDatas = [
            [u'大仲马', u'男', 'SWUST', u'中文', u'研三'],
            [u'牛顿', u'男', u'SHUST', u'物理', u'博一'],
            [u'爱因斯坦', u'男', u'SHUST', u'物理', u'研一'],
            [u'居里夫人', u'女', u'SWUST', u'化学', u'研一'],
        ]
        self.gridTable = wx.grid.Grid(self.panel, -1, pos=(5, 5), size=(490, 300), style=wx.WANTS_CHARS)
        self.infoTable = StudentInfoGridTable(gridDatas)
        self.gridTable.SetTable(self.infoTable, True)

        vbox.Add(menu_box)
        vbox.Add(self.gridTable)

        self.panel.SetSizer(vbox)

    def onClick1(self, evt):
        self.infoTable.InsertRows()

    def onClick2(self, evt):
        # self.infoTable.InsertRows([u'居里夫人1', u'女', u'WUST', u'化学', u'研3'])
        self.infoTable.AppendRows()

    def onClick3(self, evt):
        self.infoTable.DeleteRows()

    def onClick4(self, evt):
        self.infoTable.InsertRows([u'居里夫人1', u'女', u'WUST', u'化学', u'研3'])


if __name__ == '__main__':
    app = wx.App()
    frame = DataManager()
    frame.Show()
    app.MainLoop()
