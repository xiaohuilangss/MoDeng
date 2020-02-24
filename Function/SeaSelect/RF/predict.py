# encoding=utf-8

"""
使用随机森林模型对
"""
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
			dpr = DataProRF(stk_code=stk, count=100, freq=freq)
			dpr.predict_pro()
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

	end = 0