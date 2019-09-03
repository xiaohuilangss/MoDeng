# encoding = utf-8
from Config.GlobalSetting import *
import os

save_dir = "F:/MYAI/文档资料/用于读取的文件/BasicDataWithQInfo/"


result = []
for stk in g_total_stk_code:
    if os.path.exists(save_dir + "basicData_Q" + stk + ".csv"):
        with open(save_dir+"basicData_Q"+stk+".csv") as f:
            basic_data_Q = pd.read_csv(f)
            if len(basic_data_Q):
                result.append(basic_data_Q)
    else:
        print("没有找到" + stk + "的含有basic_Q的信息！")

df_data_rd = pd.concat(result,axis=0,ignore_index=True,join_axes=[result[0].columns]).dropna(axis=0,how='any')


# 对 季度变化率 进行分类，分为“大跌”、“中跌”、“微跌”、“微涨”、“中涨”、“大涨”

for id in df_data_rd.index:
    Q_ratio_diff = df_data_rd.loc[id,'Q_ratio_diff']

    # if Q_ratio_diff < -0.10:
    #     df_data_rd.loc[id, 'ratio_class'] = '大跌'
    # elif -0.10 <= Q_ratio_diff < -0.04:
    #     df_data_rd.loc[id, 'ratio_class'] = '中跌'
    # elif -0.04 <= Q_ratio_diff < 0:
    #     df_data_rd.loc[id, 'ratio_class'] = '微跌'
    # elif 0 <= Q_ratio_diff < 0.04:
    #     df_data_rd.loc[id, 'ratio_class'] = '微涨'
    # elif 0.04 <= Q_ratio_diff < 0.10:
    #     df_data_rd.loc[id, 'ratio_class'] = '中涨'
    # elif 0.10 <= Q_ratio_diff:
    #     df_data_rd.loc[id, 'ratio_class'] = '大涨'

    if Q_ratio_diff < 0:
        df_data_rd.loc[id, 'ratio_class'] = '跌'
    else:
        df_data_rd.loc[id, 'ratio_class'] = '涨'

    stk_class = df_data_rd.loc[id,'stk_class']

    if stk_class == 'sh':
        df_data_rd.loc[id, 'stk_class_num'] = 0
    elif stk_class == 'sz':
        df_data_rd.loc[id, 'stk_class_num'] = 1
    elif stk_class == 'cyb':
        df_data_rd.loc[id, 'stk_class_num'] = 2
    elif stk_class == 'zxb':
        df_data_rd.loc[id, 'stk_class_num'] = 3

df_data_rd.to_csv(save_dir + "basic_total.csv", index=False)


