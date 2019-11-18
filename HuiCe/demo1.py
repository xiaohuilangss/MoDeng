# encoding=utf-8
from DataSource.Data_Sub import get_k_data_JQ
from HuiCe.Sub import cal_today_ochl

if __name__ == '__main__':
	from DataSource.auth_info import *

	# 准备数据
	df_5m = get_k_data_JQ('000001', count=48*400, freq='5m')
	df_5m['date'] = df_5m.apply(lambda x: str(x['datetime'])[:10], axis=1)
	df_day = get_k_data_JQ('000001', count=800).sort_values(by='date', ascending=True)

	# 大循环
	for idx in df_5m[48*20:].index:

		# 获取当天数据
		df_today = cal_today_ochl(df_5m.loc[:idx, :].tail(50))

		# 获取时间
		date = df_5m.loc[idx, 'date']

		# 获取该日期之前数天的数据
		df_day_data = df_day[df_day['date'] < date].tail(16)


	df_5m_last = df_5m.tail(50)
	r = cal_today_ochl(df_5m_last)