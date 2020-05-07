# encoding = utf-8

from sdk.SDKHeader import *

"""
使用代码案例：

    1、创建模型
    model = ave_lstm(TIME_STEPS, INPUT_SIZE, OUTPUT_SIZE, CELL_SIZE, BATCH_SIZE)
    sess = tf.Session()

    将可视化数据写入文件（可有可无）
    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter(r'logs/', tf.get_default_graph())

    2、进行初始化
    sess.run(tf.global_variables_initializer())
    
    3、构造输入字典：feed_dict是TensorFlow世界与外界的数据通道！
    
                    feed_dict = {
                        model.xs: train_x[batch_index[i]:batch_index[i+1]],
                        model.ys: train_y[batch_index[i]:batch_index[i+1]],
                        # create initial state
                }
                
    4、将 数据输入到 TF 模型中，启动模型内部的相关函数，feed_dict支持 np.array 格式的数据 
                _, cost, state, pred = sess.run(
                [model.train_op, model.cost, model.cell_final_state, model.pred],
                feed_dict=feed_dict)


    保存模型
    saver.save(sess=sess, save_path='./modelDir/' + 'lstmModel' + get_current_date_str() + '.ckpt')
    
"""


LR = 0.2

class LSTMRNN(object):
    def __init__(self, n_steps, input_size, output_size, cell_size, batch_size):
        """

        :param n_steps:             步数
        :param input_size:          输入维度
        :param output_size:         输出维度
        :param cell_size:           隐含层维度
        :param batch_size:          batch大小
        """

        self.n_steps = n_steps
        self.input_size = input_size
        self.output_size = output_size
        self.cell_size = cell_size
        self.batch_size = batch_size

        with tf.name_scope('inputs'):
            self.xs = tf.placeholder(tf.float32, [None, n_steps, input_size], name='xs')
            self.ys = tf.placeholder(tf.float32, [None, n_steps, output_size], name='ys')

        with tf.variable_scope('in_hidden'):
            self.add_input_layer()

        with tf.variable_scope('LSTM_cell'):
            self.add_cell()

        with tf.variable_scope('out_hidden'):
            self.add_output_layer()

        with tf.name_scope('cost'):
            self.compute_cost()

        """
        注意这一句与之前的区别在于，这一句对类中的变量进行了赋值
        """
        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(LR).minimize(self.cost)

    def add_input_layer(self):
        """
        定义输入层
        关键的参数时输入层的size
        :return:
        """

        if g_lstm_debug_enable:
            write_to_txt(g_debug_file_url+g_lstm_debug_file_name, "开始进入add_input_layer函数，设置输入层！\n")

        """ 对输入进行整形 """
        l_in_x = tf.reshape(self.xs, [-1, self.input_size], name='2_2D')  # (batch*n_step, in_size)

        """ 
        定义输入变量的权重矩阵       
        Ws (in_size, cell_size) 
        """
        Ws_in = self._weight_variable([self.input_size, self.cell_size])

        """ 
        定义输入变量的偏置           
        bs (cell_size, ) 
        """
        bs_in = self._bias_variable([self.cell_size])

        """ 
        计算输出      
        l_in_y = (batch * n_steps, cell_size) 
        """
        with tf.name_scope('Wx_plus_b'):
            l_in_y = tf.matmul(l_in_x, Ws_in) + bs_in

        """
        对输出进行整形           
        reshape l_in_y ==> (batch, n_steps, cell_size)
        """
        self.l_in_y = tf.reshape(l_in_y, [-1, self.n_steps, self.cell_size], name='2_3D')

    def add_cell(self):
        """
        定义lstm的cell层
        关键的参数是隐含层的数量
        :return:
        """
        lstm_cell = tf.contrib.rnn.BasicLSTMCell(self.cell_size, forget_bias=1.0, state_is_tuple=True)

        with tf.name_scope('initial_state'):
            self.cell_init_state = lstm_cell.zero_state(self.batch_size, dtype=tf.float32)
            self.cell_outputs, self.cell_final_state = tf.nn.dynamic_rnn(
                lstm_cell, self.l_in_y, initial_state=self.cell_init_state, time_major=False)

    def add_output_layer(self):

        """
        对cell的输出进行整形
        shape = (batch * steps, cell_size)
        """
        l_out_x = tf.reshape(self.cell_outputs, [-1, self.cell_size], name='2_2D')

        """
        定义输出变量的权重矩阵
        """
        Ws_out = self._weight_variable([self.cell_size, self.output_size])

        """
        定义输出变量的偏值
        """
        bs_out = self._bias_variable([self.output_size, ])

        """
        计算输出变量的前向计算结果     
        shape = (batch * steps, output_size)
        """
        with tf.name_scope('Wx_plus_b'):
            self.pred = tf.matmul(l_out_x, Ws_out) + bs_out

    def compute_cost(self):
        """
        计算损失的函数
        :return:
        """

        if g_lstm_debug_enable:
            write_to_txt(g_debug_file_url+g_lstm_debug_file_name, "开始进入compute_cost函数，计算当前损失！\n")

        pred_shaped = tf.reshape(self.pred, [-1, self.n_steps], name='reshape_pred')
        pred_slice = pred_shaped[:, self.n_steps-1]

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
            tf.summary.scalar('batch_size', self.batch_size)

    def ms_error(self, labels, logits):
        return tf.square(tf.subtract(labels, logits))

    def _weight_variable(self, shape, name='weights'):
        initializer = tf.random_normal_initializer(mean=0., stddev=1.,)
        return tf.get_variable(shape=shape, initializer=initializer, name=name)

    def _bias_variable(self, shape, name='biases'):
        initializer = tf.constant_initializer(0.1)
        return tf.get_variable(name=name, shape=shape, initializer=initializer)
