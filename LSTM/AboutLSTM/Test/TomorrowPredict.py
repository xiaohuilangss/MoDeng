# encoding=utf-8
import json

import tushare as ts
import os
from Config.AutoStkConfig import rootPath
from Experiment.RelativeRank.Sub import relativeRank
from LSTM.AboutLSTM.Config import feature_cols, N_STEPS, HIDDEN_SIZE, NUM_LAYERS
from LSTM.AboutLSTM.Test.Sub import lstm_model
# from RelativeRank.Sub import relativeRank
import tensorflow as tf
from pylab import *

from SDK.MyTimeOPT import get_current_date_str, add_date_str
from SendMsgByQQ.QQGUI import send_qq


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
    with open(rootPath + '\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
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
    model_dir = rootPath + '\LSTM\AboutLSTM\modelDir/'

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


def printPredict2Public():

    towho = u'影子'
    send_qq(towho, '各位：\n以下是下一个交易日大盘最高价、最低价和收盘价的预测，因为三个价格使用相互独立的模型，所以会出现收盘价低于最低价的情况，以及类似的情形，希望各位注意！' +
                         '\n' +
                         '周一~周五 晚上19：30 计算并发送该消息！\n格式及解释：\n' +
            "('high', '2989.57','0.11%')" + '\n' +
            '最高价, 2989.57, 相对于上一个收盘价的涨跌率 0.11, 训练时误差 0.852\n后面以此类推...'
            )

    with open(rootPath + '\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
        max_min_info = json.load(f)

    for stk in ['sh', 'sz', 'cyb']:

        today_df = ts.get_k_data(stk).tail(1)
        send_qq(towho, stk + ' 今天数据：\n' + str(today_df) + '\n')
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

        send_qq(towho, stk2name[stk] + '明日预测:\n' + str(r_contrast))


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
