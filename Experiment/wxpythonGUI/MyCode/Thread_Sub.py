# encoding=utf-8
import json
import time
import copy
import os
import wx
import numpy as np
import pandas as pd

from AutoDailyOpt.Debug_Sub import debug_print_txt
from AutoDailyOpt.Sub import cal_rsv_rank, judge_single_stk
from AutoDailyOpt.p_diff_ratio_last import RSV_Record, MACD_min_last
from Config.AutoGenerateConfigFile import data_dir
from Config.Sub import read_config, dict_stk_list
from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ
from Experiment.CornerDetectAndAutoEmail.Sub import add_stk_index_to_df
from Experiment.MiddlePeriodLevelCheck.Demo1 import update_middle_period_hour_data, check_single_stk_middle_level

from Experiment.wxpythonGUI.MyCode.Data_Pro_Sub import get_pic_dict
from Experiment.wxpythonGUI.MyCode.note_string import note_init_pic, \
    note_day_analysis, note_sar_inflection_point
from SDK.Gen_Stk_Pic_Sub import gen_hour_macd_pic_wx, gen_day_pic_wx, gen_w_m_macd_pic_wx, gen_idx_pic_wx, \
    gen_hour_macd_values, gen_hour_index_pic_wx, set_background_color
from SDK.MyTimeOPT import get_current_datetime_str, add_date_str, get_current_date_str
from DataSource.auth_info import *

# 定义事件id
INIT_CPT_ID = wx.NewIdRef(count=1)
HOUR_UPDATE_ID = wx.NewIdRef(count=1)

MSG_UPDATE_ID_A = wx.NewIdRef(count=1)
MSG_UPDATE_ID_S = wx.NewIdRef(count=1)

NOTE_UPDATE_ID_A = wx.NewIdRef(count=1)
NOTE_UPDATE_ID_S = wx.NewIdRef(count=1)

LAST_TIME_UPDATE_ID = wx.NewIdRef(count=1)

FLASH_WINDOW_ID = wx.NewIdRef(count=1)


def get_t_now():
    r = get_current_datetime_str()
    h, m, s = r.split(' ')[1].split(':')
    return int(h + m)


# 线程全局参数
last_upt_t = get_t_now()


def change_font_color(msg_str):
    """
    根据字符串内所含的字符的情况，对字符进行颜色调整，
    按照先前制定的规则，如果要修改颜色，需要将原先的字符串格式外面包一层，编程tuple格式
    即：
    ('r', msg_str)
    这种格式！r表示红色
    :param msg_str:
    :return:
    """

    # 首先判断是否为字符串格式，非字符串格式直接返回
    if isinstance(msg_str, str):

        if ('触发卖出网格' in msg_str) | ('上涨' in msg_str):
            return 'r', msg_str

        elif ('触发买入网格' in msg_str) | ('下跌' in msg_str):
            return 'g', msg_str

        else:
            return msg_str
    else:
        return msg_str


def timer_update_pic(kind):

    """
    在计时器中调用，用于更新小时图片
    :param kind:
    h:小时
    d:天
    wm:周、月
    idx: 指数
    :return:

    返回的图片应该 执行page和行号，便于更新！
    以多层字典的方式返回结果，第一层区分page，第二层区分行号！
    """
    r_dic = {
        'Index': {},
        'Buy': {},
        'Concerned': {}
    }
    dict_stk_hour = copy.deepcopy(dict_stk_list)
    for page in dict_stk_hour.keys():
        for stk_info in dict_stk_list[page]:
            stk = stk_info[1]
            if kind is 'h':
                r_dic[page][stk] = (stk_info[0], gen_hour_macd_pic_wx(stk))
            elif kind is 'h_idx':
                r_dic[page][stk] = (stk_info[0], gen_hour_index_pic_wx(stk, debug=True))
            elif kind is 'd':
                r_dic[page][stk] = (stk_info[0], gen_day_pic_wx(stk))
            elif kind is 'wm':
                r_dic[page][stk] = (stk_info[0], gen_w_m_macd_pic_wx(stk))
            elif kind is 'idx':
                r_dic[page][stk] = (stk_info[0], gen_idx_pic_wx(stk))

    # 汇总返回
    return r_dic


