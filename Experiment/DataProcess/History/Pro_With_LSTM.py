# encoding = utf-8

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from Config.GlobalSetting import conn_k
from Restore.DataProcessSDK import LSTMRNN
from sdk.DBOpt import get_total_table_data

BATCH_START = 0
TIME_STEPS = 4
BATCH_SIZE = 20
INPUT_SIZE = 5
OUTPUT_SIZE = 1
CELL_SIZE = 10
LR = 0.006
PREDICT_STEP = 1


''''
open','high','close','low','volume'
'''
def get_origin_data_from_db(stk_code):
    # read data from database
    data_df = get_total_table_data(conn_k, 'k' + stk_code)

    # get necessary data
    data_df_necessary = data_df.loc[:, ['open', 'high', 'close', 'low', 'volume']]

    return data_df_necessary


'''
函数功能：获取获取训练数据，从原始数据中整理出训练数据
@:param batch_size  批大小
@:param time_step   时间步
@:param train_begin 训练起始点
@:param train_end   训练终止点

@:return    batch_index（批索引）、train_x（训练数据feature）train_y（训练数据label）
'''
def get_train_data(data_param, batch_size, time_step, train_begin, train_end, predict_step):
    time_step_temp = time_step - 1
    batch_index=[]
    data_train=data_param[train_begin:train_end]

    # 标准化
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)

    # 训练集
    train_x,train_y=[],[]

    # 此时normalized_train_data的shape是n*8
    for i in range(len(normalized_train_data)-predict_step):       # i = 1~5785

       # 生成batch_index：0，batch_size*1，batch_size*2
       if i % batch_size==0:
           batch_index.append(i)

       #获取了一个样本
       x= normalized_train_data.loc[i:i + time_step_temp, ['open', 'high', 'close', 'low', 'volume']]        # x:shape 15*7
       y= normalized_train_data.loc[i + predict_step:i + predict_step + time_step_temp, 'high']              # y:shape 15*1

       train_x.append(np.array(x))
       train_y.append(np.array(y)[:,np.newaxis])
    batch_index.append((len(normalized_train_data) - time_step_temp))  # batch_index 收尾

    # train_x :n*15*7
    # train_y :n*15*1
    return batch_index,train_x,train_y




'''
从case中获取学习数据并对数据进行规整
'''
def get_train_data_from_case(data_param, batch_size, time_step, train_begin, train_end, predict_step):
    time_step_temp = time_step - 1
    batch_index=[]
    data_train=data_param[train_begin:train_end]

    # 标准化
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)

    # 训练集
    train_x,train_y=[],[]

    # 此时normalized_train_data的shape是n*8
    for i in range(len(normalized_train_data)-predict_step):       # i = 1~5785

       # 生成batch_index：0，batch_size*1，batch_size*2
       if i % batch_size==0:
           batch_index.append(i)

       #获取了一个样本
       x= normalized_train_data.loc[i:i + time_step_temp, ['open', 'high', 'close', 'low', 'volume']]        # x:shape 15*7
       y= normalized_train_data.loc[i + predict_step:i + predict_step + time_step_temp, 'high']              # y:shape 15*1

       train_x.append(np.array(x))
       train_y.append(np.array(y)[:,np.newaxis])
    batch_index.append((len(normalized_train_data) - time_step_temp))  # batch_index 收尾

    # train_x :n*15*7
    # train_y :n*15*1
    return batch_index,train_x,train_y

if __name__ == '__main__':
    model = LSTMRNN(TIME_STEPS, INPUT_SIZE, OUTPUT_SIZE, CELL_SIZE, BATCH_SIZE)
    sess = tf.Session()

    # 将可视化数据写入文件
    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter(r'logs/', tf.get_default_graph())

    # tf.initialize_all_variables() no long valid from
    # 2017-03-02 if using tensorflow >= 0.12
    if int((tf.__version__).split('.')[1]) < 12 and int((tf.__version__).split('.')[0]) < 1:
        init = tf.initialize_all_variables()
    else:
        init = tf.global_variables_initializer()
    sess.run(init)
    # relocate to the local dir and run this line to view it on Chrome (http://0.0.0.0:6006/):
    # $ tensorboard --logdir='logs'

    plt.ion()
    plt.show()
    origin_data = get_origin_data_from_db('300508')
    for i in range(18):    # 遍历batch
        batch_index, train_x, train_y = get_train_data(origin_data, time_step=TIME_STEPS,
                                                       batch_size=BATCH_SIZE, train_begin=0, train_end=400,
                                                       predict_step=PREDICT_STEP)
        if i == 0:
            feed_dict = {
                    model.xs: train_x[batch_index[i]:batch_index[i+1]],
                    model.ys: train_y[batch_index[i]:batch_index[i+1]],
                    # create initial state
            }
        else:
            feed_dict = {
                model.xs: train_x[batch_index[i]:batch_index[i+1]],
                model.ys: train_y[batch_index[i]:batch_index[i+1]],
                model.cell_init_state: state    # use last state as the initial state for this run
            }

        _, cost, state, pred = sess.run(
            [model.train_op, model.cost, model.cell_final_state, model.pred],
            feed_dict=feed_dict)

        # plotting 红色为预测值，蓝色为输入值
        plt.plot(np.linspace(i*BATCH_SIZE,(i+1)*BATCH_SIZE-1,BATCH_SIZE),
                 list(map(lambda x:x[TIME_STEPS-1],train_y[batch_index[i]:batch_index[i+1]])), 'r*--',

                 np.linspace(i*BATCH_SIZE,(i+1)*BATCH_SIZE-1,BATCH_SIZE),
                 list(map(lambda x:x[TIME_STEPS-1],pred.reshape([-1,TIME_STEPS]))), 'bo--')

        # plt.ylim((-1.2, 1.2))
        plt.draw()
        plt.pause(0.3)


        print('cost: ', round(cost, 4))
        result = sess.run(merged, feed_dict)
        writer.add_summary(result, i)

    end = 0

