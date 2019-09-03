import tensorflow as tf


""" ------------------------ 加载已经保存的模型 ----------------------------------- """
with tf.Session() as sess:
  new_saver = tf.train.import_meta_graph('./checkpoint_dir/MyModel-1000.meta')
  new_saver.restore(sess, tf.train.latest_checkpoint('./checkpoint_dir'))


""" ------------------------ 简单案例 --------------------------------------------- """

# 假设我们有一个简单的网络模型，代码如下：
w1 = tf.placeholder("float", name="w1")
w2 = tf.placeholder("float", name="w2")
b1 = tf.Variable(2.0, name="bias")

# 定义一个op，用于后面恢复
w3 = tf.add(w1, w2)
w4 = tf.multiply(w3, b1, name="op_to_restore")
sess = tf.Session()
sess.run(tf.global_variables_initializer())

# 创建一个Saver对象，用于保存所有变量
saver = tf.train.Saver()

# 通过传入数据，执行op
print(sess.run(w4, feed_dict={w1: 4, w2: 8}))
# 打印 24.0 ==>(w1+w2)*b1

# 现在保存模型
saver.save(sess, './checkpoint_dir/MyModel', global_step=1000)


"""
======================================================================
接下来我们使用graph.get_tensor_by_name()方法来操纵这个保存的模型。
"""

sess = tf.Session()

# 先加载图和参数变量
saver = tf.train.import_meta_graph('./checkpoint_dir/MyModel-1000.meta')
saver.restore(sess, tf.train.latest_checkpoint('./checkpoint_dir'))


"""

我们项目中的测试代码

import tensorflow as tf
import numpy as np


sess = tf.Session()

# 先加载图和参数变量
saver = tf.train.import_meta_graph('F:\MYAI\Code\master\My_Quant\CornerDetectAndAutoEmail\AboutLSTM\modelDir\LstmForCornerPot.ckpt.meta')
saver.restore(sess, tf.train.latest_checkpoint('F:\MYAI\Code\master\My_Quant\CornerDetectAndAutoEmail\AboutLSTM\modelDir/'))          

graph = tf.get_default_graph()

"""


# 访问placeholders变量，并且创建feed-dict来作为placeholders的新值
graph = tf.get_default_graph()
w1 = graph.get_tensor_by_name("w1:0")
w2 = graph.get_tensor_by_name("w2:0")
feed_dict = {w1: 13.0, w2: 17.0}

# 接下来，访问你想要执行的op
op_to_restore = graph.get_tensor_by_name("op_to_restore:0")

print(sess.run(op_to_restore, feed_dict))

# 打印结果为60.0==>(13+17)*2

# 注意：保存模型时，只会保存变量的值，placeholder里面的值不会被保存

"""
===================================================================================
如果你不仅仅是用训练好的模型，
还要加入一些op，或者说加入一些layers并训练新的模型，
可以通过一个简单例子来看如何操作：
"""

import tensorflow as tf

sess = tf.Session()

# 先加载图和变量
saver = tf.train.import_meta_graph('my_test_model-1000.meta')
saver.restore(sess, tf.train.latest_checkpoint('./'))

# 访问placeholders变量，并且创建feed-dict来作为placeholders的新值
graph = tf.get_default_graph()
w1 = graph.get_tensor_by_name("w1:0")
w2 = graph.get_tensor_by_name("w2:0")
feed_dict = {w1: 13.0, w2: 17.0}

# 接下来，访问你想要执行的op
op_to_restore = graph.get_tensor_by_name("op_to_restore:0")

# 在当前图中能够加入op
add_on_op = tf.multiply(op_to_restore, 2)

print(sess.run(add_on_op, feed_dict))
# 打印120.0==>(13+17)*2*2




"""
========================================================================
如果只想恢复图的一部分，
并且再加入其它的op用于fine-tuning。
只需通过graph.get_tensor_by_name()方法获取需要的op，
并且在此基础上建立图，看一个简单例子，
假设我们需要在训练好的VGG网络使用图，并且修改最后一层，
将输出改为2，用于fine-tuning新数据：
"""

saver = tf.train.import_meta_graph('vgg.meta')

# 访问图
graph = tf.get_default_graph()

# 访问用于fine-tuning的output
fc7 = graph.get_tensor_by_name('fc7:0')

# 如果你想修改最后一层梯度，需要如下
fc7 = tf.stop_gradient(fc7)                   # It's an identity function
fc7_shape = fc7.get_shape().as_list()

new_outputs = 2
weights = tf.Variable(tf.truncated_normal([fc7_shape[3], num_outputs], stddev=0.05))
biases = tf.Variable(tf.constant(0.05, shape=[num_outputs]))
output = tf.matmul(fc7, weights) + biases
pred = tf.nn.softmax(output)

# Now, you run this with fine-tuning data in sess.run()


