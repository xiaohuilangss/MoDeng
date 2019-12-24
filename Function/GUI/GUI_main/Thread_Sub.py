# encoding=utf-8

import multiprocessing
multiprocessing.freeze_support()

import pprint
import time

import math
import wx
import numpy as np
import jqdatasdk as jq
import copy
import os
import pandas as pd

from Function.GUI.GUI_main.note_string import note_init_pic, note_sar_inflection_point
from Global_Value.p_diff_ratio_last import MACD_min_last, RSV_Record
from Global_Value.thread_lock import opt_record_lock, opt_lock
from Config.Sub import read_config, dict_stk_list
from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ, get_current_price_JQ, add_stk_index_to_df

from Global_Value.file_dir import opt_record_file_url, hist_pic_dir, opt_record
from SDK.Debug_Sub import debug_print_txt, myPrint
from SDK.Gen_Stk_Pic_Sub import \
	gen_hour_macd_values, set_background_color, gen_hour_macd_pic_local, \
	gen_hour_index_pic_local, gen_day_pic_local, gen_w_m_macd_pic_local, gen_idx_pic_local
from SDK.MyTimeOPT import get_current_datetime_str, add_date_str, get_current_date_str

from DataSource.auth_info import *

# 定义事件id
from SDK.StdForReseau.Sub import get_single_stk_reseau

INIT_CPT_ID = wx.NewIdRef(count=1)
HOUR_UPDATE_ID = wx.NewIdRef(count=1)
DAY_UPDATE_ID = wx.NewIdRef(count=1)

MSG_UPDATE_ID_A = wx.NewIdRef(count=1)
MSG_UPDATE_ID_S = wx.NewIdRef(count=1)

NOTE_UPDATE_ID_A = wx.NewIdRef(count=1)
NOTE_UPDATE_ID_S = wx.NewIdRef(count=1)

LAST_TIME_UPDATE_ID = wx.NewIdRef(count=1)

FLASH_WINDOW_ID = wx.NewIdRef(count=1)

# 定义管道信息编号
INIT_CPT_NUM = 1
HOUR_UPDATE_NUM = 2
DAY_UPDATE_NUM = 3

MSG_UPDATE_NUM_A = 4
MSG_UPDATE_NUM_S = 5

NOTE_UPDATE_NUM_A = 6
NOTE_UPDATE_NUM_S = 7

LAST_TIME_UPDATE_NUM = 8

FLASH_WINDOW_NUM = 9
DAY_ANALYSIS_NUM = 10


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
	
	debug_print_txt('rsv_cal', '', df.to_string(), True)

	for idx in df.index:
		if (df.loc[idx, 'high_M'+str(m)] - df.loc[idx, 'low_M'+str(m)] ==0) | (df.loc[idx, 'close_M'+str(m)] - df.loc[idx, 'low_M'+str(m)] ==0):
			df.loc[idx, 'RSV'] = 0.5
			
			debug_print_txt('rsv_cal', '', '最高点均值-最低点均值=0,近日可能无波动，rsv设置为0.5', True)

		else:
			df.loc[idx, 'RSV'] = (df.loc[idx, 'close_M'+str(m)] - df.loc[idx, 'low_M'+str(m)])/(df.loc[idx, 'high_M'+str(m)] - df.loc[idx, 'low_M'+str(m)])

	return df.tail(1)['RSV'].values[0]


def cal_rsv_rank(stk_code, m_days, history_length=400):

	df = get_k_data_JQ(stk_code, count=history_length, end_date=get_current_date_str())

	debug_print_txt('rsv_cal', '', code2name(stk_code) + '开始计算rsv:', True)
	
	rsv = cal_rsv_rank_sub(df, m_days)
	
	debug_print_txt('rsv_cal', '', '最终rsv：' + '%0.3f' %rsv, True)
	
	return rsv


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


def load_local_pic_for_wx(r_dic_):
	"""
	取图片
	:param kind:
	:param r_dic:
	:return:
	"""
	dict_stk_hour = copy.deepcopy(dict_stk_list)
	for unit in r_dic_:
		r_dic = r_dic_[unit]
		
		# 取值汇总
		for page in dict_stk_hour.keys():
			for stk_info in dict_stk_hour[page]:
				stk = stk_info[1]
				r_dic[page][stk] = (stk_info[0], wx.Image(r_dic[page][stk + '_url'], wx.BITMAP_TYPE_PNG).ConvertToBitmap())
		
	# 汇总返回
	return r_dic_


