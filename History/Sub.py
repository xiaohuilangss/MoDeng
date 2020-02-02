# encoding=utf-8

"""
常用定时控制中的子函数
"""
import math

from Global_Value.p_diff_ratio_last import p_diff_ratio_last_dic

from Config.Sub import read_config, write_config
from Global_Value.file_dir import json_file_url, opt_record_file_url

"""
F:\MYAI\Code\master\My_Quant\AutoDailyOpt\LocalRecord
"""
# last_p_file_url = rootPath + '\History\LocalRecord\last_p.json'
# json_file_url = data_dir + '\last_p.json'
# opt_record_file_url = data_dir + '\opt_record.json'
money_each_opt = 5000


# def myPrint(str_gui, str_temp, method='n', towho=''):
# 	"""
#
# 	:param gui:
# 	:param str_gui:
# 	:param method:
# 	:param towho:
# 	:return:
# 	"""
# 	if method is 'n':
# 		print(str_temp)
#
# 	elif method is 'gm':
# 		str_gui['msg'] = str_gui['msg'] + str_temp + '\n\n'
#
# 	elif method is 'gn':
# 		str_gui['note'] = str_gui['note'] + str_temp + '\n\n'
#
# 	elif method is 'qq':
# 		send_qq(towho, str_temp)
#
# 	return str_gui


# def read_opt_json(stk_code, json_file_url_):
#
# 	if opt_record_lock.acquire():
#
# 		try:
# 			if os.path.exists(json_file_url_):
# 				with open(json_file_url_, 'r') as f:
# 					json_p = json.load(f)
# 				if stk_code in json_p.keys():
# 					return json_p[stk_code]
# 				else:
# 					return {}
# 			else:
# 				return {}
# 		except Exception as e:
# 			pass
# 		finally:
# 			opt_record_lock.release()


def set_opt_json_threshold_satisfied_flag(json_file_url, stk_code, value=True):
    if os.path.exists(json_file_url):
        with open(json_file_url, 'r') as f:
            json_p = json.load(f)

        if stk_code in json_p.keys():
            json_p[stk_code]['has_flashed_flag'] = value

            # 将数据写入
            with open(json_file_url, 'w') as f:
                json.dump(json_p, f)
            return 0
        else:
            return 1
    else:
        return 2


def readLastP(stk_code):
    if os.path.exists(json_file_url):
        with open(json_file_url, 'r') as f:
            json_p = json.load(f)

        if stk_code in json_p.keys():
            return json_p[stk_code]
        else:
            return -1
    else:
        with open(json_file_url, 'w') as f:
            json.dump(obj={}, fp=f)
            return -1


def saveLastP(stk_code, p):
    with open(json_file_url, 'r') as f:
        json_p = json.load(f)

    json_p[stk_code] = p

    with open(json_file_url, 'w') as f:
        json.dump(obj=json_p, fp=f)

    print('函数 saveLastP：' + stk_code + '历史price发生修改！修正为' + str(p))


def cal_rsv_rank_sub(df, m):
    """
	独立这一函数，主要是为了huice
	:param df:
	:param m:
	:return:
	"""

    # 移动平均线+RSV（未成熟随机值）
    df['low_M' + str(m)] = df['low'].rolling(window=m).mean()
    df['high_M' + str(m)] = df['high'].rolling(window=m).mean()
    df['close_M' + str(m)] = df['close'].rolling(window=m).mean()

    for idx in df.index:
        if (df.loc[idx, 'high_M' + str(m)] - df.loc[idx, 'low_M' + str(m)] == 0) | (
                df.loc[idx, 'close_M' + str(m)] - df.loc[idx, 'low_M' + str(m)] == 0):
            df.loc[idx, 'RSV'] = 0.5

        else:
            df.loc[idx, 'RSV'] = (df.loc[idx, 'close_M' + str(m)] - df.loc[idx, 'low_M' + str(m)]) / (
                    df.loc[idx, 'high_M' + str(m)] - df.loc[idx, 'low_M' + str(m)])

    return df.tail(1)['RSV'].values[0]


# def cal_rsv_rank(stk_code, m_days, history_length=400):
#
# 	df = get_k_data_JQ(stk_code, count=history_length, end_date=get_current_date_str())
#
# 	return cal_rsv_rank_sub(df, m_days)


def getMinReseauSize():
    """
	从配置文件中获取网格的最小宽度，如果没有该字段，则设置默认为2%
	:return:
	"""
    r = read_config()
    if 'minReseau' in r.keys():
        return r['minReseau']
    else:

        write_config('minReseau', 0.02)
        return 0.02




def judge_p_change_ratio(stk_code, price_diff_ratio, str_gui, debug=True, gui=False):
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
        if math.fabs(price_diff_ratio - p_diff_ratio_last_dic[stk_code]) * 100 > read_config()['pcr']:

            p_diff_ratio_last_dic[stk_code] = price_diff_ratio
            if debug:
                str_temp = '函数JudgeSingleStk：' + str(stk_code) + '价格变化幅度达标，允许推送，并更新振幅记忆！' + \
                           '\np_ratio_now:' + str(price_diff_ratio) + \
                           '\np_ratio_last:' + str(p_diff_ratio_last_dic[stk_code])
                if gui:
                    str_gui['msg'] = str_gui['msg'] + str_temp + '\n'
                else:
                    print(str_temp)

            return True, str_gui
        else:
            str_temp = '函数JudgeSingleStk：' + str(stk_code) + '价格变化幅度不够，不许推送！' + \
                       '\np_ratio_now:' + str(price_diff_ratio) + \
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
    r = read_opt_json('000333', opt_record_file_url)['has_flashed_flag']

    r = set_opt_json_threshold_satisfied_flag(opt_record_file_url, '000333', value=False)

    from DataSource.auth_info import *

    cal_rsv_rank('300183', 5, history_length=400)
    saveLastP('000001', 25)

    end = 0
