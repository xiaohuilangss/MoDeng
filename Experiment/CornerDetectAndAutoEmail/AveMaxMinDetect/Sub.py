# encoding = utf-8
def addMaxMinData(df_origin, days):

    """
    原始数据可能要用到high、low和close信息
    :param df_origin:
    :param days:
    :return:
    """
    df = df_origin

    df['Max'+str(days)] = df['close'].rolling(window=days, center=False).max()
    df['Min' + str(days)] = df['close'].rolling(window=days, center=False).min()

    return df


def get_h_l_pot(stk_list):
    """
    给定stklist，给出他们的“年度”、“半年度”、“月度”最高点和最低点！
    :param stk_list:
    :return:

      half_year_high  half_year_low  month_high  month_low     stk  year_high  \
0         1700.50        1205.03     1700.50    1316.10     cyb   1900.480
1         3106.42        2464.36     3106.42    2653.90      sh   3326.700
2         9700.49        7089.44     9700.49    7919.05      sz  11326.270
3           16.77          10.26       16.77      12.45  300508     19.656
4            8.94           5.68        8.94       7.79  000625     11.653
5            4.42           2.56        4.42       2.74  000725      5.972
    """

    current_date = get_current_date_str()               # 获取当前日期
    years_before = add_date_str(current_date, -365)     # 一年前日期
    half_year = add_date_str(current_date, -180)        # 半年前日期
    month_before = add_date_str(current_date, -30)      # 一月前日期

    # 存储结果的list
    MaxMinInfoList = []

    for stk in stk_list:

        # 下载数据
        df = ts.get_k_data(stk, start=years_before)

        # 计算年度高低点
        year_low = np.min(df['close'])
        years_high = np.max(df['close'])

        # 计算半年度高低点
        half_year_low = np.min(df[df['date'] > half_year]['close'])
        half_year_high = np.max(df[df['date'] > half_year]['close'])

        # 计算月度高低点
        month_low = np.min(df[df['date'] > month_before]['close'])
        month_high = np.max(df[df['date'] > month_before]['close'])

        MaxMinInfoList.append({
            'stk': stk,
            'year_low': year_low,
            'year_high': years_high,
            'half_year_low': half_year_low,
            'half_year_high': half_year_high,
            'month_low': month_low,
            'month_high': month_high
        })

    # 高低点转为df，这一天不再更改
    df_high_low_pot = pd.DataFrame(MaxMinInfoList)

    return df_high_low_pot


def lineJudge(current_price, df_info, line_str):

    """
    判断年线、半年线及月线情况

    :param current_price:
    :param df_info:
    :param line_str:        ‘year’ ‘half_year’ ‘month’
    :return:
    """

    df_H_L_Pot = df_info

    line_name = {
        'year': u'年线',
        'half_year': u'半年线',
        'month': u'月线'
    }.get(line_str)

    if 0 <= current_price - df_H_L_Pot.loc[stk, line_str+'_low'] < df_H_L_Pot.loc[stk, line_str+'_low'] * neighbor_len:  # 下探年线
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'接近'+line_name+'最低点'

    elif current_price - df_H_L_Pot.loc[stk, line_str+'_low'] < 0:
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'跌破'+line_name+'最低点'

    elif 0 <= df_H_L_Pot.loc[stk, line_str+'_high'] - current_price < df_H_L_Pot.loc[
        stk, line_str+'_high'] * neighbor_len:  # 上攻年线高点
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'接近'+line_name+'最高点'

    elif df_H_L_Pot.loc[stk, line_str+'_high'] - current_price < 0:
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'攻破'+line_name+'最高点'

    else:
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'正常'

    return df_H_L_Pot
