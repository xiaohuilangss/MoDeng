# encoding=utf-8

"""
使用随机森林模型对
"""
import pprint

from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_all_stk
from DataSource.auth_info import jq_login
from Function.SeaSelect.RF.global_values import freq, temp_dir
from Function.SeaSelect.RF.rf_data_pre_class import DataProRF, RF

if __name__ == '__main__':

	jq_login()
	
	# 获取股票池
	s_all = get_all_stk()
	
	# 加载模型
	fl = DataProRF(None)
	rf = RF(None, fl.feature_col, fl.label_col)
	rf.load_model(save_dir=temp_dir)
	
	# 准备数据
	def get_predict_data(stk):
		try:
			print('开始预测%s！' % stk)
			dpr = DataProRF(stk_code=stk, count=100, freq=freq)
			dpr.predict_pro(local_data=True)
			return dpr.day_data.tail(1).loc[:, fl.feature_col].values

		except Exception as e:
			print('函数 data pro ：\n' + str(e))
			return None

	def predict(df):
		try:
			r = rf.predict(df)
			print('预测成功！')
			return r
		except Exception as e:
			print('函数 predict ：\n' + str(e))

	predict_feature = [(s, predict(get_predict_data(s))) for s in s_all]

	# 清空预测失败的
	p_filter = list(filter(lambda x: x[1] is not None, predict_feature))

	# 筛选出预测值大于8的案例
	p_f2 = list(filter(lambda x: x[1][0] > 8, p_filter))

	# 按可信度排序
	p = sorted(p_f2, key=lambda x: x[1][1], reverse=True)

	pprint.pprint([(x[0], code2name(x[0]), x[1][0][0], x[1][1]) for x in p[:50]])
	end = 0