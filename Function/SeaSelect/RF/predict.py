# encoding=utf-8

"""
使用随机森林模型对
"""
from DataSource.Data_Sub import get_all_stk
from Function.SeaSelect.RF.rf_data_pre_class import DataProRF, RF

if __name__ == '__main__':
	
	# 获取股票池
	s_all = get_all_stk()
	
	# 加载模型
	fl = DataProRF(None)
	rf = RF(None, fl.feature_col_origin, fl.label_col)
	rf.load_model()
	
	# 准备数据
	def get_predict_data(stk):
		dpr = DataProRF(stk_code=stk, count=40)
		dpr.pro()
		return dpr.day_data.tail(1).loc[:, fl.feature_col_finale].values
	
	predict_feature = [get_predict_data(s) for s in s_all]