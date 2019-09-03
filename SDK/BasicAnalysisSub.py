# encoding = utf-8

'''
给定code，画出从起始到现在的基本面图
'''

from Config.GlobalSetting import  mpl, plt, conn_profit, conn_k, stk_profit_data_db_name, conn_growth, conn_operation, \
    conn_debtpaying, conn_cashflow, stk_growth_data_db_name, stk_operation_data_db_name, stk_debtpaying_data_db_name, \
    stk_cashflow_data_db_name,g_total_stk_code

from SDK.DBOpt import is_table_exist, get_total_table_data
from SDK.MyTimeOPT import get_current_date_str, get_quarter_date, cal_quarter
from pandas import DataFrame
import pandas as pd
import numpy as np

mpl.rcParams['font.sans-serif'] = ['SimHei']


def get_ss_sb(codeParam, basic_ele):

    """
    从profit数据库中获取每个stk的数据，转成Dataframe后按时间升序排序，返回！

    :param codeParam:
    :param basic_ele:
    :return:
    """
    result = []

    if basic_ele == "profit":

        for year in range(2001,int(get_current_date_str().split('-')[0]) +1):
            for quarter in range(1,5):

                table_name = 'profit' + str(year)+'0'+str(quarter)
                if (int(str(year)+'0'+str(quarter)) < int(get_quarter_date())) & is_table_exist(conn_profit,stk_profit_data_db_name,table_name):
                    db_df = get_total_table_data(conn=conn_profit,table_name = table_name)
                    single_basic_ele_data = db_df[db_df.code == codeParam]\
                    .reset_index(drop=True)\
                    .to_dict(orient='index')

                    if len(single_basic_ele_data):
                        single_basic_ele_data = single_basic_ele_data[0]
                        single_basic_ele_data.update({'date':str(year)+'0'+str(quarter)})
                        result.append(single_basic_ele_data)
                    else:
                        print("函数get_single_stk_single_basic：profit指标数据为空！季度为：" + str(year)+'0'+str(quarter))


    elif basic_ele == "growth":

        for year in range(2001, int(get_current_date_str().split('-')[0]) + 1):
            for quarter in range(1, 5):

                table_name = 'growth' + str(year) + '0' + str(quarter)
                if (int(str(year) + '0' + str(quarter)) < int(get_quarter_date())) & is_table_exist(conn_growth,
                                                                                                    stk_growth_data_db_name,
                                                                                                    table_name):
                    db_df = get_total_table_data(conn=conn_growth, table_name=table_name)
                    single_basic_ele_data = db_df[db_df.code == codeParam] \
                        .reset_index(drop=True) \
                        .to_dict(orient='index')

                    if len(single_basic_ele_data):
                        single_basic_ele_data = single_basic_ele_data[0]
                        single_basic_ele_data.update({'date': str(year) + '0' + str(quarter)})
                        result.append(single_basic_ele_data)
                    else:
                        print("函数get_single_stk_single_basic：growth指标数据为空！季度为：" + str(year)+'0'+str(quarter))


    elif basic_ele == "operation":

        for year in range(2001, int(get_current_date_str().split('-')[0]) + 1):
            for quarter in range(1, 5):

                table_name = 'operation' + str(year) + '0' + str(quarter)
                if (int(str(year) + '0' + str(quarter)) < int(get_quarter_date())) & is_table_exist(conn_profit,
                                                                                                    stk_operation_data_db_name,
                                                                                                    table_name):
                    db_df = get_total_table_data(conn=conn_operation, table_name=table_name)
                    single_basic_ele_data = db_df[db_df.code == codeParam] \
                        .reset_index(drop=True) \
                        .to_dict(orient='index')

                    if len(single_basic_ele_data):
                        single_basic_ele_data = single_basic_ele_data[0]
                        single_basic_ele_data.update({'date': str(year) + '0' + str(quarter)})
                        result.append(single_basic_ele_data)
                    else:
                        print("函数get_single_stk_single_basic：operation指标数据为空！季度为：" + str(year)+'0'+str(quarter))


    elif basic_ele == "debtpaying":

        for year in range(2001, int(get_current_date_str().split('-')[0]) + 1):
            for quarter in range(1, 5):

                table_name = 'debtpaying' + str(year) + '0' + str(quarter)
                if (int(str(year) + '0' + str(quarter)) < int(get_quarter_date())) & is_table_exist(conn_debtpaying,
                                                                                                    stk_debtpaying_data_db_name,
                                                                                                    table_name):
                    db_df = get_total_table_data(conn=conn_debtpaying, table_name=table_name)
                    single_basic_ele_data = db_df[db_df.code == codeParam] \
                        .reset_index(drop=True) \
                        .to_dict(orient='index')

                    if len(single_basic_ele_data):
                        single_basic_ele_data = single_basic_ele_data[0]
                        single_basic_ele_data.update({'date': str(year) + '0' + str(quarter)})
                        result.append(single_basic_ele_data)
                    else:
                        print("函数get_single_stk_single_basic：debtpaying指标数据为空！季度为：" + str(year)+'0'+str(quarter))

    elif basic_ele == "cashflow":

        for year in range(2001, int(get_current_date_str().split('-')[0]) + 1):
            for quarter in range(1, 5):

                table_name = 'cashflow' + str(year) + '0' + str(quarter)
                if (int(str(year) + '0' + str(quarter)) < int(get_quarter_date())) & is_table_exist(conn_cashflow,
                                                                                                    stk_cashflow_data_db_name,
                                                                                                    table_name):
                    db_df = get_total_table_data(conn=conn_cashflow, table_name=table_name)
                    single_basic_ele_data = db_df[db_df.code == codeParam] \
                        .reset_index(drop=True) \
                        .to_dict(orient='index')

                    if len(single_basic_ele_data):
                        single_basic_ele_data = single_basic_ele_data[0]
                        single_basic_ele_data.update({'date': str(year) + '0' + str(quarter)})
                        result.append(single_basic_ele_data)
                    else:
                        print("函数get_single_stk_single_basic：cashflow指标数据为空！季度为：" + str(year)+'0'+str(quarter))


    else:
        print("函数get_single_stk_single_basic：不识别的basic指标  " + basic_ele)


    try:
        result = DataFrame(result).sort_values(by='date',ascending=True)
    except:
        result = DataFrame()
        print("函数get_single_stk_single_basic：遇到没有数据的指标！" + basic_ele)


    return result

