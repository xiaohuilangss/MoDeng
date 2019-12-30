# encoding=utf-8

"""
本脚本用来测试书上的LSTM代码

"""
import json

import tensorflow as tf
import numpy as np
import pickle
import random
import os
import time


from Function.LSTM.AboutLSTM.Config import N_STEPS, feature_cols, HIDDEN_SIZE, NUM_LAYERS
from Function.LSTM.AboutLSTM.Test.Sub import lstm_model

from Global_Value.file_dir import rootPath

""" -------------------- 测试 ---------------------- """


def train(data_train, times, model_dir, model_name, N_STEPS, feature_cols, HIDDEN_SIZE, NUM_LAYERS):
    """

    :param times:               训练次数
    :param model_dir:           模型路径        例如：'..\modelDir/'
    :param model_name:          模型名称
    :return:
    """
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
    if os.path.exists(model_dir + model_name + '/' + model_name + '.ckpt.meta'):

        saver = tf.train.import_meta_graph(
            model_dir + model_name + '/' + model_name + '.ckpt.meta')

        saver.restore(sess, tf.train.latest_checkpoint(
            model_dir + model_name + '/'))

        graph = tf.get_default_graph()
    else:
        sess.run(tf.global_variables_initializer())

    loss_list = []
    t_s = time.time()       # 起始时间
    loss_list_accuracy = []

    for i in range(times):

        # 从总样本中随机抽取,batch_size = 7
        list_sample = random.sample(data_train, 7)

        input = [x[0] for x in list_sample]
        output = np.reshape([x[1][-1] for x in list_sample], newshape=[-1, 1])

        _, _, l = sess.run([predictions, train_op, loss], feed_dict={X: input, y: output})

        # 保存最后1000个误差，取均值，作为本次训练的误差
        if i > times-1000:
            loss_list_accuracy.append(l)

        loss_list.append(l)

        if len(loss_list) > 100:

            print('本次损失为：' + str(np.mean(loss_list)))
            loss_list = []

    print('总耗时：' + '%0.2f' % ((time.time() - t_s) / 60) + '分钟')

    # 保存模型
    saver.save(sess=sess, save_path=model_dir + model_name + '/' + model_name + '.ckpt')

    # 返回本次训练的误差
    return np.mean(loss_list_accuracy)


def train_main(stk_code, times):

    for label in ['low', 'close', 'high']:

        data_dir = '../DataPrepare/' + stk_code + '/'

        # 准备数据
        with open(data_dir + stk_code + 'train' + label + '.pkl', 'rb') as f:
            data_train = pickle.load(f)

        acc = train(
            data_train=data_train,
            times=times,
            model_dir='..\modelDir/',
            model_name=stk_code+'_'+label,
            N_STEPS=N_STEPS,
            feature_cols=feature_cols,
            HIDDEN_SIZE=HIDDEN_SIZE,
            NUM_LAYERS=NUM_LAYERS)

        # 将本次训练的精度写入json文件
        with open(rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
            json_max_min_info = json.load(f)

        if stk_code in json_max_min_info.keys():
            json_max_min_info[stk_code][label+'_acc'] = '%0.3f' % (acc*10000)
        else:
            json_max_min_info[stk_code] = {label+'_acc': '%0.3f' % (acc*10000)}

        with open(rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json', 'w') as f:
            json.dump(json_max_min_info, f)


if __name__ == '__main__':

    for ts in range(10):
        for stk in ['sz', 'sh', 'cyb']:
            train_main(stk, 300000)
            print('完成' + stk + '的第' + str(ts) + '训练任务！')
            # send_qq(u'影子', '完成' + stk + '的第' + str(ts) + '训练任务！')

    # stk_code = 'sh'
    # label = 'high'
    # times = 300000*3
    #
    # data_dir = '../DataPrepare/' + stk_code + '/'
    #
    # # 准备数据
    # with open(data_dir + stk_code + 'train' + label + '.pkl', 'rb') as f:
    #     data_train_high = pickle.load(f)
    #
    # train(
    #     data_train=data_train_high,
    #     times=times,
    #     model_dir='..\modelDir/',
    #     model_name=stk_code + '_' + label,
    #     N_STEPS=N_STEPS,
    #     feature_cols=feature_cols,
    #     HIDDEN_SIZE=HIDDEN_SIZE,
    #     NUM_LAYERS=NUM_LAYERS)

