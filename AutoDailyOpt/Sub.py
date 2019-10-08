# encoding=utf-8

"""
常用定时控制中的子函数
"""
import math

from AutoDailyOpt.p_diff_ratio_last import RSV_Record, p_diff_ratio_last_dic
from Config.AutoGenerateConfigFile import data_dir
from Config.AutoStkConfig import rootPath
import json
import os

from Config.Sub import readConfig
from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_current_price_JQ, get_RT_price, get_k_data_JQ
from Experiment.RelativeRank.Sub import sendHourMACDToQQ
from Experiment.Reseau.StdForReseau.Sub import getSigleStkReseau
from SDK.MyTimeOPT import get_current_date_str
from SendMsgByQQ.QQGUI import send_qq

"""
F:\MYAI\Code\master\My_Quant\AutoDailyOpt\LocalRecord
"""
# last_p_file_url = rootPath + '\AutoDailyOpt\LocalRecord\last_p.json'
last_p_file_url = data_dir + '\last_p.json'

money_each_opt = 5000


def myPrint(str_gui, str_temp, method='n', towho=''):
    """

    :param gui:
    :param str_gui:
    :param method:
    :param towho:
    :return:
    """
    if method is 'n':
        print(str_temp)

    elif method is 'gm':
        str_gui['msg'] = str_gui['msg'] + str_temp + '\n\n'

    elif method is 'gn':
        str_gui['note'] = str_gui['note'] + str_temp + '\n\n'

    elif method is 'qq':
        send_qq(towho, str_temp)

    return str_gui


def readLastP(stk_code):

    if os.path.exists(last_p_file_url):
        with open(last_p_file_url, 'r') as f:
            json_p = json.load(f)

        if stk_code in json_p.keys():
            return json_p[stk_code]
        else:
            return -1
    else:
        with open(last_p_file_url, 'w') as f:
            json.dump(obj={}, fp=f)


def saveLastP(stk_code, p):
    with open(last_p_file_url, 'r') as f:
        json_p = json.load(f)

    json_p[stk_code] = p

    with open(last_p_file_url, 'w') as f:
        json.dump(obj=json_p, fp=f)

    print('函数 saveLastP：' + stk_code + '历史price发生修改！修正为'+str(p))


def calRSVRank(stk_code, Mdays, history_length=400):

    df = get_k_data_JQ(stk_code, count=history_length, end_date=get_current_date_str())

    # 移动平均线+RSV（未成熟随机值）
    M = Mdays

    df['low_M'+str(M)] = df['low'].rolling(window=M).mean()
    df['high_M'+str(M)] = df['high'].rolling(window=M).mean()
    df['close_M'+str(M)] = df['close'].rolling(window=M).mean()

    for idx in df.index:
        if (df.loc[idx, 'high_M'+str(M)] - df.loc[idx, 'low_M'+str(M)] ==0) | (df.loc[idx, 'close_M'+str(M)] - df.loc[idx, 'low_M'+str(M)] ==0):
            df.loc[idx, 'RSV'] = 0.5

        else:
            df.loc[idx, 'RSV'] = (df.loc[idx, 'close_M'+str(M)] - df.loc[idx, 'low_M'+str(M)])/(df.loc[idx, 'high_M'+str(M)] - df.loc[idx, 'low_M'+str(M)])

    # df['RSV'] = df.apply(lambda x: (x['close_M'+str(M)] - x['low_M'+str(M)])/(x['high_M'+str(M)] - x['low_M'+str(M)]), axis=1)

    return df.tail(1)['RSV'].values[0]