def get_ss_sb_sq(codeParam, basic_ele, quarter):

    """
    下载“单个stk”的“单个basic方面”的“当前季度的basic信息”

    ss:single stk
    sb:single basic
    sq:single quarter
    :param codeParam:
    :return:
    """
    result = list()
    if basic_ele == "profit":

        table_name = 'profit' + quarter
        if is_table_exist(conn_profit,stk_profit_data_db_name,table_name):
            db_df = get_total_table_data(conn=conn_profit,table_name = table_name)
            single_basic_ele_data = db_df[db_df.code == codeParam]\
            .reset_index(drop=True)\
            .to_dict(orient='index')

            if len(single_basic_ele_data):
                single_basic_ele_data = single_basic_ele_data[0]
                single_basic_ele_data.update({'date':quarter})
                result.append(single_basic_ele_data)
            else:
                print("函数get_single_stk_single_basic：profit指标数据为空！季度为：" + quarter)

    elif basic_ele == "growth":

        table_name = 'growth' + quarter
        if is_table_exist(conn_growth,
                            stk_growth_data_db_name,
                            table_name):

            db_df = get_total_table_data(conn=conn_growth, table_name=table_name)
            single_basic_ele_data = db_df[db_df.code == codeParam] \
                .reset_index(drop=True) \
                .to_dict(orient='index')

            if len(single_basic_ele_data):
                single_basic_ele_data = single_basic_ele_data[0]
                single_basic_ele_data.update({'date': quarter})
                result.append(single_basic_ele_data)
            else:
                print("函数get_single_stk_single_basic：growth指标数据为空！季度为：" + quarter)

    elif basic_ele == "operation":

        table_name = 'operation' + quarter
        if is_table_exist(conn_profit,
                            stk_operation_data_db_name,
                            table_name):
            db_df = get_total_table_data(conn=conn_operation, table_name=table_name)
            single_basic_ele_data = db_df[db_df.code == codeParam] \
                .reset_index(drop=True) \
                .to_dict(orient='index')

            if len(single_basic_ele_data):
                single_basic_ele_data = single_basic_ele_data[0]
                single_basic_ele_data.update({'date': quarter})
                result.append(single_basic_ele_data)
            else:
                print("函数get_single_stk_single_basic：operation指标数据为空！季度为：" + quarter)

    elif basic_ele == "debtpaying":

        table_name = 'debtpaying' + quarter
        if is_table_exist(conn_debtpaying,
                            stk_debtpaying_data_db_name,
                            table_name):
            db_df = get_total_table_data(conn=conn_debtpaying, table_name=table_name)
            single_basic_ele_data = db_df[db_df.code == codeParam] \
                .reset_index(drop=True) \
                .to_dict(orient='index')

            if len(single_basic_ele_data):
                single_basic_ele_data = single_basic_ele_data[0]
                single_basic_ele_data.update({'date': quarter})
                result.append(single_basic_ele_data)
            else:
                print("函数get_single_stk_single_basic：debtpaying指标数据为空！季度为：" + quarter)

    elif basic_ele == "cashflow":

        table_name = 'cashflow' + quarter
        if is_table_exist(conn_cashflow,
                            stk_cashflow_data_db_name,
                            table_name):
            db_df = get_total_table_data(conn=conn_cashflow, table_name=table_name)
            single_basic_ele_data = db_df[db_df.code == codeParam] \
                .reset_index(drop=True) \
                .to_dict(orient='index')

            if len(single_basic_ele_data):
                single_basic_ele_data = single_basic_ele_data[0]
                single_basic_ele_data.update({'date': quarter})
                result.append(single_basic_ele_data)
            else:
                print("函数get_single_stk_single_basic：cashflow指标数据为空！季度为：" + quarter)

    else:
        print("函数get_single_stk_single_basic：不识别的basic指标  " + basic_ele)

    try:
        result = DataFrame(result).sort_values(by='date',ascending=True)
    except:
        result = DataFrame()
        print("函数get_single_stk_single_basic：遇到没有数据的指标！" + basic_ele)

    return result

