# encoding = utf-8

from sdk.SDKHeader import *
from DataProcess.CNNClassify.GlobalSetting_CNNtest import *


# 准备测试数据

# 第二套数据
data_list = merge_batch_from_csv(g_total_stk_code[0:500],50,label_field_list,feature_field_list,20,save_dir)

# 第一套数据
# data_list = merge_batch_from_csv(g_total_stk_code[0:500],50,label_field_list,feature_field_list_ave,20,save_dir_ave)

# model = CNN2(batch_size)


# 加载模型
sess = tf.InteractiveSession()
# saver.save(sess=sess, save_path='./modelDir/' + 'cnnModel.ckpt')

saver = tf.train.import_meta_graph('./modelDir/' + 'cnnModel.ckpt.meta')
saver.restore(sess, tf.train.latest_checkpoint('./modelDir/'))

graph = tf.get_default_graph()
x = graph.get_tensor_by_name("inputs/image:0")
logits = graph.get_tensor_by_name("logits/logits:0")


result_final = []
for example in range(0,int(len(data_list)/batch_size)):

    # 获取一个batch的数据
    single_batch = np.array(list(map(lambda x:x["image"],data_list[example*batch_size:(example+1)*batch_size]))).reshape([batch_size,input_x,input_y])

    feed_dict = {x: single_batch}
    classification_result = tf.nn.softmax(sess.run(logits, feed_dict))
    result = sess.run(tf.nn.softmax(classification_result))
    print(str(result))
    result_final.extend(result)

end = 0