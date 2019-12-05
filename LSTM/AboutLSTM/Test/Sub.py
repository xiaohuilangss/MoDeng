# encoding = utf-8
import tensorflow as tf
import numpy as np
import pandas as pd

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


def lstm_model(n_steps, n_inputs, HIDDEN_SIZE, NUM_LAYERS):

    """

    :param n_steps:
    :param n_inputs:
    :param HIDDEN_SIZE:
    :param NUM_LAYERS:
    :return:
    """

    cell = tf.nn.rnn_cell.MultiRNNCell(
        [tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE) for _ in range(NUM_LAYERS)]
    )

    X = tf.placeholder(tf.float32, [None, n_steps, n_inputs], name='ipt')
    y = tf.placeholder(tf.float32, [None, 1], name='opt')

    """
    使用tf自带接口将多层LSTM连接成RNN网络，并计算前向结果
    outputs 的维度是：[batch_size, time, HIDDEN_SIZE]
    """
    outputs, _ = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)

    """ 在实例中我们只取预测数据的最后一个 """
    output = outputs[:, -1, :]

    """ 增加一层全连接层作为输出 """
    predictions = tf.contrib.layers.fully_connected(output, 1, activation_fn=None)

    """定义损失 """
    loss = tf.losses.mean_squared_error(labels=y, predictions=predictions)

    """ 创建优化器并得到优化步骤 """
    train_op = tf.contrib.layers.optimize_loss(
        loss,
        tf.train.get_global_step(),
        optimizer='Adagrad',
        learning_rate=0.1,
        name='optimize'
    )

    return predictions, loss, train_op, X, y