def get_ss_sq_total_basic(codeParam, quarter):

    """
    ss:single stk
    sq:single quarter
    获取“单个stk”、“单个季度”的所有basic方面的信息
    :param codeParam:
    :return:
    """
    result = list()
    for basic_ele in ["profit","growth","operation","debtpaying","cashflow"]:
        single_df = get_ss_sb_sq(codeParam, basic_ele, quarter)

        if len(single_df):
            result.append(single_df.drop(["code","name"],axis=1).set_index("date"))

    if len(result):
        return pd.concat(result,axis=1,join='outer').reset_index().T.drop_duplicates().T
    else:
        return pd.DataFrame()

def get_ss_total_basic(codeParam):
    """

    :param codeParam:
    :return:
    """
    result = list()
    for basic_ele in ["profit","growth","operation","debtpaying","cashflow"]:
        single_df = get_ss_sb(codeParam, basic_ele)

        if len(single_df):
            result.append(single_df.drop(["code","name"],axis=1).set_index("date"))

    return pd.concat(result,axis=1,join='outer').reset_index().T.drop_duplicates().T

def add_quarter_to_df(k_df):

    """
    在K数据dataframe中添加“季度列”
    :param k_df:
    :return:
    """
    k_df["quarter"] = list(map(lambda x: cal_quarter(x), k_df.date))
    return k_df

def get_quarter_growth_ratio(data_df, quarter):

    """
    给定data_df和季度，求该季度的增长率（是不是应该求其与大盘增长率的比例？）
    :param data_df:
    :param quarter:
    :return:
    """

    # # 判断df中是否存在名为“index”的列，如果有，更名为“quarter”
    # if "index" in data_df.columns.values:
    #     data_df = data_df.rename(columns={'index':'quarter'})


    quarter_df = data_df[data_df.quarter == quarter].sort_values(by="date",ascending=True).reset_index(drop=True)

    if len(quarter_df):
        first_close = quarter_df.head(1)["close"].get_value(0)
        last_close = quarter_df.loc[len(quarter_df)-1,:].apply("close")

        inc_ratio = (last_close - first_close)/first_close

        return inc_ratio
    else:
        return None

