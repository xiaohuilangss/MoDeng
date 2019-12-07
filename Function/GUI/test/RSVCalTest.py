# encoding=utf-8

"""
本脚本用于测试RSV计算准确性
"""
import wx

from Experiment.GUI.MyCode.Sub import MyFrame, OnTimerCtrl
from DataSource.auth_info import *




app = wx.App()
fm = MyFrame(None, title="V20190919")
fm.updateRSVRecord()
app.MainLoop()


end = 0
