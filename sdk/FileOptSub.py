# encoding = utf-8
from Config.GlobalSetting import *
import pathlib
import csv
import os

# 此文件是关于文件操作的自定义函数的文件


'''
用来将字典列表写入csv
@:return true成功  false失败
'''
def write_dict_list_to_csv(list_param,file_url):

    if len(list_param)==0:
        print("函数write_dict_list_to_csv：入参是空list！")
        return False

    if not type(list_param[0])==type({"1":1}):
        print("函数write_dict_list_to_csv：入参的类型不是list-dict！")
        return False

    # 判断文件是否已经存在,不存在则在写入时加上header，若存在则之间将values写入，以此避免header重复
    file_path = pathlib.Path(file_url)
    if file_path.exists():
        with open(file_url,'a',newline='',encoding='utf-8') as f:
            try:
                w = csv.writer(f)
                # w.writerow(list_param[0].keys())
                for row in list_param:
                    w.writerow(row.values())
            finally:
                f.close()
    else:
        with open(file_url,'a',newline='',encoding='utf-8') as f:
            try:
                w = csv.writer(f)
                w.writerow(list_param[0].keys())
                for row in list_param:
                    w.writerow(row.values())
            finally:
                f.close()


'''
txt文件快速写入
**kwargs 中字段：
noline：表示不自动换行，默认自动换行
'''
def write_to_txt(file_url_param,contents_param,**kwargs):
    f = open(file_url_param,"a",encoding="utf-8")
    if "noline" in kwargs:
        if kwargs["noline"]:
            f.write(contents_param)
    else:
        f.writelines(contents_param)

    f.close()


def read_csv_to_dict_list(file_url):
    list_dict = []

    # 判断文件是否已经存在,不存在则在写入时加上header，若存在则之间将values写入，以此避免header重复
    file_path = pathlib.Path(file_url)
    if file_path.exists():

        with open(file_url,"r") as csv_file:
            dict_reader = csv.DictReader(csv_file)
            for i in dict_reader:
                list_dict.append(dict(i))
    else:
        print("函数read_csv_to_dict_list：入参的类型不是list-dict！")

    return list_dict

# 从csv中读取数据，并转为dataframe
def read_csv_to_df(file_url_param):
    with open(file_url_param) as f:
        return pd.read_csv(f)


def eachFile(s):

    """
    返回该目录下的所有文件的完整URL，list格式
    :param s:
    :return:
    """

    fileList = []
    for parent, dirnames, filenames in os.walk(s):  # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:
            print("the full name of the file is:" + os.path.join(parent, filename))  # 输出文件路径信息
            fileList.append(os.path.join(parent, filename))

    return fileList