def get_stk_quarter_start_price(data_df, quarter):

    """
    给定stkK数据和季度，求该季度的第一天的收盘价格
    :param data_df:
    :param quarter:
    :return:
    """

    # # 判断df中是否存在名为“index”的列，如果有，更名为“quarter”
    # if "index" in data_df.columns.values:
    #     data_df = data_df.rename(columns={'index':'quarter'})


    quarter_df = data_df[data_df.quarter == quarter].sort_values(by="date",ascending=True).reset_index(drop=True)

    if len(quarter_df):
        first_close = quarter_df.head(1)["close"].get_value(0)

        return first_close
    else:
        return None

def get_quarter_growth_ratio_df(data_df):

    """
    根据数据生成季度增长率的df

    df的列为： “quarter” 和　“quarter_ration”

    :param data_df:  该stk的K数据
    :return:
    """

    result = list()
    for year in range(2001, int(get_current_date_str().split('-')[0]) + 1):
        for quarter in range(1, 5):

            quarter_temp = str(year) + '0' + str(quarter)
            ratio = get_quarter_growth_ratio(data_df, quarter_temp)

            result.append({
                "quarter":quarter_temp,
                "quarter_ration":ratio
            })

    return pd.DataFrame(result).set_index(keys='quarter')

def get_quarter_start_price_df(data_df):

    """
    根据数据生成季度初始价格的df

    df的列为： “quarter” 和　“q_start_price”

    :param data_df:  该stk的K数据（包含季度列）
    :return:
    """

    result = list()
    for year in range(2001, int(get_current_date_str().split('-')[0]) + 1):
        for quarter in range(1, 5):

            quarter_temp = str(year) + '0' + str(quarter)
            ratio = get_stk_quarter_start_price(data_df, quarter_temp)

            result.append({
                "quarter":quarter_temp,
                "q_start_price":ratio
            })

    return pd.DataFrame(result).set_index(keys='quarter')

# 画盈利能力图
def plot_stk_profit(codeParam,data_df,title,save_dif):

    # singleProfit = get_single_stk_basic(codeParam)
    singleProfit = data_df.sort_values(by="date",ascending=True)


    # trick to get the axes
    fig, ax = plt.subplots(2,1)

    ax_0 = range(0,len(singleProfit['date']))

    # 用于归一化
    b_i_max = singleProfit['business_income'].max()
    b_i_min = singleProfit['business_income'].min()

    g_max = singleProfit['gross_profit_rate'].max()
    g_min = singleProfit['gross_profit_rate'].min()

    bi_max = singleProfit['bips'].max()
    bi_min = singleProfit['bips'].min()

    ep_max = singleProfit['eps'].max()
    ep_min = singleProfit['eps'].min()

    npr_max = singleProfit['net_profit_ratio'].max()
    npr_min = singleProfit['net_profit_ratio'].min()

    np_max = singleProfit['net_profits'].max()
    np_min = singleProfit['net_profits'].min()

    roe_max = singleProfit['roe'].max()
    roe_min = singleProfit['roe'].min()

    # plot data
    ax[0].plot(ax_0, (singleProfit['business_income']-b_i_min)/b_i_max, 'go--', label=U'营业收入',linewidth=0.2,markersize=3)
    ax[0].plot(ax_0, (singleProfit['gross_profit_rate']-g_min)/g_max, 'b*--', label=U'毛利率',linewidth=0.2,markersize=3)
    ax[0].plot(ax_0, (singleProfit['bips']-bi_min)/bi_max, 'cv--', label=U'每股主营业务收入',linewidth=0.2,markersize=3)
    ax[1].plot(ax_0, (singleProfit['eps']-ep_min)/ep_max, 'g*--', label=U'每股收益',linewidth=0.2,markersize=3)
    ax[1].plot(ax_0, (singleProfit['net_profit_ratio']-npr_min)/npr_max, 'k*--', label=U'净利率',linewidth=0.2,markersize=3)
    ax[1].plot(ax_0, (singleProfit['net_profits']-np_min)/np_max, 'r*--', label=U'净利润',linewidth=0.2,markersize=3)
    ax[1].plot(ax_0, (singleProfit['roe']-roe_min)/roe_max, 'y*--', label=U'净资产收益率',linewidth=0.2,markersize=3)

    ax[0].set_xticks(ax_0)
    ax[1].set_xticks(ax_0)

    xticklabels = list(singleProfit['date'])
    ax[0].set_xticklabels(xticklabels, rotation=90,fontsize=4)
    ax[1].set_xticklabels(xticklabels, rotation=90, fontsize=4)

    ax[0].set_title('profit' + codeParam+title)
    ax[0].legend(loc='best')
    ax[1].legend(loc='best')


    # plot close，可通用
    # k_df = get_total_table_data(conn_k,"k"+codeParam).sort_values(by="date",ascending=True)
    #
    # x_axes = range(0,len(k_df["date"]))
    # ax[2].plot(x_axes, k_df['close'], 'go--', label=U'price',linewidth=0.5,markersize=1)
    #
    # tick1 = range(0, k_df['date'].size, 30)
    # ticklabels_1 = [k_df['date'][n] for n in tick1]
    #
    # ax[2].set_xticks(tick1)
    # ax[2].set_xticklabels(ticklabels_1, rotation=90,fontsize=4)

    plt.savefig(save_dif+title,dpi=1600)
    plt.close()

