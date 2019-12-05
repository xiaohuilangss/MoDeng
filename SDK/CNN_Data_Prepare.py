# encoding = utf-8

from Config.GlobalSetting import stk_tick_data_db_name
from SDK.DBOpt import is_table_exist
from SDK.AveAnalysisSub import get_average_array_span, add_inc, get_total_ave_ss
import pandas as pd
import numpy as np
from SDK.FileOptSub import read_csv_to_df
from SDK.TickAnalysisSub import get_total_volume_ss
import os
import tushare as ts
'''
                                8           9           10
close                       26.927      28.223      28.223
close_max7                  26.927         NaN      28.223
close_mean7                 25.769         NaN      28.223
close_min7                  24.996         NaN      28.223
date                    2015-02-17  2015-02-25  2015-02-26
close_max14                 27.068      28.223      28.223
close_mean14               25.8927     26.4172      27.224
close_min14                 24.835      24.996      25.523
close_max30                 27.068      28.223      28.223
close_mean30               25.8927     26.1257     26.3164
close_min30                 24.835      24.835      24.835
close_max60                 27.068      28.223      28.223
close_mean60               25.8927     26.1257     26.3164
close_min60                 24.835      24.835      24.835
close_max180                27.068      28.223      28.223
close_mean180              25.8927     26.1257     26.3164
close_min180                24.835      24.835      24.835
close_mean30_future20      26.9179     27.0767     27.3171
close_mean30_inc_ratio   0.0395939   0.0363997   0.0380281
'''



def prepare_cnn_data_to_csv_ave(code_param, inc_time_span_param, file_save_url_param):


    """
    根据k数据整理衍生相应指标（均线，作为label的未来inc），并整理为列，存入csv中。
    :param code_param:
    :param inc_time_span_param:
    :param file_save_url_param:
    :return:
    """

    # 获取stk的k数据
    # k_df = get_total_table_data(conn_k, 'k' + code_param)
    k_df = ts.get_k_data(code_param)

    # 获取均线
    ave_origin = get_average_array_span(k_df, [7, 14, 30, 60, 180], 'close')

    # 添加m30inc,前提是数据长度超过的时间轴上的前瞻距离
    if len(ave_origin) > inc_time_span_param:
        ave_with_m30inc = add_inc(ave_origin, 'close_mean30', inc_time_span_param)

        # 将df数据保存为csv
        ave_with_m30inc.to_csv(file_save_url_param, index=False)




def convert_df_to_cnn_format(data_df_param,col_label_param,col_feature_param,feature_len_param):
    """
    将df整理成cnn训练数据的格式

    返回dict列表的形式，dict有两个字段：“image”和“label”

    :param data_df_param:
    :param col_label_param:
    :param col_feature_param:
    :param feature_len_param:
    :return:
    """

    # 根据列来选出dataframe中有用的部分
    data_df_relative = data_df_param.loc[:,col_feature_param+col_label_param]

    # 如果某一天的数据有nan，果断弃之！
    data_df_relative = data_df_relative.dropna().reset_index(drop=True)

    example_amount = data_df_relative.shape[0] - feature_len_param + 1

    # 用于存储结果的list对象
    result_dict_list = []

    # 遍历得到image和label
    for index in range(0,example_amount):
        try:
            image_dense = data_df_relative.loc[index:index+feature_len_param-1,col_feature_param].T.values
            label_dense = data_df_relative.loc[index + feature_len_param - 1,col_label_param].T.values
            result_dict_list.append({"image": normalize_by_line(image_dense), "label": label_dense})
        except:
            print("函数convert_df_to_cnn_format：遍历得到image和label遇到异常！")


    return result_dict_list



def grade(value_param):

    """
    根据增长率将数据分为六个档：
    0：大跌
    1：中等下跌
    2：微跌
    3：微张
    4：中等上涨
    5：大涨
    :param value_param:
    :return:
    """


    if value_param < -10:
        return 0
    elif -4 > value_param >= -10:
        return 1
    elif 0 > value_param >= -4:
        return 2
    elif 4 > value_param >= 0:
        return 3
    elif 10 > value_param >= 4:
        return 4
    elif value_param >= 10:
        return 5


def gaussian_normalize(value_param):

    """
    将数据进行高斯归一化,返回类型为np.array()
    :param value_param:
    :return:
    """

    if isinstance(value_param, pd.Series):
        value_temp = np.array(value_param)
    elif isinstance(value_param, np.ndarray):
        value_temp = value_param
    elif isinstance(value_param, list):
        value_temp = np.array(value_param)
    else:
        print("函数 gaussian_normalize：不识别的入参类型！")
        return value_param

    return (value_temp - np.mean(value_temp))/np.cov(value_temp)


