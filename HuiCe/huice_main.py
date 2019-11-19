# encoding=utf-8
from AutoDailyOpt.Debug_Sub import debug_print_txt
from AutoDailyOpt.Sub import judge_single_stk_sub
from SDK.shelfSub import shelveP, shelveL
from pylab import *

if __name__ == '__main__':

	stk_code = '000001'
	df = shelveL('./temp_data/', stk_code+'huice')

	"""
	df = df.dropna().reset_index()
	df.plot('index', ['close', 'rsv', 'reseau'], style=['*', '*', '*'], subplots=True)
	"""
	df = df.dropna()
	last_p = df.head(1)['open'].values[0]

	for idx in df.index:

		rsv = df.loc[idx, 'rsv']
		reseau = df.loc[idx, 'reseau']

		thh_sale = reseau * 2 * rsv
		thh_buy = reseau * 2 * (1 - rsv)

		p_b = last_p - thh_buy
		p_s = last_p + thh_sale

		df.loc[idx, 'p_b'] = p_b
		df.loc[idx, 'p_s'] = p_s

		j_r = judge_single_stk_sub(
			reseau=reseau,
			rsv=rsv,
			current_price=df.loc[idx, 'close'],
			stk_price_last=last_p,
			min_reseau=0.001,
			sar_diff=df.loc[idx, 'SAR'] - df.loc[idx, 'close'])

		df.loc[idx, 'opt'] = j_r[0]

		if (j_r[0] == 1) | (j_r[0] == 2):
			last_p = df.loc[idx, 'close']

		df.loc[idx, 'last_p'] = last_p

		print(j_r[1])

	end = 0
	df = df.reset_index().reset_index()

	df_b = df[df['opt'] == 2]
	df_s = df[df['opt'] == 1]

	# 打印过程数据到文本
	df.to_csv('./temp_data/' + stk_code + 'huice.csv')
	# with open('./temp_data/' + stk_code + 'huice.txt', 'a+') as f:
	# 	f.write(df.to_string())

	fig, ax = plt.subplots(ncols=1, nrows=1)

	ax.plot(df['level_0'], df['close'], 'k*--', label='close')
	# ax.plot(df['level_0'], df['SAR'], 'c--', label='SAR')
	# ax.plot(df['level_0'], df['p_b'], 'g*--', label='b_line', linewidth=0.5)
	# ax.plot(df['level_0'], df['p_s'], 'r*--', label='s_line', linewidth=0.5)

	ax.plot(df['level_0'], df['last_p'], 'y-', label='last_p', linewidth=2.5)

	ax.plot(df_b['level_0'], df_b['close'], 'g*', label='b_pot', markersize=10)
	ax.plot(df_s['level_0'], df_s['close'], 'r*', label='s_pot', markersize=10)

	ax.legend(loc='best')
	plt.show()