# 画增长能力图
def plot_stk_growth(codeParam,data_df,title,save_dir):

    singleGrowth = data_df.sort_values(by="date",ascending=True)

    # trick to get the axes
    fig, ax = plt.subplots(2,1)

    x_axes = range(0,len(singleGrowth['date']))

    # 用于归一化
    m_max = singleGrowth['mbrg'].max()
    m_min = singleGrowth['mbrg'].min()

    np_max = singleGrowth['nprg'].max()
    np_min = singleGrowth['nprg'].min()

    na_max = singleGrowth['nav'].max()
    na_min = singleGrowth['nav'].min()

    t_max = singleGrowth['targ'].max()
    t_min = singleGrowth['targ'].min()

    e_max = singleGrowth['epsg'].max()
    e_min = singleGrowth['epsg'].min()


    s_max = singleGrowth['seg'].max()
    s_min = singleGrowth['seg'].min()

    # plot data
    ax[0].plot(x_axes, (singleGrowth['mbrg']-m_min)/m_max, 'go--', label=U'主营业务收入增长率',linewidth=0.5,markersize=3)
    ax[0].plot(x_axes, (singleGrowth['nprg']-np_min)/np_max, 'b*--', label=U'净利润增长率',linewidth=0.5,markersize=3)
    ax[0].plot(x_axes, (singleGrowth['nav']-na_min)/na_max, 'cv--', label=U'净资产增长率',linewidth=0.5,markersize=3)
    ax[1].plot(x_axes, (singleGrowth['targ']-t_min)/t_max, 'g*--', label=U'总资产增长率',linewidth=0.5,markersize=3)
    ax[1].plot(x_axes, (singleGrowth['epsg']-e_min)/e_max, 'k*--', label=U'每股收益增长率',linewidth=0.5,markersize=3)
    ax[1].plot(x_axes, (singleGrowth['seg']-s_min)/s_max, 'r*--', label=U'股东权益增长率',linewidth=0.5,markersize=3)

    ax[0].set_xticks(x_axes)
    ax[1].set_xticks(x_axes)

    xticklabels = list(singleGrowth['date'])
    ax[0].set_xticklabels(xticklabels, rotation=90,fontsize=4)
    ax[0].set_title('growth' + codeParam + title)
    ax[0].legend(loc='best')

    ax[1].set_xticklabels(xticklabels, rotation=90, fontsize=4)
    ax[1].legend(loc='best')

    plt.savefig(save_dir+title,dpi=1600)
    plt.close()

#==================================== 以下用于获取板块相关的指数季度变化率 ===============================

