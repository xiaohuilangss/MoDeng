# encoding: utf-8

'''
原文链接：http://blog.csdn.net/mylove0414/article/details/56969181

此版本对代码进行的详细的注释！

运行环境：
python：     3.6.2
tensorflow： 1.2
IDE：        pycharm
OS：         windows7

如有疑问，欢迎加群讨论！群号：183625427

或点击链接加入群【算法&数学】：https://jq.qq.com/?_wv=1027&k=5E02S3F
'''


from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

# 定义LSTM的超参数
# 根据stk历史数据中的最低价、最高价、开盘价、收盘价、交易量、交易额、跌涨幅等因素，对下一日stk最高价进行预测。
rnn_unit=10       # 隐含层数目
input_size=7
output_size=1
lr=0.0006         # 学习率

# 定义权重和偏置
weights={
         'in':tf.Variable(tf.random_normal([input_size,rnn_unit])),
         'out':tf.Variable(tf.random_normal([rnn_unit,1]))
        }
biases={
        'in':tf.Variable(tf.constant(0.1,shape=[rnn_unit,])),
        'out':tf.Variable(tf.constant(0.1,shape=[1,]))
       }

'''
函数功能：获取获取训练数据，从原始数据中整理出训练数据
@:param batch_size  批大小
@:param time_step   时间步
@:param train_begin 训练起始点
@:param train_end   训练终止点

@:return    batch_index（批索引）、train_x（训练数据feature）train_y（训练数据label）
'''


def get_train_data(batch_size=60,time_step=20,train_begin=0,train_end=5800):
    batch_index=[]
    data_train=data[train_begin:train_end]

    # 标准化
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)

    # 训练集
    train_x,train_y=[],[]

    # 此时normalized_train_data的shape是n*8
    for i in range(len(normalized_train_data)-time_step):       # i = 1~5785

       # 生成batch_index：0，batch_size*1，batch_size*2
       if i % batch_size==0:
           batch_index.append(i)

       x=normalized_train_data[i:i+time_step,:7]                # x:shape 15*7
       y=normalized_train_data[i:i+time_step,7,np.newaxis]      # y:shape 15*1

       train_x.append(x.tolist())
       train_y.append(y.tolist())
    batch_index.append((len(normalized_train_data)-time_step))  # batch_index 收尾

    # train_x :n*15*7
    # train_y :n*15*1
    return batch_index,train_x,train_y


'''
函数功能：获取测试数据

@:param time_step   时间步
@:param test_begin  起始点

@:return    预测值、最终状态
'''


def get_test_data(time_step=20,test_begin=5800):

    data_test=data[test_begin:]                 # 截取测试数据
    mean=np.mean(data_test,axis=0)              # 平均数
    std=np.std(data_test,axis=0)                # 方差
    normalized_test_data=(data_test-mean)/std   # 标准化

    # 有size个sample
    size=(len(normalized_test_data)+time_step-1)//time_step
    test_x,test_y=[],[]

    for i in range(size-1):
       x=normalized_test_data[i*time_step:(i+1)*time_step,:7]   # x shape 20*7
       y=normalized_test_data[i*time_step:(i+1)*time_step,7]    # y shape (20,)
       test_x.append(x.tolist())
       test_y.extend(y)

    # 保存得到的x和y
    test_x.append((normalized_test_data[(i+1)*time_step:,:7]).tolist())     # 本例中 16*20*7
    test_y.extend((normalized_test_data[(i+1)*time_step:,7]).tolist())      # 本例中 309
    return mean,std,test_x,test_y


'''
函数功能：定义LSTM隐含层输入到输出的计算流程，前向计算

@:param X   数据的label  shape = [None,time_step,input_size]
@:return    预测值、最终状态
'''
def lstm(X):

    batch_size=tf.shape(X)[0]   # 这行语句用于获取X的第一维的具体数据 获取batch_size值
    time_step=tf.shape(X)[1]    # 这行语句用于获取X的第一维的具体数据 获取time_step值
    w_in=weights['in']
    b_in=biases['in']

    input=tf.reshape(X,[-1,input_size])     #需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入 系统的输入单元数为7，所以将输入数据shape为n行7列
    input_rnn=tf.matmul(input,w_in)+b_in    # 输入数据与输入权重相乘，得到输入数据对隐含层的影响

    # 将tensor转成3维，作为lstm cell的输入
    # 隐含层的cell接收的数据是3维的，即将n*10的数据shape为n*15*10的数据
    input_rnn=tf.reshape(input_rnn,[-1,time_step,rnn_unit])

    # 设置lstm的cell，BasicLSTMCell的入参有(self, num_units, forget_bias=1.0,state_is_tuple=True, activation=None, reuse=None)
    # 此处只设置其隐含层数目为rnn_unit，即10，其他参数使用默认值
    cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)
    init_state=cell.zero_state(batch_size,dtype=tf.float32)

    # output_rnn是记录LSTM每个输出节点的结果，final_states是cell的最后状态
    output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)

    # 将输出数据shape为n*10格式
    output=tf.reshape(output_rnn,[-1,rnn_unit])

    w_out=weights['out']
    b_out=biases['out']

    # cell输出经过与输出权重矩阵相乘并加入偏置后，得到最终输出
    pred=tf.matmul(output,w_out)+b_out

    return pred,final_states

