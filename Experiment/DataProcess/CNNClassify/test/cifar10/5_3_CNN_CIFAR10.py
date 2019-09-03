# encoding = utf-8

#%%
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import DataProcess.CNNClassify.test.cifar10.cifar10 as cifar10
import DataProcess.CNNClassify.test.cifar10.cifar10_input as cifar10_input
import tensorflow as tf
import numpy as np
import time

max_steps = 3000
batch_size = 128
data_dir = '/tmp/cifar10_data/cifar-10-batches-bin'

# 定义初始化weight权重，并给权重加上L2正则化的loss
def variable_with_weight_loss(shape, stddev, wl):
    var = tf.Variable(tf.truncated_normal(shape, stddev=stddev))
    if wl is not None:
        weight_loss = tf.multiply(tf.nn.l2_loss(var), wl, name='weight_loss')
        tf.add_to_collection('losses', weight_loss)
    return var

# 将所有的loss汇集
def loss(logits, labels):
#      """Add L2Loss to all the trainable variables.
#      Add summary for "Loss" and "Loss/avg".
#      Args:
#        logits: Logits from inference().
#        labels: Labels from distorted_inputs or inputs(). 1-D tensor
#                of shape [batch_size]
#      Returns:
#        Loss tensor of type float.
#      """
#      # Calculate the average cross entropy loss across the batch.
    labels = tf.cast(labels, tf.int64)
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=logits, labels=labels, name='cross_entropy_per_example')
    cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')
    tf.add_to_collection('losses', cross_entropy_mean)

  # The total loss is defined as the cross entropy loss plus all of the weight
  # decay terms (L2 loss).
    return tf.add_n(tf.get_collection('losses'), name='total_loss')
  
### 下载或者解压数据
cifar10.maybe_download_and_extract()

# 产生训练需要的数据，包括“特征”和“label”
# 内部包括了“数据增强”的操作，包括“翻转”、“设置亮度和对比度”、“标准化”

# 注意：本函数内部为了加快处理速度，生成了16个独立的线程，内部会存在一个线程池。所有后面的代码中需要使用函数激活折现线程，否则无法进行下面的动作。
images_train, labels_train = cifar10_input.distorted_inputs(data_dir=data_dir,
                                                            batch_size=batch_size)


# 生成测试数据，与之前训练数据的区别在于不需要“数据增强”的操作
images_test, labels_test = cifar10_input.inputs(eval_data=True,
                                                data_dir=data_dir,
                                                batch_size=batch_size)                                                  
#images_train, labels_train = cifar10.distorted_inputs()
#images_test, labels_test = cifar10.inputs(eval_data=True)

# 创建输入数据的placeholder
image_holder = tf.placeholder(tf.float32, [batch_size, 24, 24, 3])
label_holder = tf.placeholder(tf.int32, [batch_size])

#logits = inference(image_holder)


# 定义第一层卷积池化层，因为没有对weight进行L2正则，所以wl项设置为0,64代表着64个特征
weight1 = variable_with_weight_loss(shape=[5, 5, 3, 64], stddev=5e-2, wl=0.0)
kernel1 = tf.nn.conv2d(image_holder, weight1, [1, 1, 1, 1], padding='SAME')
bias1 = tf.Variable(tf.constant(0.0, shape=[64]))
conv1 = tf.nn.relu(tf.nn.bias_add(kernel1, bias1))
pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                       padding='SAME')


# lrn层模拟了生物神经系统的“侧抑制”机制，对局部神经元的活动创建竞争环境，
# 使得其中响应比较大的值变的相对更大，并抑制其他反馈较小的神经元，增强了模型的泛化能力。
norm1 = tf.nn.lrn(pool1, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)



weight2 = variable_with_weight_loss(shape=[5, 5, 64, 64], stddev=5e-2, wl=0.0)
kernel2 = tf.nn.conv2d(norm1, weight2, [1, 1, 1, 1], padding='SAME')
bias2 = tf.Variable(tf.constant(0.1, shape=[64]))
conv2 = tf.nn.relu(tf.nn.bias_add(kernel2, bias2))
norm2 = tf.nn.lrn(conv2, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)
pool2 = tf.nn.max_pool(norm2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                       padding='SAME')


reshape = tf.reshape(pool2, [batch_size, -1])                                   # 对卷积层输出的结果进行flatten
dim = reshape.get_shape()[1].value                                              # 获取数据压扁后的长度
weight3 = variable_with_weight_loss(shape=[dim, 384], stddev=0.04, wl=0.004)    # 对全连接层weight进行初始化，设置wl为0.004以防止该层过拟合
bias3 = tf.Variable(tf.constant(0.1, shape=[384]))
local3 = tf.nn.relu(tf.matmul(reshape, weight3) + bias3)

weight4 = variable_with_weight_loss(shape=[384, 192], stddev=0.04, wl=0.004)
bias4 = tf.Variable(tf.constant(0.1, shape=[192]))                                      
local4 = tf.nn.relu(tf.matmul(local3, weight4) + bias4)

weight5 = variable_with_weight_loss(shape=[192, 10], stddev=1/192.0, wl=0.0)
bias5 = tf.Variable(tf.constant(0.0, shape=[10]))
logits = tf.add(tf.matmul(local4, weight5), bias5)

loss = loss(logits, label_holder)


train_op = tf.train.AdamOptimizer(1e-3).minimize(loss) #0.72

top_k_op = tf.nn.in_top_k(logits, label_holder, 1)


# 创建session并初始化所有默模型参数
sess = tf.InteractiveSession()
tf.global_variables_initializer().run()


# 启动“图像增强”的线程队列
tf.train.start_queue_runners()


# 开始训练模型
for step in range(max_steps):

    # 记录起始时间，用于计算耗时
    start_time = time.time()

    # 读取训练数据
    image_batch,label_batch = sess.run([images_train,labels_train])

    # 进行训练
    _, loss_value = sess.run([train_op, loss],feed_dict={image_holder:image_batch,
                                                         label_holder:label_batch})
    duration = time.time() - start_time

    # 打印误差及每个样本的训练耗时
    if step % 10 == 0:
        examples_per_sec = batch_size / duration
        sec_per_batch = float(duration)
    
        format_str = ('step %d, loss = %.2f (%.1f examples/sec; %.3f sec/batch)')
        print(format_str % (step, loss_value, examples_per_sec, sec_per_batch))


# 对图像进行预测
num_examples = 10000
import math
num_iter = int(math.ceil(num_examples / batch_size))
true_count = 0  
total_sample_count = num_iter * batch_size
step = 0


while step < num_iter:

    # 读取test数据
    image_batch,label_batch = sess.run([images_test,labels_test])

    # 对test数据进行预测
    predictions = sess.run([top_k_op],feed_dict={image_holder: image_batch,
                                                 label_holder:label_batch})

    # 求正确次数和
    true_count += np.sum(predictions)
    step += 1


# 计算正确率
precision = true_count / total_sample_count
print('precision @ 1 = %.3f' % precision)
