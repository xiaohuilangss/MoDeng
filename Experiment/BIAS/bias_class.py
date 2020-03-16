# encoding=utf-8

"""
bias相关的类
"""
from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login
from Global_Value.file_dir import data_dir

import json
import os

from SDK.DataPro import relative_rank


class BIAS:
    def __init__(self, stk_code, freq, hist_count=2000, span_q=3, span_s=15, local_data_dir=data_dir + 'BIAS/'):
        self.hist_count = hist_count
        self.span_s = span_s
        self.span_q = span_q
        self.local_data_dir = local_data_dir
        self.freq = freq
        self.stk_code = stk_code

        self.bias_dict = {}
        self.json_file_name = self.local_data_dir + \
                   'bias' + \
                   self.stk_code + \
                    '_' + self.freq + \
                   '_' + \
                   str(self.span_q) + \
                   '_' + str(self.span_s) + \
                   '.json'
        
        self.log = ''
        
        # 初始化bias数据，如果本地文件有，则直接读取，否则现场制作，并存入本地
        if not self.load_bias_from_json():
            self.gen_hist_data()
            self.save_bias_to_json()
        
    def add_bias(self, df):
        
        df['line_q'] = df['close'].rolling(window=self.span_q).mean()
        df['line_s'] = df['close'].rolling(window=self.span_s).mean()
    
        df['bias'] = df.apply(lambda x: x['line_q'] - x['line_s'], axis=1)
        return df.dropna(axis=0)
        
    def gen_hist_data(self):
        """
        将历史bias数据保存到本地
        :return:
        """
        df = get_k_data_JQ(stk=self.stk_code, freq=self.freq, count=self.hist_count)
        
        bias_values = self.add_bias(df)['bias'].values
        
        bias_p = list(filter(lambda x: x >= 0, bias_values))
        bias_n = list(filter(lambda x: x < 0, bias_values))
        
        self.bias_dict = {
            'bias_p': bias_p,
            'bias_n': bias_n
        }
    
    def save_bias_to_json(self, name=''):
        """
        将bias文件的数据存到json文件中
        :param name:
        :return:
        """
        if not os.path.exists(self.local_data_dir):
            os.makedirs(self.local_data_dir)
            
        with open(self.json_file_name, 'w') as f:
            json.dump(self.bias_dict, f)
            
    def load_bias_from_json(self):
        """
        从json文件中读取bias数据
        :return:
        """
        if os.path.exists(self.json_file_name):
            try:
                with open(self.json_file_name, 'r') as f:
                    self.bias_dict = json.load(f)
                    return True
            except Exception as e:
                self.log = str(e)
                return False
        else:
            return False
    
    def cal_rank_now(self, bias_now=None):
        """
        给定一个值，计算相对bias
        :param bias_now:
        :return:
        """
        if bias_now is None:
            bias_now = self.cal_rt_bias()
        
        if bias_now >= 0:
            return relative_rank(self.bias_dict['bias_p'], bias_now)
        else:
            return relative_rank(self.bias_dict['bias_n'], bias_now) - 100
        
    def cal_rt_bias(self):
        """
        实时计算bias
        :return:
        """
        df = get_k_data_JQ(stk=self.stk_code, freq=self.freq, count=self.span_s + 2)
        df_bias = self.add_bias(df)
        
        return df_bias.tail(1)['bias'].values[0]

    def plot_test(self):
        """
        用以测试效果
        :return:
        """
        df = get_k_data_JQ(stk=self.stk_code, freq=self.freq, count=self.hist_count)
        df_bias = self.add_bias(df)

        # 增加rank数据
        df_bias['rank'] = df_bias.apply(lambda x: self.cal_rank_now(x['bias']), axis=1)

        df_bias.reset_index().reset_index().plot('level_0', ['close', 'rank'], subplots=True, style='*--')


if __name__ == '__main__':
    jq_login()

    # bias_obj_1m = BIAS(stk_code='300183', freq='1m')
    # bias_obj_1m.plot_test()

    bias_obj_1d = BIAS(stk_code='300183', freq='1d')
    bias_obj_1d.plot_test()

    end = 0