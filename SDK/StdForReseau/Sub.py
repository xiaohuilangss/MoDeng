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
    def df_win_std(df, win):
        for idx in df.tail(len(df) - win + 1).index:
            df_part = df.loc[idx - win + 1:idx, :]
            df.loc[idx, 'std_' + str(win)] = np.std(df_part.loc[:, ['close', 'low', 'high']].values)
        return df

    def get_single_stk_reseau_sub(self, df, slow=6, quick=3):
        """
        :param df:
        :return:
        """
        df = df.reset_index()

        df = self.df_win_std(df, 3)
        df = self.df_win_std(df, 6)

        df['std_m'] = df.apply(lambda x: np.mean([x['std_3'], x['std_6']]), axis=1)

        return df.tail(1)['std_m'].values[0]

    def get_single_stk_reseau(self, stk_code):
        """
        计算单只stk的当前网格
        :return:
        """
        # df = my_pro_bar(stk_code=stk_code, start=add_date_str(get_current_date_str(), -10))
        df = get_k_data_JQ(stk=stk_code, start_date=add_date_str(get_current_date_str(), -10),
                           end_date=get_current_date_str())

        if len(df) < 7:
            # df = my_pro_bar(stk_code=stk_code, start=add_date_str(get_current_date_str(), -30))
            df = get_k_data_JQ(stk=stk_code, start_date=add_date_str(get_current_date_str(), -30),
                               end_date=get_current_date_str())

        return self.get_single_stk_reseau_sub(df)


"""
df.plot('date', ['close', 'std_m'], subplots=True)
"""

if __name__ == '__main__':
    df = ts.get_k_data('000001')
    win = 3
    df = df.reset_index()

    r = get_single_stk_reseau('300508')
    end = 0
