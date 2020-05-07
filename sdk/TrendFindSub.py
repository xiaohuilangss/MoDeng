# encoding = utf-8
from sdk.SDKHeader import *
'''
思路：找到半年线为水平，60日，30日和14日线的斜率依此增大的stk。并且stk上市超过一定时间。
'''
# ss_code = '300508'
#
#
#
# # 获取一只stk的k数据
# ss_data_df = get_total_table_data(conn_k,'k'+ss_code)
#
#
# # 获取最近3天的日期，根据日期获取最近三天的180日，60日，30日，14日的均线的增长率
# days_near = ss_data_df.date.sort_values(ascending=False).head(3)
#
# time_span = [7,14,30,60,180]



# 获取最近几天某个timespan的均线的增长率的方差，其绝对值接近0的表示约平直，即其拐点附近。
def get_near_days_trend_cov(ss_df,near_days_length,specified_span):

    days_temp = ss_df.date.sort_values(ascending=False).head(near_days_length)

    # 设定结果
    result = list()

    # 求取设定的那几天的某个时间span的均线
    for day in days_temp:
        # try:
        av_index = get_average_index(ss_df, day, specified_span, 'close')
        if len(av_index):
            mean_index = av_index["close_mean"+str(specified_span)]
            result.append(mean_index)
        # except:
        #     print('error!')



    # av_single_span = pd.DataFrame(list(map(lambda x:get_average_index(ss_data_df,x, specified_span,'close'),days_temp)))["close_mean"+str(specified_span)]
    #

    # 求最近这几天的均线的方差
    av_cov = np.cov(result)


    print('函数get_near_days_trend_cov：' + '\n'+
          'time_span:'+str(specified_span)+'\n'+
          'av:'+'\n'+str(result)+'\n'+
          'cov:'+str(av_cov)+'\n\n')

    # 将方差返回
    return av_cov



# 给定：

# stk代码
# 时间span的list
# 均线前瞻长度
#
# 返回该stk相应span的均线方差

# 返回值范例：
# {
# 'cov_14': array(0.10599125514403376),
# 'cov_30': array(0.004552891156462607),
# 'cov_60': array(0.0004498451537884748),
# 'cov_180': array(0.0002672852191024599),
# 'code': '300508'
# }


#ts:time_span

def get_ts_cov(stk_code,ts,near_days_length):

    # 获取该stk的k数据
    ss_data_df = get_total_table_data(conn_k,'k'+stk_code)

    # 定义返回值
    result = {}

    # 遍历各个时间跨度，返回相应时间跨度的方差，字典形式
    for span in ts:

        result['cov_'+str(span)] = get_near_days_trend_cov(ss_data_df,near_days_length,span)

    # 在返回值中加上stk代码
    result['code'] = stk_code

    return result



# ---------------------------测试代码---------------------------

# a = get_ts_cov('300508',[14,30,60,180],4)
#
# end = 0