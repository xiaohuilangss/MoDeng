# encoding=utf-8

"""
本脚本用于维护一个本地的数据源
"""

# jq_login()
from DataSource.Data_Sub import get_k_data_JQ, get_all_stk
import os
import pandas as pd

from DataSource.auth_info import jq_login
from SDK.MyTimeOPT import get_current_datetime_str, add_date_str


class LocalData:
    """
    数据本地化相关类
    """
    def __init__(self, stk_code, freq, save_dir):
        self.save_dir = save_dir
        self.save_url = self.save_dir + str(stk_code) + '.json'
        self.freq = freq
        self.stk_code = stk_code

        self.init_count = 800

        self.df = None

        # 创建保存文件夹
        self.make_dir()

        self.log = ''

    def download_data(self):
        """
        初次下载数据
        :return:
        """
        self.df = get_k_data_JQ(stk=self.stk_code, count=self.init_count)

    def make_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def save(self):
        self.df.to_json(self.save_url)

    def load(self):
        if os.path.exists(self.save_url):
            self.df = pd.read_json(self.save_url)
            return True
        else:
            return False

    def update(self):
        """
        下载更新的数据
        :return:
        """

        if not self.is_time_to_update():
            self.log = self.log + '当前时刻靠近交易时段，不便更新数据！\n'
            return False

        if not self.load():
            self.download_data()
            self.save()
            self.log = self.log + '未检测到历史数据，全新下载数据！\n'
            return True

        df_append = get_k_data_JQ(self.stk_code, start_date=self.get_update_start_date())

        # 清除交易量为0的数据
        df_append = df_append[df_append.apply(lambda x:x['volume'] > 0, axis=1)]

        if not df_append.empty:
            self.df = pd.concat([self.df, df_append], axis=0)
            self.save()
            self.log = self.log + '完成追加最新数据！\n'
            return True
        else:
            self.log = self.log + '没有新数据！\n'
            return True

    def get_update_start_date(self):
        """
        获取已下载数据的最后日期
        :return:
        """

        return add_date_str(str(self.df.tail(1)['datetime'].values[0])[:10], 1)

    def read(self):
        if os.path.exists(self.save_url):
            self.df = pd.read_json(self.save_url)
            return df
        else:
            return pd.DataFrame()

    @staticmethod
    def is_time_to_update():
        """
        判断当前是否允许更新数据
        开盘前（上午9点之前）收盘后（下午3点半之后）
        :return:
        """
        time_now = int(get_current_datetime_str()[-7:-4].replace(':', ''))
        if (time_now < 800) | (time_now > 1530):
            return True
        else:
            return False

    @staticmethod
    def read_stk(stk_, freq_):
        """
        读取本地数据
        :param stk_:
        :param freq_:
        :return:
        """
        local_data_dir = 'C:/Users\paul\Desktop\localdata/' + freq_ + '/'
        return pd.read_json(local_data_dir + stk_ + '.json')



if __name__ == '__main__':

    freq = 'd'
    jq_login()

    local_data_dir = 'C:/Users\paul\Desktop\localdata/'+freq+'/'
    df = pd.read_json(local_data_dir+'300183.json')

    for stk in get_all_stk():

        ld = LocalData(stk, freq, local_data_dir)
        ld.update()
        print(ld.log)

    end = 0