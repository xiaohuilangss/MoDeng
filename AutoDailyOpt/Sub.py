# encoding=utf-8

"""
常用定时控制中的子函数
"""
import math
import threading
from pprint import pprint

from AutoDailyOpt.p_diff_ratio_last import RSV_Record, p_diff_ratio_last_dic
from Config.AutoGenerateConfigFile import data_dir
from Config.AutoStkConfig import rootPath
import json
import os
import pandas as pd
import numpy as np

from Config.Sub import read_config, write_config
from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_current_price_JQ, get_k_data_JQ
from Experiment.RelativeRank.Sub import sendHourMACDToQQ
from Experiment.Reseau.StdForReseau.Sub import get_single_stk_reseau
from Global_Value.file_dir import json_file_url, opt_record, opt_record_file_url
from Global_Value.thread_lock import opt_record_lock, opt_lock

from SDK.MyTimeOPT import get_current_date_str, get_current_datetime_str
from SendMsgByQQ.QQGUI import send_qq

"""
F:\MYAI\Code\master\My_Quant\AutoDailyOpt\LocalRecord
"""
# last_p_file_url = rootPath + '\AutoDailyOpt\LocalRecord\last_p.json'
# json_file_url = data_dir + '\last_p.json'
# opt_record_file_url = data_dir + '\opt_record.json'
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


def read_opt_json(stk_code, json_file_url_):
	
	if opt_record_lock.acquire():

		try:
			if os.path.exists(json_file_url_):
				with open(json_file_url_, 'r') as f:
					json_p = json.load(f)
				if stk_code in json_p.keys():
					return json_p[stk_code]
				else:
					return {}
			else:
				return {}
		except Exception as e:
			pass
		finally:
			opt_record_lock.release()

	
def set_opt_json_threshold_satisfied_flag(json_file_url, stk_code, value=True):
	if os.path.exists(json_file_url):
		with open(json_file_url, 'r') as f:
			json_p = json.load(f)
			
		if stk_code in json_p.keys():
			json_p[stk_code]['threshold_satisfied_flag'] = value
			
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

	print('函数 saveLastP：' + stk_code + '历史price发生修改！修正为'+str(p))


def cal_rsv_rank_sub(df, m):
	"""
	独立这一函数，主要是为了huice
	:param df:
	:param m:
	:return:
	"""

	# 移动平均线+RSV（未成熟随机值）
	df['low_M'+str(m)] = df['low'].rolling(window=m).mean()
	df['high_M'+str(m)] = df['high'].rolling(window=m).mean()
	df['close_M'+str(m)] = df['close'].rolling(window=m).mean()

	for idx in df.index:
		if (df.loc[idx, 'high_M'+str(m)] - df.loc[idx, 'low_M'+str(m)] ==0) | (df.loc[idx, 'close_M'+str(m)] - df.loc[idx, 'low_M'+str(m)] ==0):
			df.loc[idx, 'RSV'] = 0.5

		else:
			df.loc[idx, 'RSV'] = (df.loc[idx, 'close_M'+str(m)] - df.loc[idx, 'low_M'+str(m)])/(df.loc[idx, 'high_M'+str(m)] - df.loc[idx, 'low_M'+str(m)])

	return df.tail(1)['RSV'].values[0]


def cal_rsv_rank(stk_code, m_days, history_length=400):

	df = get_k_data_JQ(stk_code, count=history_length, end_date=get_current_date_str())

	return cal_rsv_rank_sub(df, m_days)


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


def judge_single_stk_sub(reseau, rsv, current_price, stk_price_last, min_reseau, sar_diff, sar_diff_day):

	# 实时计算价差，用于“波动提示”和“最小网格限制”
	price_diff = current_price - stk_price_last
	price_diff_ratio = price_diff/stk_price_last

	# 调节 buy 和 sale 的 threshold
	thh_sale = reseau*2*rsv
	thh_buy = reseau * 2 * (1-rsv)

	# if (min_reseau > math.fabs(thh_sale / stk_price_last)) | (min_reseau > math.fabs(thh_buy / stk_price_last)):
	# if ((rsv < 0.3) | (rsv > 0.7)) | (math.fabs((current_price - stk_price_last)/stk_price_last) < 0.013):
	# 	return 0, '未触及reseau'
	# elif (price_diff > thh_sale) & (sar_diff >= 0) & (sar_diff_day >= 0):
	# 	return 1, 'time to sale'
	# elif (price_diff < -thh_buy) & (sar_diff <= 0) & (sar_diff_day <= 0):
	# 	return 2, 'time to buy'
	# else:
	# 	return -1, 'no opt'
	
	if math.fabs((current_price - stk_price_last)/stk_price_last) < min_reseau:
		return 0, '未触及reseau'
	elif (sar_diff >= 0) & (sar_diff_day >= 0) & ((current_price - stk_price_last)/stk_price_last > min_reseau):
		return 1, 'time to sale'
	elif (sar_diff <= 0) & (sar_diff_day <= 0) & ((current_price - stk_price_last)/stk_price_last < -min_reseau):
		return 2, 'time to buy'
	else:
		return -1, 'no opt'


