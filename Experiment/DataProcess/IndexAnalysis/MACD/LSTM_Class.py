# encoding = utf-8

import tensorflow as tf
from tensorflow.contrib import rnn


def LSTM():



    _X = tf.placeholder(tf.float32, [None, timestep_size, input_size], name='x')
    y = tf.placeholder(tf.float32, [None, output_size], name='y')
    keep_prob = tf.placeholder(tf.float32, name='keep_prob')


    # -----------------------------------（二）搭建LSTM 模型 ------------------------------------------------
    lr = 1e-3

    X = tf.reshape(_X, [-1, input_size, timestep_size])

    def unit_lstm():
        # 定义一层 LSTM_cell，只需要说明 hidden_size, 它会自动匹配输入的 X 的维度
        lstm_cell = rnn.BasicLSTMCell(num_units=hidden_size, forget_bias=1.0, state_is_tuple=True)

        #添加 dropout layer, 一般只设置 output_keep_prob
        lstm_cell = rnn.DropoutWrapper(cell=lstm_cell, input_keep_prob=1.0, output_keep_prob=keep_prob)
        return lstm_cell


    #调用 MultiRNNCell 来实现多层 LSTM
    mlstm_cell = rnn.MultiRNNCell([unit_lstm() for i in range(3)], state_is_tuple=True)

    #用全零来初始化state
    init_state = mlstm_cell.zero_state(batch_size, dtype=tf.float32)
    outputs, state = tf.nn.dynamic_rnn(mlstm_cell, inputs=X, initial_state=init_state, time_major=False)
    h_state = outputs[:, -1, :]  # 或者 h_state = state[-1][1]


    # -----------------------------------（三）设置 loss function 和 优化器 -------------------------------------

    # 定义输出结果的权重矩阵及偏值
    W = tf.Variable(tf.truncated_normal([hidden_size, class_num], stddev=0.1), dtype=tf.float32)
    bias = tf.Variable(tf.constant(0.1,shape=[class_num]), dtype=tf.float32)

    # 计算输出结果
    y_pre = tf.add(tf.matmul(h_state, W),bias,name='y_pre')

    # y_pre = tf.map_fn(fn=lambda x:x[timestep_size-1],elems=y_pre_total)


    # 损失和评估函数
    # cross_entropy = -tf.reduce_mean(y * tf.log(y_pre))
    # train_op = tf.train.AdamOptimizer(lr).minimize(cross_entropy)
    # correct_prediction = tf.equal(tf.argmax(y_pre,1), tf.argmax(y,1))
    # accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float32"))


    cross_entropy = tf.reduce_mean(tf.abs(tf.subtract(y,y_pre)),name='cross_entropy')
    train_op = tf.train.AdamOptimizer(lr).minimize(cross_entropy,name='train_op')


    # tf.argmax(input, axis=None, name=None, dimension=None)：
    # 此函数是对矩阵按行或列计算最大值
