# encoding=utf-8

from SDK.GeneralSub import write_dict_list_to_csv

from Config.GlobalSetting import *
from Restore.DataProcessSDK import find_change_ratio_span
from Restore.MyTimeOPT import *

"""
思路整理：
明显我们研究的对象离不开时间这个因素，所以需要以时间轴为横轴，整理各类数据！

需要整理的数据主要有：
1、外围货币环境（M2、利率、汇率、外汇储备等）
2、宏观经济指标（cpi，ppi，GDP增长率-季度）
5、大盘相关，指数变化、资金量净流入流出等。。。
3、本stk所述的类别（板块）的总体指数变动，比如银行类、工控类。。。
4、本stk自己的基本面数据（pe、现金流等等）
"""


# --------------------------正文--------------------------------------------------
# single_case_test = find_change_ratio_span(code_param="000893", ratio_param=0.3, backward_explore_ratio=0.4)

result = list()
for code in g_total_stk_code:

    single_example = find_change_ratio_span(code_param=code, ratio_param=-0.3, backward_explore_ratio=0.4)
    if len(single_example)>0:
        result.append(single_example)
        print("完成code："+code+"的case搜索！")
    else:
        print("code：" + code + "的case搜索无结果！")

for lt in result:
    write_dict_list_to_csv(list_param=lt, file_url=g_debug_file_url+"/case_"+get_current_date_str()+".csv")