def judge_single_stk(stk_code, stk_amount_last, qq, debug=False, gui=False):
	"""
	
	:param stk_code:
	:param stk_amount_last:
	:param qq:
	:param debug:
	:param gui:
	:return:
	"""

	""" 变量声明 """
	str_gui = {
		'note': '',
		'msg': ''
	}

	""" 'n':无操作，'b', 's' """
	opt_now = 'n'

	""" ==== 获取该stk的实时价格,如果是大盘指数，使用聚宽数据，否则有限使用tushare ==== """
	try:
		current_price = get_current_price_JQ(stk_code)
	except:
		str_gui = myPrint(str_gui, stk_code + '获取实时price失败！', method={True: 'gm', False: 'n'}[gui])
		return str_gui

	""" ==================== 获取上次price ==================== """
	opt_json_stk = read_opt_json(stk_code, opt_record_file_url)
	
	# 如果没有相应的json文件，不进行判断，直接返回
	if opt_json_stk == {}:
		print('函数 judge_single_stk：' + code2name(stk_code) + '没有历史操作记录，不进行阈值判断！')
		return str_gui
	
	if len(opt_json_stk['b_opt']) == 0:
		print('函数 judge_single_stk：' + code2name(stk_code) + '没有历史操作记录，不进行阈值判断！')
		return str_gui
	
	# 读取上次p和b操作中的最小p，备用
	last_p = opt_json_stk['p_last']
	b_p_min = np.min([x['p'] for x in opt_json_stk['b_opt']])
	
	""" =========== 实时计算价差，用于“波动提示”和“最小网格限制” ======== """
	if debug:
		str_gui = myPrint(
			str_gui,
			'\n\n' + stk_code + ':\np_now:' + str(current_price) + '\np_last:' + str(
				last_p) + '\np_change_ratio:' + '',
			method={True: 'gm', False: 'n'}[gui])

	""" ========== 排除获取的价格为0的情况，此种情况可能是stop或者时间未到 ========== """
	if current_price == 0.0:

		str_gui = myPrint(
			str_gui,
			stk_code + 'price==0.0! 返回！',
			method={True: 'gm', False: 'n'}[gui])

		return str_gui

	buy_amount = math.floor((money_each_opt/current_price)/100)*100

	""" 实时计算网格大小 """
	earn_threshold_unit = get_single_stk_reseau(stk_code)

	""" 调节 buy 和 sale 的threshold """
	if stk_code in RSV_Record.keys():
		thh_sale = earn_threshold_unit*2*RSV_Record[stk_code]
		thh_buy = earn_threshold_unit * 2 * (1-RSV_Record[stk_code])
	else:
		RSV_Record[stk_code] = cal_rsv_rank(stk_code, 5) / 100
		thh_sale = earn_threshold_unit*2*RSV_Record[stk_code]
		thh_buy = earn_threshold_unit * 2 * (1-RSV_Record[stk_code])

	""" 将操作日志保存到全局变量中 """
	if opt_lock.acquire():
		try:
			opt_record.append({
				'stk_code': stk_code,
				'p_now': current_price,
				'sale_reseau': thh_sale,
				'buy_reseau': thh_buy,
				'p_last': last_p,
				# 'opt': opt,
				'date_time': get_current_datetime_str()
			})

		except Exception as e:
			print('函数 JudgeSingleStk:写入操作记录失败！原因：\n' + str(e))

		finally:
			opt_lock.release()

	if debug:
		print('函数 JudgeSingleStk:' + stk_code + '定时处理完成后，操作记录为：\n')
		pprint(opt_record)

	""" ==================== 判断波动是否满足“最小网格限制” ================= """
	"""
	config_json = read_config()
	if not ('minReseau' in config_json.keys()):
		write_config('minReseau', 0.02)
		min_reseau = 0.02
	else:
		min_reseau = config_json['minReseau']

	if (min_reseau > math.fabs(thh_sale/last_p)) | (min_reseau > math.fabs(thh_buy/last_p)):

		str_tmp = stk_code + ' ' + code2name(stk_code) + ':\n'\
			+ 'buy相对宽度：%0.3f \n' % (thh_buy/last_p) +\
			  'sale相对宽度：%0.3f\n' % (thh_sale/last_p) +\
			  '设定波动阈值：%0.3f\n' % min_reseau +\
			  '波动未达到最小网格宽度，返回！'

		str_gui = myPrint(
			str_gui,
			str_tmp,
			method={True: 'gm', False: 'n'}[gui])
		return str_gui
	
	if debug:

		str_gui = myPrint(
			str_gui,
			stk_code +
			':\np_change:' + str(price_diff * stk_amount_last) +
			'\nthreshold:' + str(earn_threshold_unit) +
			'\nthh_sale:' + str(thh_sale) +
			'\nthh_buy:' + str(thh_buy),
			method={True: 'gm', False: 'n'}[gui])
	"""
	
	""" ============================= 判断是否超过阈值,进行bs操作 ============================== """
	pcr = read_config()['pcr']
	if (current_price - b_p_min > thh_sale) & ((current_price - b_p_min)/b_p_min >= pcr):

		str_temp = "触发卖出网格！可以考虑卖出！ " + stk_code + code2name(stk_code) +\
				'\nAmount:' + str(stk_amount_last) +\
				'\n当前价格:' + str(current_price) +\
				'\n上次买入价格:' + str(b_p_min) +\
				'\n买入网格大小:' + '%0.3f' % thh_buy +\
				'\n卖出网格大小:' + '%0.3f' % thh_sale +\
				'\n最小操作幅度:' + '%0.3f' % pcr

		str_gui = myPrint(
			str_gui,
			str_temp,
			method={True: 'gn', False: 'qq'}[gui],
			towho=qq)

		if not gui:
			sendHourMACDToQQ(stk_code, qq, source='jq')

	elif (current_price - last_p < -thh_buy) & ((current_price - last_p)/b_p_min <= -pcr):

		str_temp = "触发买入网格！可以考虑买入！" + stk_code + code2name(stk_code) +\
				'\nAmount:' + str(buy_amount) +\
				'\n当前价格:' + str(current_price) +\
				'\n上次价格:' + str(last_p) +\
				'\n买入网格大小:' + '%0.2f' % thh_buy +\
				'\n卖出网格大小:' + '%0.2f' % thh_sale +\
				'\n最小操作幅度:' + '%0.3f' % pcr

		str_gui = myPrint(
			str_gui,
			str_temp,
			method={True: 'gn', False: 'qq'}[gui],
			towho=qq)

		if not gui:
			sendHourMACDToQQ(stk_code, qq, source='jq')

	else:
		str_gui = myPrint(
			str_gui,
			stk_code + ':未触发任何警戒线！',
			method={True: 'gm', False: 'n'}[gui])

		opt = 'n'

	""" ========================== 波动检测 =========================== """
	change_flag, str_gui = judge_p_change_ratio(stk_code, (current_price-last_p)/last_p, str_gui=str_gui, gui=gui)
	if change_flag:

		str_temp = "波动推送! " + stk_code + code2name(stk_code) +\
				'\nAmount:' + str(buy_amount) +\
				'\n当前价格:' + str(current_price) +\
				'\n上次价格:' + str(last_p) +\
				'\n买入网格大小:' + '%0.2f' % thh_buy +\
				'\n卖出网格大小:' + '%0.2f' % thh_sale

		str_gui = myPrint(
			str_gui,
			str_temp,
			method={True: 'gn', False: 'qq'}[gui],
			towho=qq)

		if not gui:
			sendHourMACDToQQ(stk_code, qq, source='jq')

	return str_gui


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
		if math.fabs(price_diff_ratio - p_diff_ratio_last_dic[stk_code])*100 > read_config()['pcr']:

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
	
	r = read_opt_json('000333', opt_record_file_url)['threshold_satisfied_flag']
	
	r = set_opt_json_threshold_satisfied_flag(opt_record_file_url, '000333', value=False)
	
	from DataSource.auth_info import *
	cal_rsv_rank('300183', 5, history_length=400)
	saveLastP('000001', 25)

	end = 0
