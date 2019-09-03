# encoding=utf-8

"""
根据标准差来计算格子
"""
import tushare as ts
import numpy as np

# from RelativeRank.Sub import my_pro_bar, get_k_data_JQ
from Experiment.RelativeRank.Sub import my_pro_bar
from SDK.MyTimeOPT import add_date_str, get_current_date_str

df = ts.get_k_data('000001')
win = 3
df = df.reset_index()


def df_win_std(df, win):

    for idx in df.tail(len(df)-win+1).index:
        df_part = df.loc[idx-win+1:idx, :]
        df.loc[idx, 'std_'+str(win)] = np.std(df_part.loc[:, ['close', 'low', 'high']].values)
    return df





def getSigleStkReseau(stk_code):
    """
    计算单只stk的当前网格
    :return:
    """
    df = my_pro_bar(stk_code=stk_code, start=add_date_str(get_current_date_str(), -10))
    # df = get_k_data_JQ(stk_code=stk_code, start_date=add_date_str(get_current_date_str(), -10),
    #                    end_date=get_current_date_str())

    if len(df) < 7:
        df = my_pro_bar(stk_code=stk_code, start=add_date_str(get_current_date_str(), -30))
        # df = get_k_data_JQ(stk_code=stk_code, start_date=add_date_str(get_current_date_str(), -30),
        #                    end_date=get_current_date_str())

    df = df.reset_index()

    df = df_win_std(df, 3)
    df = df_win_std(df, 6)

    df['std_m'] = df.apply(lambda x: np.mean([x['std_3'], x['std_6']]), axis=1)

    return df.tail(1)['std_m'].values[0]


"""
df.plot('date', ['close', 'std_m'], subplots=True)
"""

if __name__ == '__main__':

    r = getSigleStkReseau('300508')
    end = 0