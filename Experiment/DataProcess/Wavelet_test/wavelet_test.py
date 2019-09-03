# encoding = utf-8

import tensorflow as tf
import math
import numpy as np
import pandas as pd
import random


class wl_par():


    def __init__(self,batch,input_x,input_y,output_size,wavelet_amount):

        self.batch          = batch
        self.input_x        = input_x
        self.input_y        = input_y
        self.wavelet_amount = wavelet_amount
        self.output_size    = output_size

        # 创建输入数据的placeholder
        with tf.name_scope('inputs'):
            self.image_holder = tf.placeholder(tf.float32, [batch, input_x, input_y], name='image')
            self.label_holder = tf.placeholder(tf.float32, [batch, output_size], name='label')

        # 构造前馈网络结构
        self.add_layer()

        # 计算损失
        with tf.name_scope('cost'):
            self.compute_loss()

        # 训练动作
        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(1e-3).minimize(tf.abs(self.loss))  # 0.72

        # 对变量进行初始化
        tf.global_variables_initializer().run()


    def add_layer(self):

        """
        前馈部分实现主函数
        :return:
        """

        # 定义 “输入-隐含” 权值矩阵 以及 小波参数参数
        w_ij    = self.variable_with_weight_loss(shape=[self.input_y, self.wavelet_amount], stddev=5e-2, wl=0.0)
        bias_ij = tf.Variable(tf.constant(0.1, shape=[self.wavelet_amount]))

        # 定义“小波尺度”和“小波平移”参数
        a       = self.variable_with_weight_loss(shape=[self.wavelet_amount], stddev=5e-2, wl=0.0)
        b       = self.variable_with_weight_loss(shape=[self.wavelet_amount], stddev=5e-2, wl=0.0)


        # 定义“隐含层”到“输出层”的权值和偏置
        w_jo    = self.variable_with_weight_loss(shape=[self.wavelet_amount*self.input_x,self.output_size], stddev=5e-2, wl=0.0)
        bias_jo = tf.Variable(tf.constant(0.1, shape=[self.output_size]))


        # 遍历batch中的每张图片，根据每张图片计算隐含层
        ts_hidden_result = tf.map_fn(fn=lambda x: self.wavelet_pro(w_ij=w_ij, bias_ij=bias_ij, a=a, b=b, pic=x), elems = self.image_holder)
        ts_hidden = tf.reshape(ts_hidden_result,shape=[self.batch,-1])


        # 对每张图片根据w_jo权值计算输出
        ts_out = tf.map_fn(fn=lambda x:(tf.matmul(tf.reshape(tensor=x,shape=[1,-1]),w_jo)+bias_jo),elems=ts_hidden)
        self.logits = ts_out


    def wavelet_morlet(self, t):

        """
        定义小波函数
        :param self:
        :param t:
        :return:
        """

        return tf.multiply(tf.exp(tf.div(tf.multiply(t,tf.multiply(-1.0,t)),2.0)),tf.cos(tf.multiply(1.75,t)))

    def wavelet_pro(self,pic,w_ij,bias_ij,a,b):

        return tf.map_fn(fn=lambda x:self.wavelet_pro_row(w_ij=w_ij,bias_ij=bias_ij,a=a,b=b,row=x),elems=pic)

    def wavelet_pro_row(self,w_ij,bias_ij,a,b,row):

        """
        定义小波网络部分（使用小波对图片每一行进行处理）
        :param self:
        :param row:
        :return:
        """

        # “输入”经过权重矩阵后再经小波函数
        w_pro = tf.matmul(tf.reshape(row,shape=[1,self.input_y]), w_ij) + bias_ij

        # 进行“平移”和“放缩    1 * input_y
        ab_pro = tf.div(tf.add(w_pro, tf.multiply(b, -1)), a)

        # 应用小波函数进行处理
        return tf.map_fn(fn=lambda x: self.wavelet_morlet(x), elems=ab_pro)

    def variable_with_weight_loss(self,shape, stddev, wl):

        """
        定义初始化weight权重，并给权重加上L2正则化的loss      truncated_normal:从正态分布中随机生成

        :param shape:
        :param stddev:
        :param wl:
        :return:
        """

        var = tf.Variable(tf.truncated_normal(shape, stddev=stddev))

        if wl is not None:
            weight_loss = tf.multiply(tf.nn.l2_loss(var), wl, name='weight_loss')
            tf.add_to_collection('losses', weight_loss)

        return var

    def comp_loss(self,logits, labels):
        """
        将所有的loss汇集
        :param logits:
        :param labels:
        :return:
        """

        # labels = tf.cast(labels, tf.int64)
        # cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
        #     logits=logits, labels=labels, name='cross_entropy_per_example')
        # cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')

        return tf.reduce_sum(tf.abs(tf.subtract(logits,labels)))
        # tf.add_to_collection('losses', cross_entropy)


        # The total loss is defined as the cross entropy loss plus all of the weight
        # decay terms (L2 loss).
        # return tf.add_n(tf.get_collection('losses'), name='total_loss')


    def compute_loss(self):
        self.loss = self.comp_loss(self.logits, self.label_holder)


# ============================= 测试 =====================================

# 读取数据
input_len = 20
future_len = 5
input_width = 3
batch = 1

result = []
with open('wavelet_test.csv') as f:
    df_merge = pd.read_csv(f)


for index in df_merge[input_len:len(df_merge)-future_len].index:

    image = df_merge.loc[index-input_len:index-1,['p_diff','v_std','class_v_std']].T.values

    label = df_merge.loc[index:(index+future_len-1),'p_diff'].sum()

    result.append({'image':image,'label':label})

random.shuffle(result)

# 定义sess和变量初始化
sess = tf.InteractiveSession()

# 根据类创建对象
model = wl_par(batch=batch,input_x=input_width,input_y=input_len,output_size=1,wavelet_amount=8)

for i in range(0,5000):
    loss_sum = 0
    for ele in range(0,len(result)-batch,batch):

        # 组合 图片 和 标签
        image = []
        label = []
        for id in range(ele,ele+batch):
            image.append(result[id]["image"])
            label.append([result[id]['label']])


        [result_train,loss,_] = sess.run([model.logits,model.loss,model.train_op],feed_dict={model.image_holder:image,
                                                                                       model.label_holder:label})
        loss_sum = loss_sum + math.fabs(loss)

    print(loss_sum)

