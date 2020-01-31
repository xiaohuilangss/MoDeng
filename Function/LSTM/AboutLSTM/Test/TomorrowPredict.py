# encoding=utf-8
import json
import os

import tushare as ts

from Function.GUI.Sub.sub import text_append_color
from Function.LSTM.AboutLSTM.Config import feature_cols, N_STEPS, HIDDEN_SIZE, NUM_LAYERS
from Function.LSTM.AboutLSTM.Test.Sub import lstm_model
import tensorflow as tf
from pylab import *

from Global_Value.file_dir import rootPath
from SDK.DataPro import relativeRank
from SDK.MyTimeOPT import get_current_date_str, add_date_str
from SDK.SendMsgByQQ.QQGUI import send_qq


"""
本脚本实现调用model预测tomorrow的high点 

"""

def predict_tomorrow(
        stk_code,
        label,
        N_STEPS=N_STEPS,
        feature_cols=feature_cols,
        HIDDEN_SIZE=HIDDEN_SIZE,
        NUM_LAYERS=NUM_LAYERS
):

    """

    :param stk_code:    例子 '300508'
    :param label:       例子 'high'
    :param N_STEPS:
    :param feature_cols:
    :param HIDDEN_SIZE:
    :param NUM_LAYERS:
    :return:
    """

    """ ---------------------- 读取json中存储的极值 ---------------------- """
    with open(rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
        max_min_info = json.load(f)

    """ ---------------------- 获取实时数据 ---------------------- """
    data_now = ts.get_k_data(stk_code)[-(N_STEPS+30):]

    # 增加M9 Rank
    data_now['m9'] = data_now['close'].rolling(window=9).mean()
    data_now['diff_m9'] = data_now.apply(lambda x: (x['close'] - x['m9']) / x['close'], axis=1)
    data_now['rank'] = data_now.apply(lambda x: relativeRank(max_min_info[stk_code]['m9_history'], x['diff_m9']), axis=1)

    # rootPath = 'C:/Users\paul\Desktop\软件代码\Git-Clone'

    for c in ['close', 'high', 'low', 'open']:
        data_now[c] = (data_now[c].values - max_min_info[stk_code]['p_min'])/(max_min_info[stk_code]['p_max'] - max_min_info[stk_code]['p_min'])

    data_now['volume'] = (data_now['volume'].values - max_min_info[stk_code]['v_min'])/(max_min_info[stk_code]['v_max'] - max_min_info[stk_code]['v_min'])

    # 进行归一化
    input_normal = data_now.loc[:, feature_cols].tail(20).values

    tf.reset_default_graph()

    """ ---------------------- 创建模型 ---------------------- """
    predictions, loss, train_op, X, y = lstm_model(
        n_steps=N_STEPS,
        n_inputs=len(feature_cols),
        HIDDEN_SIZE=HIDDEN_SIZE,
        NUM_LAYERS=NUM_LAYERS)

    # 创建保存器用于模型
    saver = tf.train.Saver()

    # 初始化
    sess = tf.Session()
    model_name = stk_code + '_' + label
    model_dir = rootPath + 'Function\LSTM\AboutLSTM\modelDir/'

    if os.path.exists(model_dir + model_name + '/' + model_name + '.ckpt.meta'):

        saver = tf.train.import_meta_graph(
            model_dir + model_name + '/' + model_name + '.ckpt.meta')
        saver.restore(sess, tf.train.latest_checkpoint(
            model_dir + model_name + '/'))

        # graph = tf.get_default_graph()
        # 防报错
        tf.reset_default_graph()

        r_rela = sess.run([predictions], feed_dict={X: [input_normal]})[0][0][0]

        return max_min_info[stk_code]['p_min'] + (max_min_info[stk_code]['p_max'] - max_min_info[stk_code]['p_min'])*r_rela

    else:
        print('加载模型' + model_name + '失败！')
        return -1


def predict_tomorrow_index(tc, debug=False):

    try:

        with open(rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
            max_min_info = json.load(f)

        stk2name = {
            'sh': '上证',
            'sz': '深证',
            'cyb': '创业板'
        }

        for stk in ['sh', 'sz', 'cyb']:

            today_df = ts.get_k_data(stk).tail(1)

            text_append_color(tc, stk2name.get(stk) + ' 今天数据：\n' + today_df.to_string()
                          .replace('volume', '成交量')
                          .replace('date', '日期')
                          .replace('open', '开盘价')
                          .replace('high', '最高点')
                          .replace('low', '最低点')
                          .replace('close', '收盘价') + '\n\n')

            close_today = today_df['close'].values[0]
            r = [(label, '%0.2f' % predict_tomorrow(
                stk,
                label,
                N_STEPS=N_STEPS,
                feature_cols=feature_cols,
                HIDDEN_SIZE=HIDDEN_SIZE,
                NUM_LAYERS=NUM_LAYERS), max_min_info[stk][label + '_acc']) for label in ['high', 'low', 'close']]

            # 增加与今天收盘价的对比
            r_contrast = [(x[0], x[1], '%0.2f' % ((float(x[1])-close_today)/close_today*100) + '%') for x in r]

            text_append_color(tc, stk2name[stk] + '明日预测:\n' + str(r_contrast)
                          .replace('high', '最高点')
                          .replace('low', '最低点')
                          .replace('close', '收盘价') + '\n\n')
    except Exception as e:
        text_append_color(tc, '预测明日大盘操作失败！原因：\n' + str(e))


def printPredict2Public():

    with open(rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
        max_min_info = json.load(f)

    for stk in ['sh', 'sz', 'cyb']:

        today_df = ts.get_k_data(stk).tail(1)
        # send_qq(towho, stk + ' 今天数据：\n' + str(today_df) + '\n')
        print(stk + ' 今天数据：\n' + str(today_df) + '\n')
        close_today = today_df['close'].values[0]
        r = [(label, '%0.2f' % predict_tomorrow(
            stk,
            label,
            N_STEPS=N_STEPS,
            feature_cols=feature_cols,
            HIDDEN_SIZE=HIDDEN_SIZE,
            NUM_LAYERS=NUM_LAYERS), max_min_info[stk][label + '_acc']) for label in ['high', 'low', 'close']]

        # 增加与今天收盘价的对比
        r_contrast = [(x[0], x[1], '%0.2f' % ((float(x[1])-close_today)/close_today*100) + '%', x[2]) for x in r]
        stk2name = {
            'sh': '上证',
            'sz': '深证',
            'cyb': '创业板'
        }
        print(stk2name[stk] + '明日预测:\n' + str(r_contrast))
        # send_qq(towho, stk2name[stk] + '明日预测:\n' + str(r_contrast))


def printConcernedPredict2Self():

    towho = u'影子2'

    for stk in ['000001', '000333', '300508']:
        close_today = ts.get_k_data(stk, start=add_date_str(get_current_date_str(), -5)).tail(1)['close'].values[0]

        r = [(label, '%0.2f' % predict_tomorrow(
            stk,
            label,
            N_STEPS=N_STEPS,
            feature_cols=feature_cols,
            HIDDEN_SIZE=HIDDEN_SIZE,
            NUM_LAYERS=NUM_LAYERS)) for label in ['high', 'low', 'close']]

        # 增加与今天收盘价的对比
        r_contrast = [(x[0], x[1], '%0.2f' % ((float(x[1])-close_today)/close_today*100) + '%') for x in r]

        # stk2name = {
        #     'sh': '上证',
        #     'sz': '深证',
        #     'cyb': '创业板'
        # }

        print(stk + ':\n' + str(r_contrast))

        send_qq(towho, stk + ':\n' + str(r_contrast))


if __name__ == '__main__':

    printPredict2Public()
    # printConcernedPredict2Self()
    end = 0

    # for stk in ['sh', 'sz', 'cyb']:
    #
    #     r = [(label, '%0.2f' % predict_tomorrow(
    #         stk,
    #         label,
    #         N_STEPS=N_STEPS,
    #         feature_cols=feature_cols,
    #         HIDDEN_SIZE=HIDDEN_SIZE,
    #         NUM_LAYERS=NUM_LAYERS)) for label in ['high', 'low', 'close']]
    #
    #     print(stk + ':' + str(r))