def gen_kind_pic(kind, pool):
	"""
	造图片，存本地
	:param kind:
	h:小时
	h_idx:小时idx
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
	
	jq_login()
	
	""" 在外部下载需要的数据，防止多进程中重复连接聚宽 """
	for page in dict_stk_hour.keys():
		for stk_info in dict_stk_list[page]:
			stk = stk_info[1]
			if kind is 'h':
				r_dic[page][stk + '_d'] = gen_hour_macd_values(stk)
			elif kind is 'h_idx':
				r_dic[page][stk + '_d'] = gen_hour_macd_values(stk)[0]
			elif kind is 'd':
				r_dic[page][stk + '_d'] = get_k_data_JQ(stk, 400)
			elif kind is 'wm':
				r_dic[page][stk + '_d'] = get_k_data_JQ(stk, count=400, end_date=get_current_date_str()).reset_index()
			elif kind is 'd_idx':
				r_dic[page][stk + '_d'] = get_k_data_JQ(stk, 400)
	jq.logout()
	
	""" 生成pic """
	for page in dict_stk_hour.keys():
		for stk_info in dict_stk_list[page]:
			stk = stk_info[1]
			
			# 保存路径
			save_dir = hist_pic_dir + get_current_date_str() + '/' + stk + kind + '/'
			file_name = get_current_datetime_str()[:-3].replace(':', '').replace(' ', '').replace('-', '') + '.png'
			if not os.path.exists(save_dir):
				os.makedirs(save_dir)
			
			if kind is 'h':
				r_dic[page][stk + '_res'] = pool.apply_async(gen_hour_macd_pic_local, (r_dic[page][stk + '_d'], stk, 'jq', '', save_dir + file_name))
			elif kind is 'h_idx':
				r_dic[page][stk + '_res'] = pool.apply_async(gen_hour_index_pic_local, (r_dic[page][stk + '_d'], stk, save_dir + file_name))
			elif kind is 'd':
				r_dic[page][stk + '_res'] = pool.apply_async(gen_day_pic_local, (r_dic[page][stk + '_d'], stk, save_dir + file_name))
			elif kind is 'wm':
				r_dic[page][stk + '_res'] = pool.apply_async(gen_w_m_macd_pic_local, (r_dic[page][stk + '_d'], stk, save_dir + file_name))
			elif kind is 'd_idx':
				r_dic[page][stk + '_res'] = pool.apply_async(gen_idx_pic_local, (r_dic[page][stk + '_d'], stk, save_dir + file_name))
			
			# 在字典中保存图片路径
			r_dic[page][stk + '_url'] = save_dir + file_name
	
	return r_dic


def get_process_res(dic):
	"""
	解析出进程的返回值
	:param dic:
	:return:
	"""
	for key in dic.keys():
		dic[key] = get_res_sub(dic[key])

	return dic


def clear_data_dic(dic):
	"""
	清理一个字典中的数据
	:param dic:
	:return:
	"""
	
	for key in dic.keys():
		dic[key] = clear_data_sub(dic[key])

	return dic


def get_res_sub(r_dic):
	"""
	获取res
	:param r_dic:
	:return:
	"""
	for page in dict_stk_list.keys():
		for stk_info in dict_stk_list[page]:
			r_dic[page][stk_info[1] + '_res'] = r_dic[page][stk_info[1] + '_res'].get()
	
	return r_dic


def print_analysis_to_win(r_dic, win, flash_flag, debug=False):
	
	for page in dict_stk_list.keys():
		for stk_info in dict_stk_list[page]:
			analysis_result = r_dic[page][stk_info[1] + '_res']
			
			debug_print_txt('pipe_msg_pro', '', '收到数据：' + str(analysis_result) + ', 开始闪动和提示处理：\n', debug)
			if isinstance(analysis_result, str):
				
				# 非空说明有情况，闪烁提示
				if (not pd.isnull(analysis_result)) & (len(analysis_result) > 0):
					win.on_update_note_tc_a(change_font_color(analysis_result + '\n'))
					flash_flag = True
			elif isinstance(analysis_result, list):
				
				# 去空值
				analysis_result = list(filter(lambda x: not pd.isnull(x), analysis_result))
				
				# 非空说明有情况，闪烁提示
				if (not pd.isnull(analysis_result)) & (len(analysis_result) > 0):
					flash_flag = True
					
				for str_ in analysis_result:
					win.on_update_note_tc_a(change_font_color(str_ + '\n'))
			else:
				debug_print_txt('hour_analysis', '', '不识别的数据格式', debug)
				
			debug_print_txt('pipe_msg_pro', '', '本次数据处理完成！', debug)

	return flash_flag


def clear_data_sub(r_dic):
	"""
	用于生成图片的数据已经用完了，
	不必进入管道，在此处删除以节省管道资源
	:param r_dic:
	:param kind:
	:return:
	"""
	for page in dict_stk_list.keys():
		for stk_info in dict_stk_list[page]:
			r_dic[page][stk_info[1] + '_d'] = None
	
	return r_dic


def check_single_stk_hour_idx_sub(stk_df, stk_code, debug=False):
	"""
	打印常用指标
	"""

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
		
		# 打印原始数据
		debug_print_txt(txt_name, stk_code, stk_df.to_string() + '\n\n')
		
		# 打印结果
		debug_print_txt(txt_name, stk_code, '结果：\n' + str(result_analysis) + '\n\n')
	
	return result_analysis


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


def update_rsv_record(self):
	
	jq_login()
	try:
		code_list = list(set(read_config()['buy_stk'] + read_config()['concerned_stk'] + read_config()['index_stk']))
		
		# global  RSV_Record
		for stk in code_list:
			RSV_Record[stk] = cal_rsv_rank(stk, 5)
	
	except Exception as e:
		print(str(e))
		self.p_ctrl.m_textCtrlMsg.AppendText('RSV数据更新失败！原因：\n' + str(e) + '\n')
		debug_print_txt('main_log', '', 'RSV数据更新失败！原因：\n' + str(e) + '\n')
	finally:
		jq.logout()


def on_timer_ctrl(win, debug=False):
	"""
	控制台定时器响应函数
	:return:
	"""
	
	# 清屏
	wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_S, data='检测时间：' + get_current_datetime_str() + '\n\n'))
	
	# 不在交易时间不使能定时器
	if (not is_in_trade_time()) & (not debug):
		wx.PostEvent(win, ResultEvent(
			id=MSG_UPDATE_ID_A,
			data='控制台定时器：当前不属于交易时间！\n'))
		
		return
	
	buy_stk_list = list(set(read_config()['buy_stk'] + read_config()['index_stk']))
	
	# 局部变量
	note_list = []
	
	# 对stk进行检查
	for stk in buy_stk_list:
		str_gui = judge_single_stk(stk_code=stk, stk_amount_last=400, gui=True, debug=True)
		
		if len(str_gui['note']):
			note_list.append(str_gui['note'] + '\n\n')
		
		# 打印流水信息
		if len(str_gui['msg']):
			wx.PostEvent(win, ResultEvent(
				id=MSG_UPDATE_ID_A,
				data=change_font_color(str_gui['msg'])))
	
	# 打印日志
	debug_print_txt('timer_ctrl_log', 'total',
	                get_current_datetime_str() + ':\n' +
	                '提示消息：\n' + str(note_list) + '\n' + '流水消息：\n' + str(str_gui['msg']))
	
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


def analysis_print(pipe_data, win, kind, debug=False):
	"""-------------------- 进行判断 ------------------------"""
	debug_print_txt('pipe_msg_pro', '', '\n收到' + str(kind) + '分析数据，开始处理！\n', debug)
	flash_flag = False
	
	# 向提示框打印提示
	for key in pipe_data[1]:
		flash_flag = print_analysis_to_win(pipe_data[1][key], win, flash_flag, debug)
	
	if flash_flag:
		win.flash_window()
	
	debug_print_txt('pipe_msg_pro', '', '\n' + str(kind) + '判断完成！\n', debug)


def pipe_msg_process(win, pipe_to_master, debug=False):
	
	while True:
		pipe_data = pipe_to_master.recv()
		
		debug_print_txt('pipe_msg_pro', '', '\n\n==========================================\n收到信息，进行判断！\n', debug)
		
		""" ------------------ 管道处理机 ---------------------- """

		if pipe_data[0] == HOUR_UPDATE_NUM:
			
			debug_print_txt('pipe_msg_pro', '', '\n收到小时更新图片，开始更新！\n', debug)
			
			win.on_update_msg_tc_a('开始打印小时图片...\n')
			
			pic = load_local_pic_for_wx(pipe_data[1])
			win.on_update_hour_pic(pic)
			win.on_update_msg_tc_a('小时图片打印完成！\n')
			
			debug_print_txt('pipe_msg_pro', '', '\n小时图片更新完成！\n', debug)
			
			"""-------------------- 打印判断 ------------------------"""
			analysis_print(pipe_data, win, '小时线', debug)
		
		# day 图 更新处理
		elif pipe_data[0] == DAY_UPDATE_NUM:
			
			debug_print_txt('pipe_msg_pro', '', '\n收到日线图片更新命令！\n', debug)
			
			win.on_update_msg_tc_a('开始打印日线图片...\n')
			pic = load_local_pic_for_wx(pipe_data[1])
			win.on_update_day_pic(pic)
			win.on_update_msg_tc_a('日线图片打印完成！\n')
			
			debug_print_txt('pipe_msg_pro', '', '\n日线图片更新完成！\n', debug)
			
			"""-------------------- 打印判断 ------------------------"""
			analysis_print(pipe_data, win, '日线', debug)
			
		# 追加msg
		elif pipe_data[0] == MSG_UPDATE_NUM_A:
			win.on_update_msg_tc_a(pipe_data[1])
		
		# 设置msg
		elif pipe_data[0] == MSG_UPDATE_NUM_S:
			win.on_update_msg_tc_s(pipe_data[1])
		
		# 追加note
		elif pipe_data[0] == NOTE_UPDATE_NUM_A:
			win.on_update_note_tc_a(pipe_data[1])
		
		# 设置note
		elif pipe_data[0] == NOTE_UPDATE_NUM_S:
			win.on_update_note_tc_s(pipe_data[1])
		
		# 闪烁
		elif pipe_data[0] == FLASH_WINDOW_NUM:
			debug_print_txt('pipe_msg_pro', '', '收到闪动命令，闪动窗口！\n', debug)
			win.flash_window()
		
		# 更新上次时间
		elif pipe_data[0] == LAST_TIME_UPDATE_NUM:
			win.on_update_last_time()
		
		# CPT 初始化
		elif pipe_data[0] == INIT_CPT_NUM:
			
			debug_print_txt('pipe_msg_pro', '', '\n收到初始化命令，开始初始化！\n', debug)
			
			win.on_update_msg_tc_a('正在初始化图片...\n'),
			win.on_update_msg_tc_a(note_init_pic),
			win.on_init_pic(pipe_data[1])
			
			debug_print_txt('pipe_msg_pro', '', '\n图片初始化完成！\n', debug)
		
		# 延时两秒
		time.sleep(2)


def data_process_callback(pipe_proc, debug=False, process=6):
	
	# init update pic
	pool = multiprocessing.Pool(process)
	
	hour_pic = {
		'h': gen_kind_pic('h', pool),
		'h_idx': gen_kind_pic('h_idx', pool)
	}
	day_pic = {
		'd': gen_kind_pic('d', pool),
		'd_idx': gen_kind_pic('d_idx', pool),
		'wm': gen_kind_pic('wm', pool)
	}
	pool.close()
	pool.join()
	
	# 清空数据，节省管道资源
	day_pic = clear_data_dic(day_pic)
	hour_pic = clear_data_dic(hour_pic)
	
	# 解析分析数据
	day_pic = get_process_res(day_pic)
	hour_pic = get_process_res(hour_pic)
	
	pipe_proc.send((HOUR_UPDATE_NUM, hour_pic))
	pipe_proc.send((DAY_UPDATE_NUM, day_pic))
	
	# 循环
	while True:
		
		global last_upt_t
		upt_flag, last_upt_t = is_time_h_macd_update(last_upt_t)
		
		if upt_flag | debug:
			debug_print_txt('main_log', '', '\n开始半小时分析和更新！')

			# update hour pic
			pool = multiprocessing.Pool(process)
			hour_pic = {
				'h': gen_kind_pic('h', pool),
				'h_idx': gen_kind_pic('h_idx', pool)
			}
			pool.close()
			pool.join()
			
			# 清空数据，节省管道资源 & 解析分析数据
			hour_pic = clear_data_dic(hour_pic)
			hour_pic = get_process_res(hour_pic)
			
			pipe_proc.send((HOUR_UPDATE_NUM, hour_pic))
			
			debug_print_txt('main_log', '', '\n完成半小时分析和更新！')

		time.sleep(5)
		
	
def timer_ctrl(win, debug=False):
	jq_login()
	while True:
		on_timer_ctrl(win, debug)
		time.sleep(30)
		
	logout()


def hour_analysis(pipe_master):
	"""
	小时监测（闲置）
	:return:
	"""
	
	debug_print_txt('hour_analysis', '', '\n' + '进入小时判断' + '\n')
	
	for stk in list(set(read_config()['buy_stk'] + read_config()['concerned_stk'] + read_config()['index_stk'])):
		
		# 阈值条件不满足，该stk直接pass
		if not read_opt_json(stk, opt_record_file_url)['threshold_satisfied_flag']:
			pipe_master.send((MSG_UPDATE_NUM_A, code2name(stk) + '阈值条件不满足，不进行拐点检测\n'))
			
			debug_print_txt('hour_analysis', '', '\n' + code2name(stk) + '阈值条件不满足，不进行拐点检测\n')
			continue
		
		hour_idx_str = check_single_stk_hour_idx_wx(stk, source='jq', debug=True)
		if len(hour_idx_str):

			for str_tmp in hour_idx_str:
				pipe_master.send((NOTE_UPDATE_NUM_A, change_font_color(str_tmp)))
			
			# 打印日志
			debug_print_txt('hour_analysis', '', '\n' + str(hour_idx_str))
			
			# flash
			pipe_master.send((FLASH_WINDOW_NUM, None))
			

def on_timer_pic(win, pool, debug=False):
	"""
	图片定时器响应函数（闲置）
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
	pic_dict = {'h_macd': gen_kind_pic('h', pool), 'h_idx': gen_kind_pic('h_idx', pool)}
	wx.PostEvent(win, ResultEvent(id=HOUR_UPDATE_ID, data=pic_dict))
	wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data='小时图片更新完成！\n'))
	
	# 拐点检测
	window_flash_flag = False
	for stk in list(set(read_config()['buy_stk'] + read_config()['concerned_stk'] + read_config()['index_stk'])):
		
		# 阈值条件不满足，该stk直接pass
		if not read_opt_json(stk, opt_record_file_url)['threshold_satisfied_flag']:
			wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data=code2name(stk) + '阈值条件不满足，不进行拐点检测\n'))
			continue
		
		hour_idx_str = check_single_stk_hour_idx_wx(stk, source='jq', debug=True)
		if len(hour_idx_str):
			window_flash_flag = True
			for str_tmp in hour_idx_str:
				wx.PostEvent(win, ResultEvent(id=NOTE_UPDATE_ID_A, data=change_font_color(str_tmp)))
	
	# 窗口闪烁
	if window_flash_flag:
		wx.PostEvent(win, ResultEvent(id=FLASH_WINDOW_ID, data=None))
	
	wx.PostEvent(win, ResultEvent(id=MSG_UPDATE_ID_A, data=note_sar_inflection_point))


