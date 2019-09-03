# encoding = utf-8

from SDK.SDKHeader import *
from DataProcess.MACD.DataPrepareSub import *

# --------------------------------------- 加载模型 ----------------------------------------------
sess = tf.InteractiveSession()

saver = tf.train.import_meta_graph('./Model/' + 'LstmModel1.ckpt.meta')
saver.restore(sess, tf.train.latest_checkpoint('./Model/'))

graph = tf.get_default_graph()
x = graph.get_tensor_by_name("x:0")
y = graph.get_tensor_by_name("y:0")
cross_entropy = graph.get_tensor_by_name("cross_entropy:0")
keep_prob = graph.get_tensor_by_name("keep_prob:0")
batch_size = graph.get_tensor_by_name("batch_size:0")
y_pre = graph.get_tensor_by_name("y_pre:0")

# --------------------------------------- 准备数据 ----------------------------------------------
_batch_size = 1
batch_test = prepare_lstm_data('cyb','cyb',20,_batch_size)

# --------------------------------------- 进行预测 ----------------------------------------------

for bh in batch_test:
    pre = sess.run(y_pre, feed_dict={x: bh[0], y: bh[1], keep_prob: 1.0, batch_size:_batch_size})

    pre = pre[0][0]
    real = bh[1][0][0]
    diff = (real - pre)/real * 100


    print('real:' + str(real) + ' \t\t\t\t pre:' + str(pre)  + '\t\t\t误差：' + str(diff))