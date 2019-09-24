# encoding=utf-8

import time
from threading import *
import wx

# Button definitions
from AutoDailyOpt.p_diff_ratio_last import RSV_Record
from Config.Sub import readConfig
from Experiment.BOLL.Demo import calRSVRank
from Experiment.wxpythonGUI.MyCode.Data_Pro_Sub import get_pic_dict


def EVT_RESULT(win, func):
    """
    绑定时间与响应函数
    :param win:
    :param func:
    :return:
    """
    win.Connect(-1, -1, EVT_RESULT_ID, func)


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


# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.start()

    def run(self):

        # 初始化工作
        updateRSVRecord()

        # 生成初始化图片
        r = get_pic_dict()
        wx.PostEvent(self._notify_window, ResultEvent(id=INIT_CPT_ID, data=r))


    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

