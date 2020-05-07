# encoding = utf-8
from sdk.DBOpt import *
from Config.GlobalSetting import conn_k

def get_class_df():

    """
    获取上证、深证、创业板、中小板的数据
    :return:
    """

    basic_Q = []

    for b_ele in ['sh', 'sz', 'cyb', 'zxb']:

        # 从数据库获取上证数据
        df_b = get_total_table_data(conn_k, 'k' + b_ele)

        # 对大盘数据进行处理
        class_df = df_b.rename(columns={'volume': 'c_volume', 'close': 'c_close', 'open': 'c_open'}) \
                        .loc[:, ['c_close', 'c_open', 'c_volume', 'date']] \
                        .set_index(keys='date')

        class_df['c_change_ratio'] = class_df.apply(lambda x: (x['c_close'] - x['c_open'])/x['c_open'], axis=1)

        basic_Q.append({'b_ele': b_ele,
                        'b_Q': class_df})

    return basic_Q


def get_stk_classified_data(index_list,code):

    """
    根据stk所在类，获取其大盘数据

    :param basic_Q:                 stk四大类的季度变化率
    :param code_belongto_info:      stk所属类的信息
    :param code:                    stk代码
    :return:

    """

    # 获取该stk所属的类型
    if str(code)[0:3] == '300':
        belongto = 'cyb'

    elif str(code)[0:3] == '002':
        belongto = 'zxb'

    elif str(code)[0] == '6':
        belongto = 'sh'

    elif str(code)[0] == '0':
        belongto = 'sz'

    # 获取这个类型的变化率
    class_quarter_list = list(filter(lambda x:x['b_ele']== belongto,index_list))

    class_df = class_quarter_list[0]['b_Q']

    return class_df

def stk_k_pro(k_df):
    """

    处理个股的K数据

    :param code:
    :param date_start:
    :param date_end:
    :return:
    """

    if len(k_df):

        k_df['change_ratio'] = k_df.apply(lambda x:(x['close']-x['open'])/x['open'],axis=1)

        return k_df.set_index(keys='date')
    else:
        return pd.DataFrame()



def cal_relative_ratio(code,index_list,date_start,date_end):

    """
    给定stk代码，大盘数据，起止时间，返回包含“相对变化率差”的df
    :param code:
    :param index_list:
    :param date_start:
    :param date_end:
    :return:
    """

    # 获取个股数据
    k_df = get_total_table_data(conn=conn_k,table_name='k'+code)
    k_df = k_df[(k_df.date>=date_start)&(k_df.date<=date_end)]

    stk_df = stk_k_pro(k_df=k_df)

    #获取该个股的大盘数据
    class_stk = get_stk_classified_data(index_list,code)

    # 合并数据
    df_merge = pd.concat([stk_df,class_stk],axis=1,join='inner')
    if len(df_merge):

        # 计算相对变化差
        df_merge['ratio_diff'] = df_merge.apply(lambda x:x['change_ratio'] - x['c_change_ratio'],axis=1)

        return df_merge
    else:
        return pd.DataFrame()




# ================== 测试 ==============================
# result = get_stk_classified_data(get_class_df(),'300508')
# result = cal_relative_ratio('300508',get_class_df(),'2017-11-09','2018-01-03')

# result = stk_k_pro('300508','2017-11-09','2018-01-03')
# end = 0