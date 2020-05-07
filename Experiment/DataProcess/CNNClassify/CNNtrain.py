# encoding = utf-8

from sdk.SDKHeader import *
from DataProcess.CNNClassify.GlobalSetting_CNNtest import *



# dict_list = merge_batch_from_csv(g_total_stk_code[0:20],save_dir,50,label_field_list,feature_field_list,20)
dict_list = merge_batch_from_csv(g_total_stk_code[0:500],50,label_field_list,feature_field_list,20,save_dir)
# dict_list = merge_batch_from_csv(g_total_stk_code[0:50],50,label_field_list,feature_field_list_ave,20,save_dir_ave)

#TODO 将字典列表保存为json

# 创建session并初始化所有默模型参数
sess = tf.InteractiveSession()


# tf.global_variables_initializer().run()
model = CNN2(batch_size=batch_size,output_size = output_size,input_x = input_x,input_y = input_y,cov_x = cov_x,cov_y = cov_y)


# 创建保存器用于模型
saver = tf.train.Saver()
loss_list = list()


# 开始训练模型
for interalbe in range(50):

    for step in range(int(math.floor(len(dict_list)/batch_size))):

        # 记录起始时间，用于计算耗时
        start_time = time.time()

        # 读取训练数据
        # image_batch = dict_list[step]["image"]
        image_batch = np.array(list(map(lambda x: x["image"], dict_list[step*batch_size:(step+1)*batch_size]))).reshape([batch_size,input_x,input_y])

        # 获取label绝对值
        label_abs = list(map(lambda x: grade(x["label"][0] * 100), dict_list[step * batch_size:(step + 1) * batch_size]))
        label_batch = np.array(label_abs).reshape([batch_size])

        # 进行训练
        _, loss_value = sess.run([model.train_op, model.loss], feed_dict={model.image_holder:image_batch,
                                                              model.label_holder: label_batch})

        loss_list.append(loss_value)
        duration = time.time() - start_time

        # 打印误差及每个样本的训练耗时
        if step % 10 == 0:
            examples_per_sec = batch_size / duration
            sec_per_batch = float(duration)

            format_str = ('step %d, loss = %.2f (%.1f examples/sec; %.3f sec/batch)')
            print(format_str % (step, pd.Series(loss_list).mean(), examples_per_sec, sec_per_batch))
            loss_list = list()

saver.save(sess=sess, save_path='./modelDir/' + 'cnnModel.ckpt')
