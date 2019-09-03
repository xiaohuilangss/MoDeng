# encoding = utf-8
from Config.GlobalSetting import *

# 本文件包含于数据结构相关的自定义函数，比如处理序列等。。。



# 求一个数字序列的前后差，例如：输入[1,4,12,4,23,7] 输出[3,8，-8,19，-16]

def cal_seq_diff(seq_param):
    if len(seq_param) < 2:
        return []
    else:
        a = seq_param.copy()
        b = seq_param.copy()
        a.insert(0,0)
        b.append(0)
        result_temp = list(map(lambda x,y:x-y,b,a))
        result_temp.pop(0)
        result_temp.pop()
        return result_temp



# 给定一个序列，求环比，当前环比增长为：（当前值-上一值）/上一值
# 输入时list或者Series都可以，函数自动识别
# 例如：输入[1,4,12,4,23,7] 输出[3/1,8/4，-8/12,19/4，-16/23]
def cal_seq_qoq(seq_param):

    if isinstance(seq_param,pd.Series):

        # 将Series转为list
        seq_list = list(seq_param)

        # 计算该list的序列差
        seq_diff_local = cal_seq_diff(seq_list)

        # 计算环比增长率序列

        return []



# 获取dataframe中一个时间段内某个字段的变化趋势，主要有“方差”、“变化比率均值”、“前后比率差值”
# @:parameter code_param          stk代码
# @:parameter time_span_param     时间跨度
# @:parameter date_param
# @:parameter field_param         dataframe中被求均值的字段

def get_tendency(k_df_param,date_param, time_span_param,field_param):

    k_df = k_df_param

    # 为了节省排序时间，先将最近十天的时间取出，然后按时间排序，取最近的数据
    latest_span= k_df[(k_df.date>add_date_str(date_param,-10))&(k_df.date<date_param)]\
                        .sort_values(by='date',ascending=False).head(1)

    if len(latest_span):
        master_field = latest_span.reset_index(drop=True).to_dict(orient='index')[0][field_param]
    else:
        print("函数get_average_index： 在日期"+date_param + "计算"+field_param+"值时出错！")
        return {}


    # 取“主角日期”与该日期之前“time_span_param”长度的数据的field_param的均值
    span_df = k_df[(k_df.date>add_date_str(date_param,-1*time_span_param))&(k_df.date<date_param)]

    if len(span_df) > 0:
        span_cov = np.cov(span_df[field_param])

        # 获取序列差

    else:
        return {}

    return {"date":date_param,
            field_param:master_field,
            field_param+"cov"+str(time_span_param):span_cov}