def check_single_stk_hour_idx_wx(stk_code, source='jq', debug=False):
    """
    打印常用指标
    """
    stk_df = get_k_data_JQ(stk_code, count=120,
                          end_date=add_date_str(get_current_date_str(), 1), freq='30m')

    # 按升序排序
    stk_df = stk_df.sort_values(by='datetime', ascending=True)

    """
    增加指标

    'RSI5', 'RSI12', 'RSI30'
    'SAR'
    'slowk', 'slowd'
    'upper', 'middle', 'lower' 
    'MOM'
    """
    # 删除volume为空值的情况！
    stk_df = stk_df.loc[stk_df.apply(lambda x: not (int(x['volume']) == 0), axis=1), :]

    # 计算index
    stk_df = add_stk_index_to_df(stk_df).tail(60)

    result_analysis = []

    # 检查SAR
    sar_tail_origin = stk_df.tail(2)
    sar_tail = sar_tail_origin.copy()
    sar_tail['compare'] = sar_tail_origin.apply(lambda x: x['SAR'] - x['close'], axis=1)

    if sar_tail.head(1)['compare'].values[0] * sar_tail.tail(1)['compare'].values[0] < 0:
        if sar_tail.tail(1)['SAR'].values[0] < sar_tail.tail(1)['close'].values[0]:
            title_tmp = stk_code + ' ' + code2name(stk_code) + ' 注意 SAR 指标翻转，后续数小时可能上涨！'
            result_analysis.append(title_tmp)
            set_background_color(bc='b_r')
        else:
            title_tmp = stk_code + ' ' + code2name(stk_code) + ' 注意 SAR 指标翻转，后续数小时可能下跌！'
            result_analysis.append(title_tmp)

    # 打印过程日志
    if debug:

        txt_name = 'hour_index'

        # 打印时间
        debug_print_txt(txt_name, stk_code, '时间：' + get_current_datetime_str() + '\n\n')

        # 打印原始数据
        debug_print_txt(txt_name, stk_code, stk_df.to_string() + '\n\n')

        # 打印结果
        debug_print_txt(txt_name, stk_code, '结果：\n' + str(result_analysis) + '\n\n')

    return result_analysis


def check_single_stk_hour_macd_wx(stk_code, source='jq'):

    df_30, df_60 = gen_hour_macd_values(stk_code, source=source, title='')

    l_60 = df_60.tail(3)['MACD'].values
    l_30 = df_30.tail(3)['MACD'].values

    if l_60[1] == np.min(l_60):

        title_str = '60分钟开始上涨'
        sts = 1
    elif l_60[1] == np.max(l_60):
        title_str = '60分钟开始下跌'
        sts = 2
    elif l_30[1] == np.max(l_30):
        title_str = '30分钟开始下跌'
        sts = 3
    elif l_30[1] == np.min(l_30):
        title_str = '30分钟开始上涨'
        sts = 4
    else:
        title_str = '当前无拐点'
        sts = 0

    # 避免重复发图！
    if stk_code in MACD_min_last.keys():
        if MACD_min_last[stk_code] != sts:
            send_pic = True
            MACD_min_last[stk_code] = sts
        else:
            send_pic = False
    else:
        send_pic = True
        MACD_min_last[stk_code] = sts

    if send_pic & (sts != 0):
        return code2name(stk_code) + '-' + title_str + '\n'
    else:
        return ''


def is_in_trade_time():
    """
    判断是否在交易时间，即
    09:30~11:30
    13:00~15:00

    :return:
    """
    r = get_current_datetime_str()
    h, m, s = r.split(' ')[1].split(':')
    t = int(h + m)
    if ((t > 930) & (t < 1130)) | ((t > 1300) & (t < 1500)):
        return True
    else:
        return False


