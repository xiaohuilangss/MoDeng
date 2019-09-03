# encoding = utf-8

from SDK.SDKHeader import *
from DataProcess.IndexAnalysis.MACD.DataPrepareSub import *

# %matplotlib inline
import tensorflow as tf
from tensorflow.contrib import rnn
# import scipy
import numpy as np

config = tf.ConfigProto()
sess = tf.Session(config=config)



# ----------------------------------- 定义参数 ------------------------------------------------

lr = 1e-3
_batch_size = 30

# 每个时刻的输入特征是28维的，就是每个时刻输入一行，一行有 28 个像素
input_size = 8

# 时序持续长度为28，即每做一次预测，需要先输入28行
timestep_size = 30

# 每个隐含层的节点数0
hidden_size = 64

# LSTM layer 的层数
layer_num = 2

# 最后输出分类类别数量，如果是回归预测的话应该是 1
class_num = 1


# ----------------------------- 判断模型是否已经存在，若存在，则加载 ------------------------------

if os.path.exists('./Model/LstmModel1.ckpt.meta'):

    # 从保存的模型中加载“图”和“参数”
    saver = tf.train.import_meta_graph('./Model/' + 'LstmModel1.ckpt.meta')
    saver.restore(sess, tf.train.latest_checkpoint('./Model/'))

    graph = tf.get_default_graph()

    # 恢复相应参数的值
    _X = graph.get_tensor_by_name("x:0")
    y = graph.get_tensor_by_name("y:0")
    cross_entropy = graph.get_tensor_by_name("cross_entropy:0")
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    batch_size = graph.get_tensor_by_name("batch_size:0")
    y_pre = graph.get_tensor_by_name("y_pre:0")
    train_op = graph.get_operation_by_name("train_op")

else:

    # ----------------------------------- 定义超参数 ------------------------------------------------

    # 在训练和测试的时候，我们想用不同的 batch_size.所以采用占位符的方式
    batch_size = tf.placeholder(tf.int32, [], name='batch_size')

    _X = tf.placeholder(tf.float32, [None, timestep_size, input_size], name='x')
    y = tf.placeholder(tf.float32, [None, class_num], name='y')
    keep_prob = tf.placeholder(tf.float32, name='keep_prob')


    # ----------------------------------- 搭建LSTM 模型 ------------------------------------------------

    # 把784个点的字符信息还原成 28 * 28 的图片
    # 下面几个步骤是实现 RNN / LSTM 的关键
    X = tf.reshape(_X, [-1, input_size, timestep_size])


    # X_std = tf.map_fn(fn=lambda x:tf.nn.l2_normalize(x,1),elems=X)
    def unit_lstm():

        # 定义一层 LSTM_cell，只需要说明 hidden_size, 它会自动匹配输入的 X 的维度
        lstm_cell = rnn.BasicLSTMCell(num_units=hidden_size, forget_bias=1.0, state_is_tuple=True)

        # 添加 dropout layer, 一般只设置 output_keep_prob
        lstm_cell = rnn.DropoutWrapper(cell=lstm_cell, input_keep_prob=1.0, output_keep_prob=keep_prob)
        return lstm_cell


    # 调用 MultiRNNCell 来实现多层 LSTM
    mlstm_cell = rnn.MultiRNNCell([unit_lstm() for i in range(3)], state_is_tuple=True)

    # 用全零来初始化state
    init_state = mlstm_cell.zero_state(batch_size, dtype=tf.float32)
    outputs, state = tf.nn.dynamic_rnn(mlstm_cell, inputs=X, initial_state=init_state, time_major=False)
    h_state = outputs[:, -1, :]  # 或者 h_state = state[-1][1]

    # ----------------------------------- 设置 loss function 和 优化器 -------------------------------------

    # 定义输出结果的权重矩阵及偏值
    W = tf.Variable(tf.truncated_normal([hidden_size, class_num], stddev=0.1), dtype=tf.float32)
    bias = tf.Variable(tf.constant(0.1, shape=[class_num]), dtype=tf.float32)

    # 计算输出结果
    y_pre = tf.add(tf.matmul(h_state, W), bias, name='y_pre')

    # y_pre = tf.map_fn(fn=lambda x:x[timestep_size-1],elems=y_pre_total)

    # 损失和评估函数
    # cross_entropy = -tf.reduce_mean(y * tf.log(y_pre))
    # train_op = tf.train.AdamOptimizer(lr).minimize(cross_entropy)
    # correct_prediction = tf.equal(tf.argmax(y_pre,1), tf.argmax(y,1))
    # accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float32"))

    cross_entropy = tf.reduce_mean(tf.abs(tf.subtract(y, y_pre)), name='cross_entropy')
    train_op = tf.train.AdamOptimizer(lr).minimize(cross_entropy, name='train_op')

    # tf.argmax(input, axis=None, name=None, dimension=None)：
    # 此函数是对矩阵按行或列计算最大值

    # 创建保存器用于模型
    saver = tf.train.Saver()
    sess.run(tf.global_variables_initializer())


# -----------------------------------（四）开始训练 -------------------------------------

# 获取stk与class的映射信息
belongto = get_stk_belongto_info()

# 获取各个class信息
class_df_list = get_class_df()


for j in range(0,30):

    i= 0
    for stk in g_total_stk_code:

        # 获取该stk所对应的
        class_df = get_class_df_by_code(code=stk, belongto_info=belongto, class_df_list=class_df_list)
        batch_list = prepare_lstm_data(stk, class_df, timestep_size, _batch_size)

        err = []
        for bh in batch_list:

            if len(bh[0]) == _batch_size:
                sess.run(train_op, feed_dict={_X: bh[0], y: bh[1], keep_prob: 0.5, batch_size: _batch_size})

                # 打印训练精度
                train_accuracy = sess.run(cross_entropy, feed_dict={
                    _X: bh[0], y: bh[1], keep_prob: 1.0, batch_size: _batch_size})
                err.append(train_accuracy)

                # 已经迭代完成的 epoch 数: mnist.train.epochs_completed
        i = i + 1
        print("step %d, 训练损失 %f" % ((i + 1), np.array(err).mean()))

    saver.save(sess=sess, save_path='./Model/LstmModel1.ckpt')




