# encoding=utf-8

"""
使用随机森林模型对
"""
import json
import pprint

import os

import multiprocessing

from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_all_stk
from DataSource.auth_info import jq_login
from Function.SeaSelect.RF.global_values import freq, temp_dir
from Function.SeaSelect.RF.rf_data_pre_class import DataProRF, RF
from Function.SeaSelect.Sub.Sub import gen_pdf


class RFPre:
	def __init__(self, save_dir, stk_list):
		self.stk_list = stk_list
		self.save_dir = save_dir
		self.log = ''
		self.rf = None
		
		self.dpr = DataProRF(None)
		self.pre_result = None
		
		# 执行处理
		self.load_rf_model()
		self.predict_list()
	
	@staticmethod
	def save_result_to_json(save_dir, result, name='predict_result.json'):
		"""
		将结果存入json
		:param name:
		:param save_dir:
		:param result:
		:return:
		"""
		file_url = save_dir + name
		if not os.path.exists(file_url):
			with open(file_url, 'w') as f:
				json.dump(result, f)
		else:
			with open(file_url, 'wr') as f:
				r_ori = json.load(f)
				r_ori = r_ori + result
				json.dump(r_ori, f)
		
		self.log = self.log + '结果保存成功！\n'
		
	# 准备数据
	def get_predict_data(self, stk):
		try:
			self.log = '开始预测%s！' % stk
			dpr = DataProRF(stk_code=stk, count=100, freq=freq)
			dpr.predict_pro(local_data=True)
			return dpr.day_data.tail(1).loc[:, self.dpr.feature_col].values
		
		except Exception as e:
			print('函数 data pro ：\n' + str(e))
			return None
	
	def predict_sig(self, feature):
		try:
			r = self.rf.predict(feature)
			print('预测成功！')
			return r
		except Exception as e:
			print('函数 predict ：\n' + str(e))
	
	def load_rf_model(self):
		
		# 加载模型
		rf = RF(None, self.dpr.feature_col, self.dpr.label_col)
		rf.load_model(save_dir=self.save_dir)
		self.rf = rf
		
	def predict_list(self):
		self.pre_result = [(s, self.predict_sig(self.get_predict_data(s))) for s in self.stk_list]
	
	
def async(dir, stk_list):
	rp = RFPre(dir, stk_list)
	print(rp.log)
	return rp.pre_result


if __name__ == '__main__':

	# 获取stk池
	s_all = get_all_stk()
	
	p_amount = 7
	pool = multiprocessing.Pool(p_amount)
	span = int(len(s_all)/p_amount)
	
	idx_s = list(range(0, len(s_all)-span, span))
	
	r = [pool.apply_async(async, (temp_dir, s_all[x:x+span-1])).get() for x in idx_s]
	pool.close()
	pool.join()
	
	# 保存结果
	r_sum = []
	for r_sig in r:
		r_sum = r_sum + r_sig

	# 清空预测失败的
	p_filter = list(filter(lambda x: x[1] is not None, r_sum))

	# 筛选出预测值大于8的案例
	p_f2 = list(filter(lambda x: x[1][0] > 8, p_filter))

	# 按可信度排序
	p = sorted(p_f2, key=lambda x: x[1][1], reverse=True)

	pprint.pprint([(x[0], code2name(x[0]), x[1][0][0], x[1][1]) for x in p[:50]])

	# 打印pdf文件
	gen_pdf([x[0] for x in p[:50]])

	end = 0