# encoding=utf-8

"""
根据标准差来计算格子
"""
import tushare as ts
import numpy as np

from DataSource.Data_Sub import get_k_data_JQ
from SDK.MyTimeOPT import add_date_str, get_current_date_str


class Reseau:
    """
    动态网格策略底层实现类
    """
    def __init__(self):
        pass

    @staticmethod
    def df_win_std(df_, win_):
        """
        计算给定周期内的“收盘价”、“最高价”、“最低价”的标准差
        :param df_:
        :param win_:
        :return:
        """
        for idx in df_.tail(len(df_) - win_ + 1).index:
            df_part = df_.loc[idx - win_ + 1:idx, :]
            df_.loc[idx, 'std_' + str(win_)] = np.std(df_part.loc[:, ['close', 'low', 'high']].values)
        return df_

    def get_single_stk_reseau_sub(self, df_, slow=6, quick=3):
        """
        计算动态网格
        :param quick:
        :param slow:
        :param df_:
        :return:
        """
        df_ = df_.reset_index(drop=True)
        df_ = self.df_win_std(df_, quick)
        df_ = self.df_win_std(df_, slow)

        df_['std_m'] = df_.apply(lambda x: np.mean([x['std_' + str(quick)], x['std_' + str(slow)]]), axis=1)

        return df_.tail(1)['std_m'].values[0]

    def get_single_stk_reseau(self, stk_code):
        """
        计算单只stk的当前网格
        :return:
        """
        # df = my_pro_bar(stk_code=stk_code, start=add_date_str(get_current_date_str(), -10))
        df_ = get_k_data_JQ(stk=stk_code, start_date=add_date_str(get_current_date_str(), -10),
                            end_date=get_current_date_str())

        if len(df_) < 7:
            # df = my_pro_bar(stk_code=stk_code, start=add_date_str(get_current_date_str(), -30))
            df_ = get_k_data_JQ(stk=stk_code, start_date=add_date_str(get_current_date_str(), -30),
                                end_date=get_current_date_str())

        return self.get_single_stk_reseau_sub(df_)


"""
df.plot('date', ['close', 'std_m'], subplots=True)
"""

if __name__ == '__main__':
    df = ts.get_k_data('000001')
    win = 3
    df = df.reset_index()

    r = get_single_stk_reseau('300508')
    end = 0
