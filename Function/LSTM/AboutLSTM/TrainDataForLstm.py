# encoding=utf-8

"""
本脚本用以生成lstm训练用的数据
"""
import json
import math
import tushare as ts
import pickle

from Experiment.Capital_Flow import get_stk_money_flow
from CornerDetectAndAutoEmail.Sub import genSingleStkTrainData, sliceDfToTrainData
from LSTM.AboutLSTM.Config import feature_cols, label_col, N_STEPS
from RelativeRank.Sub import relativeRank
from sdk.CNN_Data_Prepare import gaussian_normalize, normalize
import numpy as np
import os

import pandas as pd

json_max_min_info = {}


def genTrainDataHL(stk_code, start_time, N_STEPS, feature_cols, label_col, data_store_dir):
    """
    第二天高低点的判断
    :param stk_code:
    :param start_time:
    :param data_store_dir:       './DataPrepare/'
    :return:
    """

    df_cyb = ts.get_k_data(stk_code, start=start_time)
    df = df_cyb

    # 测试相对均值偏移度
    df['m9'] = df['close'].rolling(window=9).mean()
    df['diff_m9'] = df.apply(lambda x: (x['close'] - x['m9']) / x['close'], axis=1)

    df['rank'] = df.apply(lambda x: relativeRank(df['diff_m9'], x['diff_m9']), axis=1)

    # 计算标签的环比变化率
    df[label_col[0] + '_tomorrow'] = df[label_col[0]].shift(-1)

    # 删除空值
    df = df.dropna(how='any')

    # 对open、 close、high、 low进行归一化，对volume单独归一化
    p_min = np.min(df.loc[:, ['open', 'close', 'high', 'low']].values)
    p_max = np.max(df.loc[:, ['open', 'close', 'high', 'low']].values)

    v_min = np.min(df.loc[:, ['volume']].values)
    v_max = np.max(df.loc[:, ['volume']].values)

    # 保存数据的极值情况
    global json_max_min_info
    json_max_min_info[stk_code] = \
        {
            'p_max': p_max,
            'p_min': p_min,
            'v_max': v_max,
            'v_min': v_min,
            'm9_history': list(df['diff_m9'].values)
        }

    for c in ['close', 'high', 'low', 'open', label_col[0] + '_tomorrow']:
        df[c] = (df[c].values - p_min)/(p_max - p_min)

    df['volume'] = (df['volume'].values - v_min)/(v_max - v_min)

    # 与capital进行合并
    # df_cap = get_stk_money_flow(stk_code, start_date, end_date=None)

    # df = pd.concat([df.set_index(keys='date'), df_cap], axis=1)

    # 二次删除空值
    df = df.dropna(how='any')

    # 对数据进行切片
    data_slice_list_norm = sliceDfToTrainData(
        df=df,
        length=N_STEPS-1,
        feature_cols=feature_cols,
        label_col=[label_col[0]+'_tomorrow'],
        norm_flag=False
    )

    # 将数据分割为训练集和数据集
    lenth = math.floor(len(data_slice_list_norm)*0.8)
    list_train = data_slice_list_norm[:lenth]
    list_test = data_slice_list_norm[lenth:]

    if not os.path.exists(data_store_dir):
        os.makedirs(data_store_dir)

    # 保存数据
    with open(data_store_dir + stk_code + 'train' + label_col[0] + '.pkl', 'wb') as f:
        pickle.dump(list_train, f)

    with open(data_store_dir + stk_code + 'test' + label_col[0] + '.pkl', 'wb') as f:
        pickle.dump(list_test, f)


if __name__ == '__main__':

    with open('./stk_max_min.json', 'r') as f:
        json_max_min_info = json.load(f)

    for stk_code in ['sh', 'sz', 'cyb', '000001', '300508']:

        start_date = '2009-05-01'

        genTrainDataHL(stk_code=stk_code,
                       start_time=start_date,
                       N_STEPS=N_STEPS,
                       feature_cols=feature_cols,
                       label_col=['low'],
                       data_store_dir='./DataPrepare/'+stk_code+'/')

        genTrainDataHL(stk_code=stk_code,
                       start_time=start_date,
                       N_STEPS=N_STEPS,
                       feature_cols=feature_cols,
                       label_col=['high'],
                       data_store_dir='./DataPrepare/'+stk_code+'/')

        genTrainDataHL(stk_code=stk_code,
                       start_time=start_date,
                       N_STEPS=N_STEPS,
                       feature_cols=feature_cols,
                       label_col=['close'],
                       data_store_dir='./DataPrepare/'+stk_code+'/')

    # 保存极值信息
    with open('./stk_max_min.json', 'w') as f:
        json.dump(json_max_min_info, f)