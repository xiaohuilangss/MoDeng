# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(854, 484), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"配置海选参数"), wx.VERTICAL)

        self.m_grid5 = wx.grid.Grid(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(800, 300), 0)

        # Grid
        self.m_grid5.CreateGrid(5, 5)
        self.m_grid5.EnableEditing(True)
        self.m_grid5.EnableGridLines(True)
        self.m_grid5.SetGridLineColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_CAPTIONTEXT))
        self.m_grid5.EnableDragGridSize(False)
        self.m_grid5.SetMargins(0, 0)

        # Columns
        self.m_grid5.SetColSize(0, 80)
        self.m_grid5.SetColSize(1, 80)
        self.m_grid5.SetColSize(2, 80)
        self.m_grid5.SetColSize(3, 81)
        self.m_grid5.SetColSize(4, 80)
        self.m_grid5.EnableDragColMove(False)
        self.m_grid5.EnableDragColSize(True)
        self.m_grid5.SetColLabelSize(30)
        self.m_grid5.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.m_grid5.EnableDragRowSize(True)
        self.m_grid5.SetRowLabelSize(80)
        self.m_grid5.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.m_grid5.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        sbSizer1.Add(self.m_grid5, 0, wx.ALL, 5)

        self.m_dirPicker5 = wx.DirPickerCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, u"设置海选pdf生成后存放的路径\n",
                                             u"Select a folder", wx.DefaultPosition, wx.Size(500, -1),
                                             wx.DIRP_DEFAULT_STYLE)
        self.m_dirPicker5.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        sbSizer1.Add(self.m_dirPicker5, 0, wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        m_sdbSizer3 = wx.StdDialogButtonSizer()
        self.m_sdbSizer3OK = wx.Button(sbSizer1.GetStaticBox(), wx.ID_OK)
        m_sdbSizer3.AddButton(self.m_sdbSizer3OK)
        self.m_sdbSizer3Cancel = wx.Button(sbSizer1.GetStaticBox(), wx.ID_CANCEL)
        m_sdbSizer3.AddButton(self.m_sdbSizer3Cancel)
        m_sdbSizer3.Realize()

        sbSizer1.Add(m_sdbSizer3, 1, wx.EXPAND, 5)

        self.SetSizer(sbSizer1)
        self.Layout()

        self.Centre(wx.BOTH)
        self.Show()
        self.Fit()

    def __del__(self):
        pass


if __name__ == '__main__':
    app = wx.App()
    MyFrame1(None)
    app.MainLoop()
