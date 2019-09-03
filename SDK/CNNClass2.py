# encoding = utf-8

import tensorflow as tf

class CNN2():

    def __init__(self, batch_size,output_size,input_x,input_y,cov_x,cov_y):

        self.batch_size = batch_size

        self.input_x = input_x
        self.input_y = input_y

        self.cov_x = cov_x
        self.cov_y = cov_y
        self.output_size = output_size

        # 创建输入数据的placeholder
        with tf.name_scope('inputs'):
            self.image_holder = tf.placeholder(tf.float32, [batch_size,input_x, input_y], name='image')
            self.label_holder = tf.placeholder(tf.int32, [batch_size], name='label')

        # 添加CNN主题
        with tf.name_scope("cnn_body"):
            self.add_layer()

        with tf.name_scope("logits"):
            logits = tf.multiply(self.logits,1,name='logits')

        # 计算损失
        with tf.name_scope('cost'):
            self.compute_loss()

        # 训练动作
        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(1e-3).minimize(self.loss,name='train_op')  # 0.72

        # 计算输出概率
        with tf.name_scope('probability'):

            # 使用in_top_k函数输出准确率，默认k为1，即输出分数最高的那一类的准确率
            self.top_k_op = tf.nn.in_top_k(self.logits, self.label_holder, 1)

        with tf.name_scope('initial'):
            tf.global_variables_initializer().run()

    # 定义初始化weight权重，并给权重加上L2正则化的loss
    def variable_with_weight_loss(self,shape, stddev, wl):
        var = tf.Variable(tf.truncated_normal(shape, stddev=stddev))
        if wl is not None:
            weight_loss = tf.multiply(tf.nn.l2_loss(var), wl, name='weight_loss')
            tf.add_to_collection('losses', weight_loss)
        return var


    # 将所有的loss汇集
    def comp_loss(self,logits, labels):

        labels = tf.cast(labels, tf.int64)
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
            logits=logits, labels=labels, name='cross_entropy_per_example')
        cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')
        tf.add_to_collection('losses', cross_entropy_mean)

        # The total loss is defined as the cross entropy loss plus all of the weight
        # decay terms (L2 loss).
        return tf.add_n(tf.get_collection('losses'), name='total_loss')


    # 添加层函数
    def add_layer(self):

        # 定义第一层卷积池化层，因为没有对weight进行L2正则，所以wl项设置为0
        with tf.name_scope('weight1'):
            weight1 = self.variable_with_weight_loss(shape=[self.cov_x, self.cov_y, 1, 128], stddev=5e-2, wl=0.0)
            kernel1 = tf.nn.conv2d(tf.reshape(self.image_holder,[self.batch_size,self.input_x,self.input_y,1]), weight1, [1, 1, 1, 1], padding='SAME')
            bias1 = tf.Variable(tf.constant(0.0, shape=[128]))
            conv1 = tf.nn.relu(tf.nn.bias_add(kernel1, bias1))
            pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                                   padding='SAME')


            # lrn层模拟了生物神经系统的“侧抑制”机制，对局部神经元的活动创建竞争环境，
            # 使得其中响应比较大的值变的相对更大，并抑制其他反馈较小的神经元，增强了模型的泛化能力。
            norm1 = tf.nn.lrn(pool1, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)

        with tf.name_scope('weight2'):
            weight2 = self.variable_with_weight_loss(shape=[self.cov_x, self.cov_y, 128, 128], stddev=5e-2, wl=0.0)
            kernel2 = tf.nn.conv2d(norm1, weight2, [1, 1, 1, 1], padding='SAME')
            bias2 = tf.Variable(tf.constant(0.1, shape=[128]))
            conv2 = tf.nn.relu(tf.nn.bias_add(kernel2, bias2))
            norm2 = tf.nn.lrn(conv2, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)
            pool2 = tf.nn.max_pool(norm2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                                   padding='SAME')


        reshape = tf.reshape(pool2, [self.batch_size, -1])  # 对卷积层输出的结果进行flatten
        dim = reshape.get_shape()[1].value                  # 获取数据压扁后的长度

        with tf.name_scope('weight3'):
            weight3 = self.variable_with_weight_loss(shape=[dim, 16384], stddev=0.04, wl=0.004)  # 对全连接层weight进行初始化，设置wl为0.004以防止该层过拟合
            bias3 = tf.Variable(tf.constant(0.1, shape=[16384]))
            local3 = tf.nn.relu(tf.matmul(reshape, weight3) + bias3)

        with tf.name_scope('weight4'):
            weight4 = self.variable_with_weight_loss(shape=[16384, 192], stddev=0.04, wl=0.004)
            bias4 = tf.Variable(tf.constant(0.1, shape=[192]))
            local4 = tf.nn.relu(tf.matmul(local3, weight4) + bias4)

        with tf.name_scope('weight5'):
            weight5 = self.variable_with_weight_loss(shape=[192, self.output_size], stddev=1 / 192.0, wl=0.0)
            bias5 = tf.Variable(tf.constant(0.0, shape=[self.output_size]))

        self.logits = tf.add(tf.matmul(local4, weight5), bias5, name='logits')

    def compute_loss(self):
        self.loss = self.comp_loss(self.logits, self.label_holder)

    # with tf.name_scope('train'):
    #     train_op = tf.train.AdamOptimizer(1e-3).minimize(loss)  # 0.72
    #
    # with tf.name_scope('probability'):
    #
    #     # 使用in_top_k函数输出准确率，默认k为1，即输出分数最高的那一类的准确率
    #     top_k_op = tf.nn.in_top_k(self.logits, label_holder, 1)


