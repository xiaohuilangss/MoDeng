# encoding = utf-8

from sdk.SDKHeader import *

from Config.GlobalSetting import *
from sdk.MyTimeOPT import add_date_str, minus_date_str


def cal_chain_ratio_average(list_param):
    '''
    对一个数字序列进行处理，求其增长趋势，返回值包括“环比增长率均值”
    (不科学，弃用！)
    '''
    if len(list_param)<2:
        return None

    if len(list_param)==2:
        return [(list_param[1]-list_param[0])/list_param[0]]
    else:
        forward = list_param[0:len(list_param)-1]
        behind = list_param[1:len(list_param)]

        # 求取前后差值
        diff = list(map(lambda x:x[0]-x[1],zip(behind,forward)))

        # 求取环比改变
        chain_ratio = list(map(lambda x:x[0]/x[1],zip(diff,forward)))

        return sum(chain_ratio)/len(chain_ratio)



def get_sample_flow(con_param, code_param, sample_amount, sample_length):
    '''
    获取流入量，按月为单位
    当月的日平均水流量，绝对输入量，取日均量的原因是为了防止因为数据缺失而导致月输入总量的计算错误！
    。。。先写一个月绝对总输入量的

    @:parameter code_param:     代码
    @:parameter sample_amount:  样本个数,int类型，
                                比如，4，则从当前时刻往前推4个月作为时期跨度，即返回4个数据：每个月的水量净流入
    @:parameter sample_length   样本长度，int类型，比如说30是一个月，7是一个周

    举例：sample_amount=4，sample_length=30，则以30天为单位，返回最近的四个单位的数据

    '''


    # 如果表不存在，返回空
    if not is_table_exist(conn=con_param, table_name="tick"+code_param,database_name= stk_tick_data_db_name):
        print("stk" + code_param + "：数据不存在！")
        return []


    # 获取该代码的dataframe
    df = get_total_table_data(conn=con_param, table_name="tick"+code_param).drop_duplicates()

    # 创建用于存储结果的list
    result = list()


    # dateSeries 降序排列的date_series
    date_series = sorted(df.date,reverse=True)

    # 获取df中的最晚时间
    latest_date_in_table = date_series[0]

    # 获取df中的最早时间
    early_date_in_table = date_series[len(date_series)-1]

    for i in range(0, sample_amount):

        # 获取本次数据的时间跨度（起止时间都取开区间）
        start_date_temp = add_date_str(latest_date_in_table,-(i+1)*sample_length +1)
        end_date_temp = add_date_str(latest_date_in_table,-i*sample_length)

        # 如果最早时间早于表中的最早时间，则直接返回
        if minus_date_str(end_date_temp,early_date_in_table) < 0:
            print("采样的最早时间超过了表中的最早时间，for循环break！")


        # 获取本时间段的数据
        df_span = df[(df.date>start_date_temp)&(df.date<=end_date_temp)].drop_duplicates()
        if(df_span.empty):
            continue

        # 求本段时间的日均水流量
        diff_series = df_span.total_in-df_span.total_out
        in_out_avge = diff_series.sum()/len(diff_series)

        # 将结果保存到list中
        result.append(in_out_avge)

    # 按时间顺序排序
    result.reverse()

    # 返回结果
    return result


def plot_tick_data_from_db(data_df,stk_code):

    # read data from database
    # data_df = get_total_table_data(conn_tick, 'tick' + stk_code)

    # trick to get the axes
    fig, ax = plt.subplots(2,1)

    # plot data
    # ax.plot(data_df['date'], data_df['big_in'], 'go--', label='big_in')
    ax[1].plot(data_df['date'], data_df['total_in'], 'b*--', label='total_in')
    ax[0].plot(data_df['date'], data_df['close'], 'g*--', label='close')
    # ax.plot(data_df['date'], data_df['total_in']-data_df['total_out'], 'r*--', label='total_change')

    # make and set ticks and ticklabels
    xticklabels = list(map(lambda elem: str(elem)[2:10], data_df['date']))
    ax[1].set_xticklabels(xticklabels, rotation=90)
    ax[0].set_xticklabels(xticklabels, rotation=90)
    ax[1].set_title('tick+close' + stk_code)
    ax[1].legend(loc='best')

    # show the figure
    plt.show()

# -------------------------画close与total_in的图形-------------------------------------------
code_str = "300508"
tick_df = get_total_table_data(conn_tick,"tick"+code_str)
k_df = get_total_table_data(conn_k,"k"+code_str)

k_df_index = k_df.set_index("date")
tick_df_index = tick_df.set_index("date")

concat_df = pd.concat([k_df_index,tick_df_index],axis=1,join="inner").reset_index()




plot_tick_data_from_db(concat_df,'000418')


# ------------------------- 用来测试水流变化趋势的代码 ----------------------------------

# 获取采样数据,在采样的同时，将code与采样结果zip
samples = list(map(lambda x:{"code":x,"sample":get_sample_flow(con_param=conn_tick, code_param=x, sample_amount=6, sample_length=5)}, g_total_stk_code))

# 过滤掉samples中空的成员(过滤之后没法与code进行zip，所以需要在过滤之前zip)
samples_filter = list(filter(lambda x:not x["sample"]==[],samples))


# 根据采样数据判断水流增减趋势
# 返回一个list
# 其成员格式：
#   {“code”：***，“trend”：***}
trend_list = list(map(lambda x:{"code":x["code"], "average":sum(x["sample"])/len(x["sample"]),"sample":x["sample"]}, samples_filter))


# 按进水量大小对其进行排序，进水量大的在前
trend_sorted = sorted(trend_list, key=lambda x:x["average"])


# 将结果写入csv文件
write_dict_list_to_csv(list_param=trend_sorted, file_url="F:/MYAI/文档资料/用于调试的过程文件/trend.csv")