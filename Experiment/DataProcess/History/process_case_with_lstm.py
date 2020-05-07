# encoding=utf-8

import json
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from pandas import DataFrame

from Config.GlobalSetting import g_debug_file_url
from sdk.LSTM_Class import LSTMRNN
from sdk.MyTimeOPT import get_current_date_str

TIME_STEPS = 21
BATCH_SIZE = 5
INPUT_SIZE = 5
OUTPUT_SIZE = 1
CELL_SIZE = 40
# LR = 0.06

'''
1、从json文件中读取学习数据
返回格式：
{ 'code': '300596',
  'start': '2017-03-27',
  'end': '2017-04-18', 
  'change_ratio': '-0.280922689437',
  'customer_end_index': '62', 
  'feature':dataframe
}
2、在feature中增加label
3、将dataframe多个合成一个
'''
def read_studyData_from_json(file_url):

    result = []
    with open(file=file_url) as studyFile:
        case_feature = json.load(fp=studyFile)

    # 将feature从字符串转为dataframe
    for case in case_feature:
        case["feature"] = DataFrame(json.loads(case["feature"]))\
            .sort_values(by="date")\
            .reset_index(drop=True)

        # 在dataframe中添加label，即字段“ratio”
        case["feature"]["ratio"] = float(case["change_ratio"])
        result.append(case["feature"])

    return pd.concat(result).reset_index()

'''
从case中获取学习数据并对数据进行规整
'''
def get_train_data_from_case(data_param, batch_size, time_step, train_begin, train_end):
    time_step_temp = time_step
    batch_index=[]
    data_train=data_param[train_begin:train_end]

    # 标准化 出错，原因是ratio是字符串
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)

    # 训练集
    train_x,train_y=[],[]

    # 此时normalized_train_data的shape是n*8
    for i in range(int(math.floor(len(normalized_train_data)/time_step))):       # i = 1~5785

       # 生成batch_index：0，batch_size*1，batch_size*2
       if i % batch_size==0:
           batch_index.append(i)

       #获取了一个样本,dataframe 对于loc的区间选择采用的是“前闭后闭”，所以我们需要在后面减1来实现前闭后开
       x= normalized_train_data.loc[i*time_step_temp:(i+1)*time_step_temp-1, ['open', 'high', 'close', 'low', 'volume']]           # x:shape 15*7
       y= normalized_train_data.loc[i*time_step_temp:(i+1)*time_step_temp-1, 'ratio']                                              # y:shape 15*1

       train_x.append(np.array(x))
       train_y.append(np.array(y)[:,np.newaxis])
    batch_index.append(int(math.floor(len(normalized_train_data)/time_step)))  # batch_index 收尾

    # train_x :n*15*7
    # train_y :n*15*1
    return batch_index,train_x,train_y

# --------------------------------------正文-----------------------------------------


if __name__ == '__main__':
    model = LSTMRNN(TIME_STEPS, INPUT_SIZE, OUTPUT_SIZE, CELL_SIZE, BATCH_SIZE)
    sess = tf.Session()

    # 将可视化数据写入文件
    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter(r'logs/', tf.get_default_graph())

    init = tf.global_variables_initializer()
    sess.run(init)
    # relocate to the local dir and run this line to view it on Chrome (http://0.0.0.0:6006/):
    # $ tensorboard --logdir='logs'

    plt.ion()
    plt.show()

    # 创建保存器用于模型
    saver = tf.train.Saver()

    studyData_jsonFile = g_debug_file_url + "studyData_" + get_current_date_str() + ".json"
    origin_data = read_studyData_from_json(studyData_jsonFile).loc[:, ["high", "low", "open", "close", "volume", "ratio"]]
    origin_data["ratio"] = origin_data["ratio"].apply(lambda x:float(x))
    batch_index, train_x, train_y = get_train_data_from_case(origin_data, time_step=TIME_STEPS,
                                                             batch_size=BATCH_SIZE, train_begin=0, train_end=42000)
    for j in range(15):
        for i in range(385):    # 遍历batch

            if (i == 0)&(j==0):
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
            plt.plot(np.linspace((i+100*j)*BATCH_SIZE,(i+100*j+1)*BATCH_SIZE-1,BATCH_SIZE),
                     list(map(lambda x:x[TIME_STEPS-1],train_y[batch_index[i]:batch_index[i+1]])), 'r*--',

                     np.linspace((i+100*j)*BATCH_SIZE,(i+100*j+1)*BATCH_SIZE-1,BATCH_SIZE),
                     list(map(lambda x:x[TIME_STEPS-1],pred.reshape([-1,TIME_STEPS]))), 'bo--')

            plt.ylim((-1.2, 1.2))

            # plt.pause(0.3)

            print('cost: ', round(cost, 4))
            result = sess.run(merged, feed_dict)
            writer.add_summary(result, i+j*100)

    saver.save(sess=sess, save_path='./modelDir/' + 'lstmModel' + get_current_date_str() + '.ckpt')
    plt.draw()

    end = 0