def JudgeSingleStk(stk_code, stk_amount_last,  qq, debug=False, gui=False):

    str_gui = {
        'note': '',
        'msg': ''
    }

    # 获取该stk的实时价格,如果是大盘指数，使用聚宽数据，否则有限使用tushare
    if stk_code in ['sh', 'sz', 'cyb']:
        current_price = get_current_price_JQ(stk_code)
    else:
        try:
            current_price = get_RT_price(stk_code, source='ts')
        except:

            str_gui = myPrint(str_gui, stk_code + '获取实时price失败！', method={True:'gm', False:'n'}[gui])
            return str_gui

    # 获取上次price
    stk_price_last = readLastP(stk_code)
    if stk_price_last < 0:
        saveLastP(stk_code, current_price)
        stk_price_last = current_price

    # 实时计算价差
    price_diff = current_price - stk_price_last
    price_diff_ratio = price_diff/stk_price_last

    if debug:
        str_gui = myPrint(
            str_gui,
            '\n\n' + stk_code + ':\np_now:' + str(current_price) + '\np_last:' + str(
                stk_price_last) + '\np_change_ratio:' + str(price_diff_ratio),
            method={True: 'gm', False: 'n'}[gui])

    if current_price == 0.0:

        str_gui = myPrint(
            str_gui,
            stk_code + 'price==0.0! 返回！',
            method={True: 'gm', False: 'n'}[gui])

        return str_gui

    buy_amount = math.floor((money_each_opt/current_price)/100)*100

    # 实时计算网格大小
    earn_threshold_unit = getSigleStkReseau(stk_code)

    # 调节 buy 和 sale 的threshold
    if stk_code in RSV_Record.keys():
        thh_sale = earn_threshold_unit*2*RSV_Record[stk_code]
        thh_buy = earn_threshold_unit * 2 * (1-RSV_Record[stk_code])
    else:
        RSV_Record[stk_code] = calRSVRank(stk_code, 5)/100
        thh_sale = earn_threshold_unit*2*RSV_Record[stk_code]
        thh_buy = earn_threshold_unit * 2 * (1-RSV_Record[stk_code])

    # 计算其离心度分数
    try:
        # rank9, _, _, _ = calRealtimeRankWithGlobal(stk_code=stk_code)
        rank9 = -1
    except:
        rank9 = -1

    if debug:

        str_gui = myPrint(
            str_gui,
            stk_code +
            ':\np_change:' + str(price_diff * stk_amount_last) +
            '\nthreshold:' + str(earn_threshold_unit) +
            '\nthh_sale:' + str(thh_sale) +
            '\nthh_buy:' + str(thh_buy),
            method={True: 'gm', False: 'n'}[gui])

    if price_diff > thh_sale:
        # if JudgePChangeRatio(stk_code, price_diff_ratio):

        str_temp = "触发卖出网格！可以考虑卖出！ "+stk_code + code2name(stk_code) +\
                '\nAmount:' + str(stk_amount_last) +\
                '\n当前价格:' + str(current_price) +\
                '\n上次价格:' + str(stk_price_last) +\
                '\n买入网格大小:' + '%0.2f' % thh_buy +\
                '\n卖出网格大小:' + '%0.2f' % thh_sale
                # '\nM9_rank:' + str('%0.2f' % rank9)

        str_gui = myPrint(
            str_gui,
            str_temp,
            method={True: 'gn', False: 'qq'}[gui],
            towho=qq)

        if not gui:
            sendHourMACDToQQ(stk_code, qq, source='jq')

        # 更新本地价格
        saveLastP(stk_code, current_price)

    elif price_diff < -thh_buy:

        str_temp = "触发买入网格！可以考虑买入！" + stk_code + code2name(stk_code) +\
                '\nAmount:' + str(buy_amount) +\
                '\n当前价格:' + str(current_price) +\
                '\n上次价格:' + str(stk_price_last) +\
                '\n买入网格大小:' + '%0.2f' % thh_buy +\
                '\n卖出网格大小:' + '%0.2f' % thh_sale
                # '\nM9_rank:' + str('%0.2f' % rank9)

        str_gui = myPrint(
            str_gui,
            str_temp,
            method={True: 'gn', False: 'qq'}[gui],
            towho=qq)

        if not gui:
            sendHourMACDToQQ(stk_code, qq, source='jq')

        saveLastP(stk_code, current_price)

    else:
        str_gui = myPrint(
            str_gui,
            stk_code + ':未触发任何警戒线！',
            method={True: 'gm', False: 'n'}[gui])

    # 波动检测
    change_flag, str_gui = JudgePChangeRatio(stk_code, price_diff_ratio, str_gui=str_gui, gui=gui)
    if change_flag:

        str_temp = "波动推送! " + stk_code + code2name(stk_code) +\
                '\nAmount:' + str(buy_amount) +\
                '\n当前价格:' + str(current_price) +\
                '\n上次价格:' + str(stk_price_last) +\
                '\n买入网格大小:' + '%0.2f' % thh_buy +\
                '\n卖出网格大小:' + '%0.2f' % thh_sale
                # '\nM9_rank:' + str('%0.2f' % rank9)

        str_gui = myPrint(
            str_gui,
            str_temp,
            method={True: 'gn', False: 'qq'}[gui],
            towho=qq)

        if not gui:
            sendHourMACDToQQ(stk_code, qq, source='jq')

    return str_gui


def JudgePChangeRatio(stk_code, price_diff_ratio, str_gui, debug=True, gui=False):
    """
    判断stk的变化是否达到一定的幅度，以杜绝反复上报
    :param stk_code:
    :return:
    """
    global price_diff_ratio_last_dic
    if debug:
        str_temp = '函数JudgeSingleStk：进入函数！'
        if gui:
            str_gui['msg'] = str_gui['msg'] + str_temp + '\n'
        else:
            print('函数JudgeSingleStk：进入函数！')

    # 变化1个百分点再报，避免重复报
    if stk_code in p_diff_ratio_last_dic.keys():
        if math.fabs(price_diff_ratio - p_diff_ratio_last_dic[stk_code])*100 > readConfig()['pcr']:

            p_diff_ratio_last_dic[stk_code] = price_diff_ratio
            if debug:
                str_temp = '函数JudgeSingleStk：' + str(stk_code) + '价格变化幅度达标，允许推送，并更新振幅记忆！' +\
                      '\np_ratio_now:'+str(price_diff_ratio) +\
                      '\np_ratio_last:'+str(p_diff_ratio_last_dic[stk_code])
                if gui:
                    str_gui['msg'] = str_gui['msg'] + str_temp + '\n'
                else:
                    print(str_temp)

            return True, str_gui
        else:
            str_temp = '函数JudgeSingleStk：' + str(stk_code) + '价格变化幅度不够，不许推送！' +\
                  '\np_ratio_now:' + str(price_diff_ratio) +\
                  '\np_ratio_last:' + str(p_diff_ratio_last_dic[stk_code])
            if gui:
                str_gui['msg'] = str_gui['msg'] + str_temp + '\n'
            else:
                print(str_temp)

            return False, str_gui
    else:
        p_diff_ratio_last_dic[stk_code] = price_diff_ratio
        if debug:
            str_temp = '函数JudgeSingleStk：' + str(stk_code) + '首次运行，允许推送！'
            if gui:
                str_gui['msg'] = str_gui['msg'] + str_temp + '\n'
            else:
                print(str_temp)

        return True, str_gui


if __name__ == '__main__':
    from DataSource.auth_info import *
    calRSVRank('300183', 5, history_length=400)
    saveLastP('000001', 25)
    
    end = 0