def is_time_h_macd_update(last_upt_t):
    """
    判断是否需要更新小时macd图
    选择在
    10:00,10:30,11:00,11:30,13:00,13:30,14:00,14:30,15:00
    等几个时间点更新图片
    :param: last_upt_t 上次更新时间
    :return:
    """
    t_pot = [935, 1005, 1035, 1105, 1135, 1335, 1405, 1435, 1505]
    t = get_t_now()

    r_judge = [(t > x) & (last_upt_t < x) for x in t_pot]

    if True in r_judge:
        return True, t
    else:
        return False, last_upt_t


def check_stk_list_middle_level(stk_list):
    """
    检测一系列stk的中期水平
    :param stk_list:
    :param threshold:
    :return:
    """
    if not os.path.exists(data_dir+'middlePeriodHourData.json'):
        update_middle_period_hour_data()

    # 读取历史小时数据
    with open(data_dir+'middlePeriodHourData.json', 'r') as f:
        dict = json.load(f)

    r = [(x, (1-check_single_stk_middle_level(x, dict)/100)*100) for x in list(set(stk_list))]
    r_df = pd.DataFrame(data=r, columns=['code', 'level_value'])
    r_df['name'] = r_df.apply(lambda x: code2name(x['code']), axis=1)
    r_df_sort = r_df.sort_values(by='level_value', ascending=True).head(12)
    r_df_sort['level'] = r_df_sort.apply(lambda x: '%0.2f' % x['level_value'] + '%', axis=1)

    r_df_sort = r_df_sort.loc[:, ['name', 'level']].reset_index(drop=True)

    return r_df_sort


def update_rsv_record(self):
    try:
        code_list = list(set(read_config()['buy_stk'] + read_config()['concerned_stk'] + read_config()['index_stk']))

        # global  RSV_Record
        for stk in code_list:
            RSV_Record[stk] = cal_rsv_rank(stk, 5) / 100

    except Exception as e:
        print(str(e))
        self.p_ctrl.m_textCtrlMsg.AppendText('RSV数据更新失败！原因：\n' + str(e) + '\n')


def on_timer_ctrl(win, debug=False):

    """
    控制台定时器响应函数
    :return:
    """

    # 清屏
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_S, data='检测时间：' + get_current_datetime_str() + '\n\n'))

    # 不在交易时间不使能定时器
    if not is_in_trade_time():
        wx.PostEvent(win, ResultEvent(
            id=MSG_UPDATE_ID_A,
            data='控制台定时器：当前不属于交易时间！\n'))

        return

    buy_stk_list = list(set(read_config()['buy_stk'] + read_config()['index_stk']))

    if debug:
        print('OnTimerCtrl_4')

    # 局部变量
    note_list = []

    # 对stk进行检查
    for stk in buy_stk_list:
        str_gui = judge_single_stk(stk_code=stk, stk_amount_last=400, qq='', gui=True, debug=True)

        if len(str_gui['note']):
            note_list.append(str_gui['note'])

        # 打印流水信息
        if len(str_gui['msg']):
            wx.PostEvent(win, ResultEvent(
                id=MSG_UPDATE_ID_A,
                data=str_gui['msg']))

    # 根据情况打印提示信息，并闪动
    if len(note_list):

        # 清屏
        wx.PostEvent(win, ResultEvent(
            id=NOTE_UPDATE_ID_S,
            data='检测时间：' + get_current_datetime_str() + '\n\n'))

        # 打印提示
        for note in note_list:
            wx.PostEvent(win, ResultEvent(
                id=NOTE_UPDATE_ID_A,
                data=change_font_color(note)))

        # 闪动图标提醒
        wx.PostEvent(win, ResultEvent(
            id=FLASH_WINDOW_ID,
            data=None))


