# encoding = utf-8

"""
    本段代码用于测试tf的优化器功能
"""

import tensorflow as tf


# 定义一个权值矩阵
initializer = tf.random_normal_initializer(mean=0., stddev=1., )
W = tf.get_variable(shape=[3, 8], initializer=initializer, name='W')

# 定义一个输入常量
input = tf.constant([2., 1., 5.4], shape=[1, 3])

# 计算输出
output = tf.reshape(tf.matmul(input, W), shape=[-1])

# 做差
o1 = output[0:7]
o2 = output[1:8]

o_diff = tf.reduce_sum(tf.square(tf.subtract(o1, o2)))

open_times = tf.reduce_sum(o1)

# 定义优化动作
train_op = tf.train.AdamOptimizer(0.2).minimize(open_times)

# 定义sess并初始化变量
sess = tf.Session()
sess.run(tf.global_variables_initializer())


for i in range(0, 100000):

    print(str(sess.run(open_times)))

    print('----------------------------------------------------------------\n\n')
    sess.run(train_op)
