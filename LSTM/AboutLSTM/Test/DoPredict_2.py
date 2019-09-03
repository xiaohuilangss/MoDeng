# encoding=utf-8
import json

import tensorflow as tf
from pylab import *

from Config.AutoStkConfig import rootPath
from LSTM.AboutLSTM.Config import N_STEPS, feature_cols, HIDDEN_SIZE, NUM_LAYERS
from LSTM.AboutLSTM.Test.Sub import lstm_model

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

"""
实际可用的检测模型训练精度的脚本
"""

""" -------------------- 测试 ---------------------- """


if __name__ == '__main__':

    stk_code = '300508'
    label = 'high'

    # 准备数据
    with open('../DataPrepare/' + stk_code + '/' + stk_code + 'test' + label + '.pkl', 'rb') as f:
        data_train = pickle.load(f)

    tf.reset_default_graph()

    # 创建模型
    predictions, loss, train_op, X, y = lstm_model(
        n_steps=N_STEPS,
        n_inputs=len(feature_cols),
        HIDDEN_SIZE=HIDDEN_SIZE,
        NUM_LAYERS=NUM_LAYERS)

    # 创建保存器用于模型
    saver = tf.train.Saver()

    # 初始化
    sess = tf.Session()
    if os.path.exists('../modelDir/'+stk_code + '_' + label + '/' + stk_code + '_' + label + '.ckpt.meta'):

        saver = tf.train.import_meta_graph(
            '..\modelDir/' + stk_code + '_' + label + '/' + stk_code + '_' + label + '.ckpt.meta')

        saver.restore(sess, tf.train.latest_checkpoint(
            '..\modelDir/' + stk_code + '_' + label + '/'))

        graph = tf.get_default_graph()

        """ ---------------------- 使用模型进行预测 ------------------------- """
        result = [(x[1][-1][0], sess.run([predictions], feed_dict={X: [x[0]]})[0][0][0]) for x in data_train]
        with open(rootPath + '\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
            max_min_info = json.load(f)

        p_max = max_min_info[stk_code][0]
        p_min = max_min_info[stk_code][1]

        result = [(p_min+x[0]*(p_max-p_min), p_min+x[1]*(p_max-p_min)) for x in result]

        """ -------------------------- 画图展示预测效果 -------------------- """
        fig, ax = plt.subplots(nrows=1)
        ax_x = list(range(len(result)))
        ax.plot(ax_x, [x[1] for x in result], 'g*--', label='原始数据')
        ax.plot(ax_x, [x[0] for x in result], 'r*--', label='预测数据')

        plt.legend(loc='best')
        plt.show()

        end = 0

    else:
        print('lstm模型加载不成功！')