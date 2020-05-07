# encoding = utf-8
from sdk.SDKHeader import *

save_dir = "F:/MYAI/文档资料/用于读取的文件/cnn_data/"
save_dir_ave = "F:/MYAI/文档资料/用于读取的文件/cnn_data_ave/"

"""
当前有两套数据：
（1）只有均值的数据
（2）包含均值和volume的数据

在使用第一套时，数据准备、训练、预测都需要用路径“save_dir_ave”
在使用第二套时，数据准备、训练、预测都需要用路径“save_dir”

"""



field_list_volume = ['big_in','big_out','total_in','total_out']
time_span_list_volume = [14,30,60,180]
label_field_list = ["close_mean30_inc_ratio"]
feature_field_list = ["close_mean14","close_mean30","close_mean60","close_mean180"]+merge_field_mean(field_list_volume,time_span_list_volume)
feature_field_list_ave = ["close_mean14","close_mean30","close_mean60","close_mean180"]



# CNN类参数定义
batch_size = 100
output_size = 6

input_x = 20
input_y = 20

cov_x = 1
cov_y = 8

