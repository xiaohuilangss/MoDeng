#encoding=utf-8

from sdk.LSTM_Class import LSTMRNN
from sdk.SDKHeader import *

BATCH_START = 0
TIME_STEPS = 15
BATCH_SIZE = 5
INPUT_SIZE = 4
OUTPUT_SIZE = 1
CELL_SIZE = 10
LR = 0.006
PREDICT_STEP = 1
LAYER_NUM = 2

class ave_lstm(LSTMRNN):

    def __init__(self, n_steps, input_size, output_size, cell_size, batch_size):
        LSTMRNN.__init__(self, n_steps, input_size, output_size, cell_size, batch_size)

    def compute_cost(self):
        if g_lstm_debug_enable:
            write_to_txt(g_debug_file_url+g_lstm_debug_file_name,"开始进入compute_cost函数，计算当前损失！\n")

        pred_shaped = tf.reshape(self.pred, [-1,self.n_steps], name='reshape_pred')
        pred_slice = pred_shaped[:,self.n_steps-1]

        y_shaped = tf.reshape(self.ys, [-1, self.n_steps], name='reshape_pred')
        y_slice = y_shaped[:, self.n_steps-1]

        myLosses = tf.square(tf.subtract(y_slice, pred_slice))


        # # 莫凡测试 能够通过，说明lstm类没有问题，k没有收敛是由于损失定义错误的原因
        # myLosses = tf.square(tf.subtract(tf.reshape(self.pred, [-1], name='reshape_pred'),
        #                     tf.reshape(self.ys,[-1],name='reshape_target')))

        tf.summary.scalar('myLosses', tf.reduce_sum(myLosses))

        with tf.name_scope('average_cost'):
            self.cost = tf.div(
                tf.reduce_sum(myLosses, name='losses_sum'),
                self.batch_size,
                name='average_cost')
            tf.summary.scalar('cost', self.cost)
            tf.summary.scalar('batch_size',self.batch_size)

    def add_cell(self):
        with tf.name_scope('multi_cell'):
            lstm_cell = tf.contrib.rnn.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True)
            mlstm_cell = tf.contrib.rnn.MultiRNNCell([lstm_cell]*LAYER_NUM,state_is_tuple=True)

        with tf.name_scope('my_initial_state'):
            self.cell_init_state = mlstm_cell.zero_state(self.batch_size, dtype=tf.float32)
            self.cell_outputs, self.cell_final_state = tf.nn.dynamic_rnn(
                mlstm_cell, self.l_in_y, initial_state=self.cell_init_state, time_major=False)


'''
从case中获取学习数据并对数据进行规整
'''
def get_train_data_from_ave(data_param, batch_size, time_step, train_begin, train_end):
    time_step_temp = time_step
    batch_index=[]
    data_train=data_param[train_begin:train_end]

    # 标准化 出错，原因是ratio是字符串
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)

    # 训练集
    train_x,train_y=[], []

    # 此时normalized_train_data的shape是n*8
    for i in range(int(math.floor(len(normalized_train_data)/time_step))):       # i = 1~5785

       # 生成batch_index：0，batch_size*1，batch_size*2
       if i % batch_size==0:
           batch_index.append(i)

       # 获取了一个样本,dataframe 对于loc的区间选择采用的是“前闭后闭”，所以我们需要在后面减1来实现前闭后开
       x= normalized_train_data.loc[i*time_step_temp:(i+1)*time_step_temp-1, ['close_now', 'mean30', 'mean60', 'mean180']]
       y= normalized_train_data.loc[i*time_step_temp:(i+1)*time_step_temp-1, 'm30inc_ratio']

       train_x.append(np.array(x))
       train_y.append(np.array(y)[:, np.newaxis])

    batch_index.append(int(math.floor(len(normalized_train_data)/time_step)))  # batch_index 收尾

    # train_x :n*15*7
    # train_y :n*15*1
    return batch_index, train_x, train_y



if __name__ == '__main__':
    model = ave_lstm(TIME_STEPS, INPUT_SIZE, OUTPUT_SIZE, CELL_SIZE, BATCH_SIZE)
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


    code_str = '300508'
    with open(g_debug_file_url+code_str + "ave-analysis-total.csv") as f:
        origin_data = pd.read_csv(f)

    origin_data = origin_data.loc[:, ['close_now', 'mean30', 'mean60', 'mean180', 'm30inc_ratio']]

    batch_index, train_x, train_y = get_train_data_from_ave(origin_data, time_step=TIME_STEPS,
                                                             batch_size=BATCH_SIZE, train_begin=0, train_end=450)
    for j in range(50):
        for i in range(6):    # 遍历batch

            i_range = 6

            if (i == 0) & (j==0):
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
            plt.plot(np.linspace((i+i_range*j)*BATCH_SIZE,(i+i_range*j+1)*BATCH_SIZE-1,BATCH_SIZE),
                     list(map(lambda x:x[TIME_STEPS-1],train_y[batch_index[i]:batch_index[i+1]])), 'r*--',

                     np.linspace((i+i_range*j)*BATCH_SIZE,(i+i_range*j+1)*BATCH_SIZE-1,BATCH_SIZE),
                     list(map(lambda x: x[TIME_STEPS-1],pred.reshape([-1,TIME_STEPS]))), 'bo--')

            # plt.ylim((-1.2, 1.2))

            plt.pause(0.3)

            print('cost: ', round(cost, 4))
            result = sess.run(merged, feed_dict)
            writer.add_summary(result, i+j*100)

    saver.save(sess=sess, save_path='./modelDir/' + 'lstmModel' + get_current_date_str() + '.ckpt')
    plt.draw()
    end = 0