def timer_work_thread(win, debug=False):

    # 更新rsv，将更新rsv的工作放入线程中，
    # 便于快速出GUI，也可以避免多次链接jq数据源
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='正在初始化RSV值...\n'))
    update_rsv_record(win)

    # 进行图片初始化并打印提示
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='正在初始化图片...\n'))
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data=note_init_pic))

    # 更新图片及打印分析结果
    r = get_pic_dict()
    wx.PostEvent(win, ResultEvent(id=INIT_CPT_ID, data=r[0]))
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='图片初始化完成！\n'))

    # 向提示框打印日线判断提示
    wx.PostEvent(win, ResultEvent(
        id=NOTE_UPDATE_ID_A,
        data=change_font_color(note_day_analysis)))

    if len(r[1]) > 0:

        # 向提示框打印提示
        for note_str in r[1]:
            wx.PostEvent(win, ResultEvent(
                id=NOTE_UPDATE_ID_A,
                data=change_font_color(note_str + '\n')))

        # 闪烁窗口
        wx.PostEvent(win, ResultEvent(id=FLASH_WINDOW_ID, data=None))

        # 延时
        time.sleep(30)

    while True:

        # 调用半小时图片更新函数
        on_timer_pic(win, debug)
        time.sleep(15)

        # 调用控制台处理函数
        on_timer_ctrl(win, debug)
        time.sleep(15)


def on_timer_pic(win, debug=False):
    """
    图片定时器响应函数
    :return:
    """
    global last_upt_t
    upt_flag, last_upt_t = is_time_h_macd_update(last_upt_t)
    wx.PostEvent(win, ResultEvent(id=LAST_TIME_UPDATE_ID, data=last_upt_t))

    if not upt_flag:
        wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='图片更新定时器：“小时图片”更新时间点未到！\n'))
        return

    # 清屏
    wx.PostEvent(win, ResultEvent(id=NOTE_UPDATE_ID_S, data='检测时间：' + get_current_datetime_str() + '\n\n'))

    # 生成更新的图片
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='开始更新小时图片...\n'))
    pic_dict = {'h_macd': timer_update_pic('h'), 'h_idx': timer_update_pic('h_idx')}
    wx.PostEvent(win, ResultEvent(id=HOUR_UPDATE_ID, data=pic_dict))
    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='小时图片更新完成！\n'))

    # 中期水平检测
    # wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='开始“中期水平检测”...！\n'))
    # df_level = check_stk_list_middle_level(list(set(readConfig()['buy_stk'] + readConfig()['concerned_stk'])))
    # wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='“中期水平检测”完成！\n'))
    # wx.PostEvent(win, ResultEvent(id=NOTE_UPDATE_ID_A, data=str(df_level) + '\n\n'))
    # wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data=note_middle_rank))

    # 拐点检测
    window_flash_flag = False
    for stk in list(set(read_config()['buy_stk'] + read_config()['concerned_stk'] + read_config()['index_stk'])):
        hour_idx_str = check_single_stk_hour_idx_wx(stk, source='jq', debug=True)
        if len(hour_idx_str):
            window_flash_flag = True
            for str_tmp in hour_idx_str:
                wx.PostEvent(win, ResultEvent(id=NOTE_UPDATE_ID_A, data=change_font_color(str_tmp)))

    # 窗口闪烁
    if window_flash_flag:
        wx.PostEvent(win, ResultEvent(id=FLASH_WINDOW_ID, data=None))

    wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data=note_sar_inflection_point))


# def updateRSVRecord():
#     try:
#         code_list = list(set(readConfig()['buy_stk'] + readConfig()['concerned_stk'] + readConfig()['index_stk']))
#
#         # global  RSV_Record
#         for stk in code_list:
#             RSV_Record[stk] = calRSVRank(stk, 5)

class ResultEvent(wx.PyEvent):
    """
    事件类
    """
    def __init__(self, id, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(id)
        self.data = data