class ResultEvent(wx.PyEvent):
	"""
	事件类
	"""
	
	def __init__(self, id, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(id)
		self.data = data


def judge_single_stk(stk_code, stk_amount_last, debug=False, gui=False):
	"""

	:param stk_code:
	:param stk_amount_last:
	:param debug:
	:param gui:
	:return:
	"""
	
	""" 变量声明 """
	str_gui = {
		'note': '',
		'msg': ''
	}
	str_ = '\n\n\n=============================================\n' + code2name(stk_code) + ':开始进入本周期判断!\n'
	debug_print_txt('stk_judge', stk_code, str_, debug)
	str_gui['msg'] = str_gui['msg'] + str_
	
	money_each_opt = 5000
	
	""" ==== 获取该stk的实时价格,如果是大盘指数，使用聚宽数据，否则有限使用tushare ==== """
	try:
		current_price = get_current_price_JQ(stk_code)
	except:
		str_gui['msg'] = str_gui['msg'] + stk_code + '获取实时price失败！\n'
		return str_gui
	
	str_ = '实时价格:' + str(current_price) + '\n'
	debug_print_txt('stk_judge', stk_code, str_, debug)
	str_gui['msg'] = str_gui['msg'] + str_
	
	""" ==================== 获取上次price ==================== """
	opt_json_stk = read_opt_json(stk_code, opt_record_file_url)
	
	# 如果没有相应的json文件，不进行判断，直接返回
	if opt_json_stk == {}:
		str_ = code2name(stk_code) + '没有历史操作记录，不进行阈值判断！\n'
		debug_print_txt('stk_judge', stk_code, '函数 judge_single_stk：' + str_,
		                debug)
		str_gui['msg'] = str_gui['msg'] + str_
		return str_gui
	
	if len(opt_json_stk['b_opt']) == 0:
		str_ = code2name(stk_code) + '没有历史操作记录，不进行阈值判断！\n'
		debug_print_txt('stk_judge', stk_code, '函数 judge_single_stk：' + str_,
		                debug)
		str_gui['msg'] = str_gui['msg'] + str_
		return str_gui
	
	# 读取
	threshold_satisfied_flag = opt_json_stk['threshold_satisfied_flag']
	
	str_gui['msg'] = str_gui['msg'] + '已经进行过闪动提示?：' + {False: '是', True: '否'}.get(threshold_satisfied_flag, '未知') + '\n'
	
	# 读取上次p和b操作中的最小p，备用
	last_p = opt_json_stk['p_last']
	b_p_min = np.min([x['p'] for x in opt_json_stk['b_opt']])
	
	str_ = '\n上次操作价格：' + str(last_p) + \
	       '\n最小买入价格：' + str(b_p_min) + \
           '\n买入-波动率:' + '%0.3f' % (100.0 * (current_price - last_p) / last_p) + '%' + \
           '\n卖出-波动率:' + '%0.3f' % (100.0 * (current_price - b_p_min) / b_p_min) + '%' + \
			'\n买入-波动:' + '%0.2f' % (current_price - last_p) + \
			'\n卖出-波动:' + '%0.2f' % (current_price - b_p_min)
	
	debug_print_txt('stk_judge', stk_code, str_, debug)
	str_gui['msg'] = str_gui['msg'] + str_ + '\n'
	
	""" =========== 实时计算价差，用于“波动提示”和“最小网格限制” ======== """
	
	""" ========== 排除获取的价格为0的情况，此种情况可能是stop或者时间未到 ========== """
	if current_price == 0.0:
		str_gui = myPrint(
			str_gui,
			stk_code + 'price==0.0! 返回！',
			method={True: 'gm', False: 'n'}[gui])
		
		return str_gui
	
	buy_amount = math.floor((money_each_opt / current_price) / 100) * 100
	
	""" 实时计算网格大小 """
	earn_threshold_unit = get_single_stk_reseau(stk_code)
	
	""" 调节 buy 和 sale 的threshold """
	if stk_code in RSV_Record.keys():
		thh_sale = earn_threshold_unit * 2 * RSV_Record[stk_code]
		thh_buy = earn_threshold_unit * 2 * (1 - RSV_Record[stk_code])
		
		debug_print_txt('stk_judge', stk_code, '', debug)
	else:
		RSV_Record[stk_code] = cal_rsv_rank(stk_code, 5)
		thh_sale = earn_threshold_unit * 2 * RSV_Record[stk_code]
		thh_buy = earn_threshold_unit * 2 * (1 - RSV_Record[stk_code])
		
	str_ = '\n卖出网格大小:' + '%0.3f' % thh_sale + '\n买入网格大小:' + '%0.3f' % thh_buy + '\n'
	debug_print_txt('stk_judge', stk_code, str_, debug)
	str_gui['msg'] = str_gui['msg'] + str_
	
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
	
	""" ============================= 判断是否超过阈值,进行bs操作 ============================== """
	pcr = read_config()['pcr']/100.0
	
	# 打印日志
	debug_print_txt('stk_judge', stk_code, '读取的最小波动率:' + str(pcr) + '\n', debug)
	
	debug_print_txt('stk_judge', stk_code, '允许阈值判断标志位（True为允许）:' + str(threshold_satisfied_flag) + '\n', debug)
	debug_print_txt('stk_judge', stk_code, '判断是否可以卖出：\ncurrent_price - b_p_min > thh_sale:' + str(current_price - b_p_min > thh_sale) + '\n', debug)
	debug_print_txt('stk_judge', stk_code,
	                '(current_price - b_p_min) / b_p_min >= pcr:' + str((current_price - b_p_min) / b_p_min >= pcr) + '\n', debug)
	
	debug_print_txt('stk_judge', stk_code,
	                '判断是否可以买入：\ncurrent_price - last_p < -thh_buy:' + str(current_price - last_p < -thh_buy) + '\n',
	                debug)
	debug_print_txt('stk_judge', stk_code,
	                '(current_price - last_p) / b_p_min <= -pcr:' + str((current_price - last_p) / b_p_min <= -pcr) + '\n', debug)

	if (current_price - b_p_min > thh_sale) & ((current_price - b_p_min) / b_p_min >= pcr):
		
		str_temp = "触发卖出网格！可以考虑卖出！ " + stk_code + code2name(stk_code) + \
		           '\nAmount:' + str(stk_amount_last) + \
		           '\n当前价格:' + str(current_price) + \
		           '\n上次买入价格:' + str(b_p_min) + \
		           '\n买入网格大小:' + '%0.3f' % thh_buy + \
		           '\n卖出网格大小:' + '%0.3f' % thh_sale + \
		           '\n最小操作幅度:' + '%0.3f' % pcr
		
		debug_print_txt('stk_judge', stk_code, str_temp + '\n在灯神进行bs操作之前，此stk不再进行阈值判断\n',
		                debug)
		
		if threshold_satisfied_flag:
			str_gui['note'] = str_gui['note'] + str_temp
			
			# 除非有bs操作，否则不再提示
			set_opt_json_threshold_satisfied_flag(opt_record_file_url, stk_code, value=False)
			
		else:
			str_gui['msg'] = str_gui['msg'] + str_temp
			
	elif (current_price - last_p < -thh_buy) & ((current_price - last_p) / b_p_min <= -pcr):
		
		str_temp = "触发买入网格！可以考虑买入！" + stk_code + code2name(stk_code) + \
		           '\nAmount:' + str(buy_amount) + \
		           '\n当前价格:' + str(current_price) + \
		           '\n上次价格:' + str(last_p) + \
		           '\n买入网格大小:' + '%0.2f' % thh_buy + \
		           '\n卖出网格大小:' + '%0.2f' % thh_sale + \
		           '\n最小操作幅度:' + '%0.3f' % pcr
		
		debug_print_txt('stk_judge', stk_code, str_temp + '\n在灯神进行bs操作之前，此stk不再进行阈值判断\n',
		                debug)
		if threshold_satisfied_flag:
			str_gui['note'] = str_gui['note'] + str_temp
			
			# 除非有bs操作，否则不再提示
			set_opt_json_threshold_satisfied_flag(opt_record_file_url, stk_code, value=False)
		else:
			str_gui['msg'] = str_gui['msg'] + str_temp
		
		
	
	else:
		str_ = stk_code + ':未触发任何警戒线！\n'
		str_gui['msg'] = str_gui['msg'] + str_
		debug_print_txt('stk_judge', stk_code, str_, debug)
		
	return str_gui


def set_opt_json_threshold_satisfied_flag(json_file_url, stk_code, value=True):
	if os.path.exists(json_file_url):
		with open(json_file_url, 'r') as f:
			json_p = json.load(f)
		
		if stk_code in json_p.keys():
			json_p[stk_code]['threshold_satisfied_flag'] = value
		else:
			json_p[stk_code] = {
					'b_opt': [],
					'p_last': None,
					'threshold_satisfied_flag': value,
					'total_earn': 0
				}
			
		# 将数据写入
		with open(json_file_url, 'w') as f:
			json.dump(json_p, f)
			
		return 0
	else:
		return 2


if __name__ == '__main__':
	jq_login()
	buy_stk_list = list(set(read_config()['buy_stk'] + read_config()['index_stk']))
	
	# 局部变量
	note_list = []
	
	# 对stk进行检查
	for stk in buy_stk_list:
		str_gui = judge_single_stk(stk_code=stk, stk_amount_last=400, gui=True, debug=True)
	logout()
	app = wx.App()
	pool = multiprocessing.Pool(processes=7)
	from DataSource.auth_info import *
	
	r = gen_kind_pic('idx', pool)
	
	pprint.pprint(r)
	
	end = 0
