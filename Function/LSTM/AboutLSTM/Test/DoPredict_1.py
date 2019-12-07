# encoding = utf-8
import tushare as ts


from LSTM.AboutLSTM.Config import feature_cols, M_INT, N_STEPS, N_INPUTS, HIDDEN_SIZE, NUM_LAYERS, label_col
from LSTM.AboutLSTM.Test.Sub import lstm_model

import tensorflow as tf
import os
import numpy as np
from pylab import *
import pickle

""" 本脚本根据训练好的lstm模型进行预测 """


""" -------------------- 测试 ---------------------- """
stk_code = 'cyb'

# 准备数据
with open('../DataPrepare/' + stk_code+'test' + '.pkl', 'rb') as f:
    list = pickle.load(f)

""" -------------------------- 加载lstm模型进行预测 --------------------------- """

# 创建模型
predictions, loss, train_op, X, y = lstm_model(
    n_steps=N_STEPS,
    n_inputs=N_INPUTS,
    HIDDEN_SIZE=HIDDEN_SIZE,
    NUM_LAYERS=NUM_LAYERS)

# 创建保存器用于模型
saver = tf.train.Saver(tf.global_variables())

# 初始化
sess = tf.Session()
if os.path.exists('../modelDir/300508/300508_high.ckpt.meta'):

    saver = tf.train.import_meta_graph(
        '..\modelDir/300508/300508_high.ckpt.meta')
    saver.restore(sess, tf.train.latest_checkpoint(
        '..\modelDir/300508/'))

    # graph = tf.get_default_graph()

    """ ---------------------- 使用模型进行预测 ------------------------- """
    result = list(map(lambda x: (x[1][-1], sess.run([predictions], feed_dict={X: x[0]})[0][0][0]),list))

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

