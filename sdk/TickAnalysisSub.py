
# encoding = utf-8
from Config.GlobalSetting import conn_tick
from sdk.MyTimeOPT import add_date_str
from pandas import DataFrame
import pandas as pd
from sdk.DBOpt import get_total_table_data
# 用于整理tick数据

# 给定dataframe和日期，以及时间跨度，获取该日期的均值
def get_single_ave_by_date(df_param, date_param, time_span_param, field_param):

    temp_df = df_param

    # 为了节省排序时间，先将最近十天的时间取出，然后按时间排序，取最近的数据
    latest_span= temp_df[(temp_df.date>add_date_str(date_param,-15))&(temp_df.date<date_param)]\
                        .sort_values(by='date',ascending=False).head(1)
    if len(latest_span):
        master_field = latest_span.reset_index(drop=True).to_dict(orient='index')[0][field_param]
    else:
        print("函数get_average_index： 在日期"+date_param + "计算"+field_param+"值时出错！")
        return {"date":date_param,
                field_param+"_mean"+str(time_span_param):None}

    # 取“主角日期”与该日期之前“time_span_param”长度的数据的field_param的均值
    span_df = temp_df[(temp_df.date>add_date_str(date_param,-1*time_span_param))&(temp_df.date<date_param)]

    span_mean = span_df[field_param].mean()

    return {"date":date_param,
            field_param+"_mean"+str(time_span_param):span_mean}






def gen_field_ave(df_param,field_list,time_span_list):

    """
    以日期为索引，将volume整理为df均线，封装为一个通用函数。
    即入参为一个dataframe，一个时间跨度，根据这个时间跨度求某个字段的均线，并将结果作为新的字段添加到dataframe中。
    例如：以时间跨度7求字段max的均线。
    field 为list  time_span也是list

    返回的是列增加的dataframe

    :param df_param:
    :param field_list:
    :param time_span_list:
    :return:
    """

    temp_df = df_param

    # 获取date字段
    date_Series = df_param.date


    for field in field_list:
        for time_span in time_span_list:
            ave_dict_df = DataFrame(list(map(lambda x:get_single_ave_by_date(df_param=temp_df,date_param=x,time_span_param=time_span,field_param=field),date_Series)))

            temp_df = pd.merge(temp_df,ave_dict_df,on='date')

    return temp_df



def merge_field_mean(field_list,time_span_list):

    """
    根据field_list 和 time_span_list组合字段名，用于从dataframe中提取相应列

    :param field_list:
    :param time_span_list:
    :return:
    """

    result = list()

    for field in field_list:
        for time_span in time_span_list:
            result.append(field+'_mean'+str(time_span))

    return result



def get_total_volume_ss(code_param,field_list,time_span_list):

    """
    完整获取单个stk的volume数据,ss:single stk

    :param code_param:
    :param field_list:
    :param time_span_list:
    :return:
    """

    tick_df = get_total_table_data(conn_tick, 'tick'+code_param)

    df_merge = gen_field_ave(tick_df, field_list, time_span_list)

    field_list = merge_field_mean(field_list, time_span_list)

    field_list.append('date')

    return df_merge.loc[:, field_list]





# 整理tick数据的范例:

'''
tick_df = get_total_table_data(conn_tick,'tick300508')

df_merge = gen_field_ave(tick_df,['big_in','big_out','total_in','total_out'],[30,60,180])

field_list = merge_field_mean(['big_in','big_out','total_in','total_out'],[30,60,180])

field_list.append('date')

df_tick_result = df_merge.loc[:,field_list]

'''