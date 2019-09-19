# encoding = utf-8

from SDK.SDKHeader import *


def get_class_df_by_code(code,belongto_info,class_df_list):

    """
    根据代码获取其所属class的df
    :param code:
    :param belongto_info:  stk 所属class信息
    :param class_df_list:   各个class的df列表
    :return:
    """

    class_belong = get_class_stk_belong(code,belongto_info)

    return list(filter(lambda x: x['b_ele'] == class_belong, class_df_list))[0]['b_Q']


def prepare_lstm_data(code,df_class_belong_to,predict_depth,batch_size):

    """
    为lstm准备训练数据
    :param code:
    :param df_class_belong_to: 所属class的df，需要升序排序后输入
    :param predict_depth:
    :param batch_size:
    :return:
    """

    _batch_size = batch_size

    # 下载测试数据
    df = get_total_table_data(conn_k, 'k'+code).sort_values(by='date', ascending=True)

    # 添加MACD信息
    df_MACD = get_MACD(df)

    # 精简列,并时间降序，用以计算未来增长情况
    df_MACD = df_MACD.loc[:, ['close', 'date', 'MACD', 'volume','low','high']].sort_values(by='date', ascending=False)

    # 增加未来预测天数内天最大值
    df_MACD['close_max_' + str(predict_depth)] = df_MACD.close.rolling(window=predict_depth).max()

    # 计算“当前值”与“未来10天最大值”之间的变化幅度
    df_MACD['inc_ratio_' + str(predict_depth)] = df_MACD.apply(
        lambda x: (x['close_max_' + str(predict_depth)] - x['close']) / (x['close'] + 0.000000000000001), axis=1)

    # 去除存在控制的行
    df_MACD = df_MACD.dropna(axis=0)

    # 恢复为时间升序
    df_MACD = df_MACD.sort_values(by='date', ascending=True)

    MACD_min = df_MACD.MACD.min()
    MACD_max = df_MACD.MACD.max()

    close_min = df_MACD.close.min()
    close_max = df_MACD.close.max()

    volume_min = df_MACD.volume.min()
    volume_max = df_MACD.volume.max()

    df_MACD['MACD'] = (df_MACD.MACD - MACD_min) / (MACD_max - MACD_min)
    df_MACD['close'] = (df_MACD.close - close_min) / (close_max - close_min)
    df_MACD['volume'] = (df_MACD.volume - volume_min) / (volume_max - volume_min)
    df_MACD['high'] = (df_MACD.high - df_MACD.high.min()) / (df_MACD.high.max() - df_MACD.high.min())
    df_MACD['low'] = (df_MACD.low - df_MACD.low.min()) / (df_MACD.low.max() - df_MACD.low.min())


    # 如果有输入所属class的df，即参数df_class_belong_to不为空，则计算其所属class相关MACD， 并将其与stk的df按日期合并
    if len(df_class_belong_to):

        # 计算class的MACD
        class_df = get_MACD(df_class_belong_to.rename(columns={'c_close':'close'})).rename(columns={'MACD':'c_MACD','close':'c_close'})

        # 对class中的df进行归一化
        class_df['c_MACD'] = (class_df.c_MACD-class_df.c_MACD.min())/(
                class_df.c_MACD.max() - class_df.c_MACD.min())

        class_df['c_volume'] = (class_df.c_volume - class_df.c_volume.min()) / (
                    class_df.c_volume.max() - class_df.c_volume.min())

        class_df['c_close'] = (class_df.c_close - class_df.c_close.min()) / (
                    class_df.c_close.max() - class_df.c_close.min())

        df_MACD = pd.concat([df_MACD.set_index(keys='date',drop=True),class_df.set_index(keys='date',drop=True).loc[:,['c_close','c_volume','c_MACD','c_open']]],join='inner',axis=1).reset_index()


    # 组成学习样本list
    example_list = []
    for id in df_MACD.loc[predict_depth:, :].index:
        example_list.append(
            np.array([np.array(df_MACD.loc[id - predict_depth:id - 1, ['MACD', 'volume', 'close','high','low','c_MACD','c_volume','c_close']]),
                      np.array(df_MACD.loc[id - 1, 'inc_ratio_' + str(predict_depth)])])
        )

    # 组成batch
    batch_list = []
    for i in range(0, len(example_list), _batch_size):
        feature = np.array(list(map(lambda x: x[0], example_list[i:i + _batch_size])))
        label = np.array(list(map(lambda x: x[1], example_list[i:i + _batch_size])))[:, newaxis]
        batch_list.append([feature, label])

    return batch_list



# ------------------------------ 测试 -------------------------------------------

# code = '300508'
#
# # 获取stk与class的映射信息
# belongto = get_stk_belongto_info()
#
# # 获取各个class信息
# class_df_list = get_class_df()
#
# # 获取该stk对应的classdf
# class_df = get_class_df_by_code(code=code,belongto_info=belongto,class_df_list=class_df_list)
#
#
# df = prepare_lstm_data('300508',class_df,20,30)
#
# end = 0