def normalize_by_line(value_param):

    """
    按行归一化一个矩阵

    :param value_param:
    :return:
    """

    if isinstance(value_param, np.ndarray):
        return np.array(list(map(lambda x: gaussian_normalize(x), value_param)))
    else:
        print("函数 normalize_by_line:遇到不识别的入参类型，将入参原路返回！")
        return value_param


def batch_gen_cnn_data(code_list,inc_ratio_time_span,field_list,time_span_list,file_save_dir):

    """
    “批存储”
    根据代码列表将数据按合适的格式存到指定文件夹,
    有些stk天数不够，但在此函数里没有考虑这一问题，所以在读取的时候应该根据此条件进行筛选
    @param field_list  volume df中需要求均值的字段

    :param code_list:
    :param inc_ratio_time_span:
    :param field_list:
    :param time_span_list:
    :param file_save_dir:
    :return:
    """

    for code in code_list:

        csv_name = file_save_dir + str(code) + "CNN_Data.csv"

        # “数据库里面存在这个表”,且“目标文件不存在”的时候，才能继续操作
        if is_table_exist(conn_tick, stk_tick_data_db_name, 'tick'+code) & (not os.path.exists(csv_name)):

            # 获取均值数据
            df_ave = get_total_ave_ss(code, inc_ratio_time_span)

            # 获取volume数据
            df_volume = get_total_volume_ss(code, field_list, time_span_list)

            df_total = pd.merge(df_ave, df_volume, on='date')

            df_total.to_csv(csv_name)

        else:
            print("函数batch_gen_cnn_data：tick"+code+" 表不存在，或者目标csv文件已经存在，函数返回空！")



def batch_gen_cnn_data_only_ave(code_list, inc_ratio_time_span, file_save_dir):

    """
    “批存储2”
    根据  “代码列表”  将数据按    “合适的格式” 存到  “指定文件夹”,
    有些stk天数不够，但在此函数里没有考虑这一问题，所以在读取的时候应该根据此条件进行筛选
    @param field_list  volume df中需要求均值的字段

    :param code_list:
    :param inc_ratio_time_span:
    :param file_save_dir:
    :return:
    """

    for code in code_list:

        csv_name = file_save_dir + str(code) + "CNN_Data.csv"

        # “数据库里面存在这个表”,且“目标文件不存在”的时候，才能继续操作
        if is_table_exist(conn_tick, stk_tick_data_db_name, 'tick' + code) & (not os.path.exists(csv_name)):

            # 获取均值数据
            df_ave = get_total_ave_ss(code, inc_ratio_time_span)
            df_ave.to_csv(csv_name)

        else:
            print("函数batch_gen_cnn_data：tick" + code + " 表不存在，或者目标csv文件已经存在，函数返回空！")





def merge_batch_from_csv(code_list,threshold_amount,label_field_list,feature_field_list,feature_length,file_save_dir):

    """
    “批读取合并”
    根据代码列表从csv中读取数据，合并为一个大的list，用以训练cnn网络
    label_field_list  例如：["close_mean30_inc_ratio"]
    feature_field_list 例如：["close_mean14","close_mean30","close_mean60","close_mean180"]

    :param code_list:
    :param threshold_amount:
    :param label_field_list:
    :param feature_field_list:
    :param feature_length:
    :param file_save_dir:
    :return:
    """

    result = list()

    for code in code_list:
        csv_name = file_save_dir + str(code) + "CNN_Data.csv"

        # 如果路径下存在这个文件，才能去读
        if os.path.exists(csv_name):
            single_stk = read_csv_to_df(csv_name)

            # 判断该stk的数据量是否合格，即是否大于指定值"threshold amount",数据足够，则合并到结果中
            if len(single_stk) > threshold_amount:

                    result.extend(convert_df_to_cnn_format(single_stk,label_field_list,feature_field_list,feature_length))

    return result



# ----------------------函数测试用---------------------------
# a = np.array([[3,6,2,4],[5,2,6,2],[89,3,74,4]])
# type(a)
# b = normalize_by_line(a)
#
# end = 0
# save_dir = "F:/MYAI/文档资料/用于读取的文件/data_for_cnn/"
# batch_gen_cnn_data(g_total_stk_code[0:200],20,save_dir)