# 获取上证、深证、创业板、中小板的季度变化率
def get_class_Q_ratio():

    """
    获取上证、深证、创业板、中小板的季度变化率
    :return:
    """
    basic_Q = []

    for b_ele in ['sh', 'sz', 'cyb', 'zxb']:

        # 从数据库获取上证数据
        df_b = get_total_table_data(conn_k, 'k' + b_ele)

        # 增加季度
        df_b_with_quarter = add_quarter_to_df(df_b)

        # 增加季度增长率
        df_b_Q = get_quarter_growth_ratio_df(df_b_with_quarter)

        basic_Q.append({'b_ele': b_ele,
                        'b_Q': df_b_Q})

    return basic_Q

def get_stk_belongto_info():

    """
    获取每支stk所属类别（上证、深证、创业板、中小板）
    :return:
    """

    code_belongto_info = []
    for code in g_total_stk_code:

        if str(code)[0:3] == '300':
            belongto = 'cyb'

        elif str(code)[0:3] == '002':
            belongto = 'zxb'

        elif str(code)[0] == '6':
            belongto = 'sh'

        elif str(code)[0] == '0':
            belongto = 'sz'
        else:
            print('遇到不知所属的stk代码，其代码为：' + str(code))
            belongto = ''

        code_belongto_info.append({'code': code,
                                   'belongto': belongto})

    return pd.DataFrame(code_belongto_info)

def get_stk_classified_Q_ratio(class_Q,code_belongto_info,code):

    """
    根据stk所在类，获取其季度增长率df

    :param basic_Q:                 stk四大类的季度变化率
    :param code_belongto_info:      stk所属类的信息
    :param code:                    stk代码
    :return:

    """

    # 获取该stk所属的类型
    stk_class_dic = code_belongto_info[code_belongto_info.code == code]
    if len(stk_class_dic):
        stk_class = stk_class_dic['belongto'].values[0]
    else:
        return np.nan

    # 获取这个类型的变化率
    class_quarter_list = list(filter(lambda x:x['b_ele']== stk_class,class_Q))

    if len(class_quarter_list):
        class_quarter_ratio = class_quarter_list[0]['b_Q']
    else:
        return np.nan


    return class_quarter_ratio

def minus_quarter_df(data_df):

    """
    对df中的季度减一.因为季报在该季度结束后发布，所以03季度的影响在04季度体现。

    df 中的季度为index

    :param data_df:
    :return:
    """

    for index in data_df.index:

        if not str(index)[5] == '1':
            data_df.loc[index,'Q_minus'] = str(index)[0:5] + str(int(str(index)[5])-1)
        else:
            data_df.loc[index, 'Q_minus'] = str(int(str(index)[0:4])-1) + '04'

    return data_df

def minus_quarter(quarter_str):

    """
    输入一个字符串形式的季度，将其减一，并返回字符串类型的结果
    :param quarter_str:
    :return:
    """

    if not quarter_str[5] == '1':
        return  quarter_str[0:5] + str(int(quarter_str[5]) - 1)
    else:
        return  str(int(quarter_str[0:4]) - 1) + '04'

def add_quarter(quarter_str):
    """
    输入一个字符串形式的季度，将其加一，并返回字符串类型的结果
    :param quarter_str:
    :return:
    """

    if not quarter_str[5] == '4':
        return quarter_str[0:5] + str(int(quarter_str[5]) + 1)
    else:
        return str(int(quarter_str[0:4]) + 1) + '01'

def get_class_stk_belong(code,belong_to_info):
    """
    给定stk代码，获取其所属证券类型
    :param code:
    :param belong_to_info:
    :return:
    """
    return belong_to_info[belong_to_info.code==code]['belongto'].values[0]




# --------------------测试------------------------

# code = '300508'
# quarter = '201702'
#
# result = get_stk_classified_Q_ratio(get_class_Q_ratio(),get_stk_belongto_info(),code,quarter)
# code_belongto_info = get_stk_belongto_info()
# class_Q = get_class_Q_ratio()
# result = get_stk_classified_Q_ratio(class_Q,code_belongto_info,'300508')
#
# end = 0



