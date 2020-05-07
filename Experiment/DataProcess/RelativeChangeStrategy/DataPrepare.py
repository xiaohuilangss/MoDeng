# encoding = utf-8
"""
    本策略主要思想是，通过计算个股与大盘每日价格（指标）涨跌幅度的差值来评估一只stk在一段时间内的强弱

"""
from sdk.SDKHeader import *


index_list = get_class_df()
date_today = get_current_date_str()
days = 10


save_dir = "F:/MYAI/文档资料/用于读取的文件/"+'相对强势个股' + get_current_date_str()+'/'+str(days)+'/'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)


result = []
for stk in g_total_stk_code:
    df = cal_relative_ratio(stk,index_list, add_date_str(date_today,-1*days), date_today)

    if len(df):
        change_sum = df.ratio_diff.sum()

        result.append({'code':stk,'change_sum':change_sum})

    print(stk+'处理完成！')

df_sum = pd.DataFrame(result).dropna().sort_values(by='change_sum',ascending=False).head(60)
df_sum.to_csv('Data/RelativeS' + str(days)+'.csv')

for code in df_sum.code:
    plot_part_ave(90, code, save_dir, 'relative' + code)