'''
函数功能：训练模型
@:param batch_size      批大小
@:param time_step       时间步长度
@:param train_begin     训练起始
@:param train_end       训练截止
@:return                打印得分并将模型保存
'''


def train_lstm(batch_size=80,time_step=15,train_begin=2000,train_end=5800):

    # X是训练数据中的feature Y是训练数据中的label
    X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
    Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])

    # 获取训练数据  batch_index:80的等差序列 train_x：[3785*15] train_y:[3785*15]  15:time_step值
    batch_index,train_x,train_y=get_train_data(batch_size,time_step,train_begin,train_end)

    # 创建预测值获取的计算流程
    with tf.variable_scope("sec_lstm"):
        pred,_=lstm(X)

    # 创建损失函数的计算流程
    loss=tf.reduce_mean(tf.square(tf.reshape(pred,[-1])-tf.reshape(Y, [-1])))

    # 定义优化函数（即训练使）
    train_op=tf.train.AdamOptimizer(lr).minimize(loss)

    # 将变量保存
    saver=tf.train.Saver(tf.global_variables(),max_to_keep=15)

    with tf.Session() as sess:
        try:
            module_file = tf.train.latest_checkpoint('.')
            saver.restore(sess, module_file)
        except:
            sess.run(tf.global_variables_initializer())

        # 重复训练10000次
        for i in range(10):
            # 按批次进行训练，每一批次80条数据
            for step in range(len(batch_index)-1):
                _,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
            print(i,loss_)
            if i % 200==0:
                print("保存模型：",saver.save(sess,'./stock2.model',global_step=i))


'''
函数功能：根据模型进行预测

@:param time_step       时间步长度
@:return                打印得分并将模型保存
'''


def prediction(time_step=20):
    X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
    #Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])

    # 获取测试数据的“均值”、“方差”、feature和label
    # test_x 16*20（最后一个长度为9） test_y：309
    mean,std,test_x,test_y=get_test_data(time_step)

    with tf.variable_scope("sec_lstm",reuse=True):
        pred,_=lstm(X)

    saver=tf.train.Saver(tf.global_variables())

    with tf.Session() as sess:

        #参数恢复
        module_file = tf.train.latest_checkpoint('./')
        saver.restore(sess, module_file)
        test_predict=[]
        for step in range(len(test_x)-1):
          prob=sess.run(pred,feed_dict={X:[test_x[step]]})   # prob是长度为20的一维矩阵，也就是说，对于我们的模型，输入是15，输出是20
          predict=prob.reshape((-1))
          test_predict.extend(predict)
        test_y=np.array(test_y)*std[7]+mean[7]
        test_predict=np.array(test_predict)*std[7]+mean[7]
        acc=np.average(np.abs(test_predict-test_y[:len(test_predict)])/test_y[:len(test_predict)])  #偏差

        #以折线图表示结果
        plt.figure()
        plt.plot(list(range(len(test_predict))), test_predict, color='b')
        plt.plot(list(range(len(test_y))), test_y,  color='r')
        plt.show()


# ========================================主代码==================================

# 导入数据
f=open('dataset/dataset_2.csv')
df=pd.read_csv(f)               # 读入stk数据
data=df.iloc[:,2:10].values     # 取第3-10列   data实际数据大小[6109 * 8]


# 内部调用了get_train_data函数，从data中获取了训练数据
# 获取训练数据  batch_index:80的等差序列 train_x：[3785*15] train_y:[3785*15]  15:time_step值
# 默认取2000~5800之间的数据作为训练数据，
train_lstm()

# 内部调用了get_test_data函数，从data中获取了测试函数
# 取5800往后的数据作为测试数据，一共309个数据
# test_x 16*20（最后一个长度为9） test_y：309
prediction() 
