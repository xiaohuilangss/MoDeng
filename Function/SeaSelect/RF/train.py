# encoding=utf-8

"""
随机森林训练训练脚本
"""
import os
import pandas as pd

from DataSource.Data_Sub import get_all_stk
from DataSource.auth_info import jq_login
from Function.SeaSelect.RF.rf_data_pre_class import DataProRF, RF
from Function.SeaSelect.RF.global_values import *


class RFTrain:
    def __init__(self):
        pass

    @ staticmethod
    def get_stk_data(stk, freq='d'):
        data_pro_obj = DataProRF(stk, count=400, freq=freq)
        data_pro_obj.train_pro()
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        data_pro_obj.day_data.to_json(temp_dir + stk + '.json')
        print('完成%s的训练数据预处理' % stk)

        return data_pro_obj.day_data

    @staticmethod
    def load(s):
        """
        加载
        :param s:
        :return:
        """
        print('开始下载%s的数据！' % s)
        try:

            file_url = temp_dir + s + '.json'
            if os.path.exists(file_url):
                print(s + '本地数据已经存在，直接读取！')
                return pd.read_json(file_url)
            else:
                return RFTrain.get_stk_data(s, freq=freq)
        except Exception as e:
            print('%s数据预处理出错！原因：\n' % s + str(e))
            return pd.DataFrame()


if __name__ == '__main__':
    jq_login()

    s_all = get_all_stk()

    if not os.path.exists(temp_dir + 'total.json'):

        train_stk_list = get_all_stk()
        df = pd.concat(list(filter(lambda x: not x.empty, [RFTrain.load(x) for x in train_stk_list])))
        df.reset_index().to_json(temp_dir + 'total.json')

    else:
        df = pd.read_json(temp_dir + 'total.json')

    fl = DataProRF(None)

    # 生成随机森林模型
    rf = RF(df, fl.feature_col, fl.label_col)

    # 分割数据
    rf.splice_data(ratio=0.2)

    rf.load_model(save_dir=temp_dir)

    # 训练模型
    rf.train()

    rf.save_model(save_dir=temp_dir)

    print(rf.log)

    # 评估
    print(str(rf.evaluate(confidence_threshold=0.6)))