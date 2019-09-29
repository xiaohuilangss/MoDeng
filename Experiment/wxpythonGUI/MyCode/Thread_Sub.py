# encoding=utf-8

import time
from threading import *
import wx

# Button definitions
from AutoDailyOpt.Sub import calRSVRank
from AutoDailyOpt.p_diff_ratio_last import RSV_Record
from Config.Sub import readConfig

from Experiment.wxpythonGUI.MyCode.Data_Pro_Sub import get_pic_dict


def updateRSVRecord():
    try:
        code_list = list(set(readConfig()['buy_stk'] + readConfig()['concerned_stk'] + readConfig()['index_stk']))

        # global  RSV_Record
        for stk in code_list:
            RSV_Record[stk] = calRSVRank(stk, 5)/100

    except Exception as e:
        print(str(e))
        # self.p_ctrl.m_textCtrlMsg.AppendText('RSV数据更新失败！原因：\n' + str(e) + '\n')


class ResultEvent(wx.PyEvent):
    """
    事件类
    """
    def __init__(self, id, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(id)
        self.data = data

