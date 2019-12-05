# encoding=utf-8

""" =========================== 将当前路径及工程的跟目录添加到路径中 ============================ """
import json
import sys
import os
from pprint import pprint

import numpy as np

from Config.AutoGenerateConfigFile import data_dir
from DataSource.Code2Name import name2code

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("MoDeng\\")+len("MoDeng\\")]  # 获取myProject，也就是项目的根路径

sys.path.append('..')
sys.path.append(rootPath)


from SDK.DBOpt import genDbConn
from SDK.MyTimeOPT import get_current_datetime_str

import pandas as pd

"""
本脚本用于记录操作历史

主要的命令有：

1、买卖命令：

例子： 

300508 buy 300 13.25        stk300508已经以13.25的价格买入了300股
002456 sale 200 15.3        stk002456已经以15.3的价格卖出了200股

2、查询命令
last  buy                   查询最后一次买入（未抵消）的价格

3、删除命令
del 300508 buy 300 13.25

"""


# def cat_stk_b_opt(stk_name, json_file_url):
# 	"""
#
# 	:param stk_name:
# 	:param json_file_url:
# 	:return:
# 	"""
#
# 	# 已有文件，打开读取
# 	if os.path.exists(json_file_url):
# 		with open(json_file_url, 'r') as f:
# 			opt_record = json.load(f)
# 	else:
# 		return '没有记录文件！'
#
# 	if name2code(stk_name) not in opt_record.keys():
# 		return '没有' + stk_name + '的数据！'
#
# 	if len(opt_record[name2code(stk_name)]['b_opt']) == 0:
# 		return stk_name + '没有操作记录！'
#
# 	return pd.DataFrame(opt_record[name2code(stk_name)]['b_opt']).sort_values(by='time', ascending=True).loc[:, ['time', 'p', 'amount']].to_string()
#
#
# def add_opt_to_json(input_str, json_file_url):
#
# 	# 返回字符串
# 	return_str = []
#
# 	# 已有文件，打开读取
# 	if os.path.exists(json_file_url):
# 		with open(json_file_url, 'r') as f:
# 			opt_record = json.load(f)
# 	else:
# 		opt_record = {}
#
# 	# 解析输入
# 	stk_name, opt, amount, p = input_str.split(' ')
# 	stk_code = name2code(stk_name)
# 	p, amount = float(p), float(amount)
#
# 	if stk_code in opt_record.keys():
# 		opt_r_stk = opt_record[stk_code]
# 	else:
# 		opt_r_stk = {
# 			'b_opt': [],
# 			'p_last': None,
# 			'threshold_satisfied_flag': False,
# 			'total_earn': 0
# 		}
#
# 	if opt == 'b':
# 		opt_r_stk['b_opt'].append(dict(time=get_current_datetime_str(), p=p, amount=amount))
#
# 	if opt == 's':
# 		if len(opt_r_stk['b_opt']) > 0:
# 			p_min = np.min([x['p'] for x in opt_r_stk['b_opt']])
# 			opt_r_stk['b_opt'].sort(key=lambda x: x['p'] == p_min, reverse=False)
#
# 			opt_pop = opt_r_stk['b_opt'].pop(-1)
# 			opt_r_stk['total_earn'] = opt_r_stk['total_earn'] + (p - opt_pop['p'])*float(opt_pop['amount'])
#
# 			return_str.append('抵消：' + str(opt_pop) + '\n')
# 			return_str.append('earn：' + str((p - float(opt_pop['p']))*float(opt_pop['amount'])) + '\n')
#
# 	opt_r_stk['p_last'] = p
# 	opt_r_stk['threshold_satisfied_flag'] = False
#
# 	# 保存数据
# 	opt_record[stk_code] = opt_r_stk
# 	with open(json_file_url, 'w') as f:
# 		json.dump(opt_record, f)
#
# 	# 返回
# 	return return_str


""" ============================ 命令行输入逻辑 =================================== """

if __name__ == '__main__':
	json_file_url = data_dir + '\opt_record.json'

	while True:
		input_str = input('输入你的命令：')

		# 按空格解析命令
		input_split = input_str.split(' ')

		if len(input_split) == 4:       # 插入命令
			
			add_opt_to_json(input_str, json_file_url)
		elif '查看所有' in input_str:
			with open(json_file_url, 'r') as f:
				opt_record = json.load(f)
				pprint(opt_record)
				
		elif '查看记录' in input_str:
			print(cat_stk_b_opt(input_split[1], json_file_url))
			
