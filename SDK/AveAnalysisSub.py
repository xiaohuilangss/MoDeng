# encoding = utf-8
import gc

from Config.GlobalSetting import *
from SDK.MyTimeOPT import *
from SDK.BasicAnalysisSub import get_ss_sb
import os
from SDK.MACD_Sub import *

from SDK.RelativeChangeStrategySub import get_stk_classified_data, stk_k_pro
import talib


def get_average_index(k_df_param,date_param, time_span_param,field_param):

    """
    获取dataframe中一个时间段内的最大值、最小值、平均值

    :param k_df_param:
    :param date_param:
    :param time_span_param:
    :param field_param:
    :return:
    """

    k_df = k_df_param

    # 为了节省排序时间，先将最近十天的时间取出，然后按时间排序，取最近的数据
    latest_span= k_df[(k_df.date>add_date_str(date_param,-10))&(k_df.date<=date_param)]\
                        .sort_values(by='date', ascending=False).head(1)
    if len(latest_span):
        master_field = latest_span.reset_index(drop=True).to_dict(orient='index')[0][field_param]
    else:
        print("函数get_average_index： 在日期"+date_param + "计算"+field_param+"值时出错！")
        return {}

    # 取“主角日期”与该日期之前“time_span_param”长度的数据的field_param的均值
    span_df = k_df[(k_df.date>add_date_str(date_param, -1*time_span_param))&(k_df.date<date_param)]

    span_max = span_df[field_param].max()
    span_min = span_df[field_param].min()
    span_mean = span_df[field_param].mean()

    return {"date":date_param,
            field_param:master_field,
            field_param+"_max"+str(time_span_param):span_max,
            field_param+"_min"+str(time_span_param):span_min,
            field_param+"_mean"+str(time_span_param):span_mean}


def get_single_average(k_df_param,time_span,field_param):

    """
    给定stk的df数据和timespan，出dataframe
    :param k_df_param:
    :param time_span:
    :param field_param:
    :return:
    """

    result =  list(map(lambda x:get_average_index(k_df_param=k_df_param,date_param=x,time_span_param=time_span,field_param=field_param),k_df_param.date))
    return DataFrame(list(filter(lambda x:len(x) != 0,result))).set_index("date")


def get_average_array_span(df_param,array_span_param,field_param):

    """
    给定dataframe，一个list形式的timespan，输出一个dataframe
    :param df_param:
    :param array_span_param:
    :param field_param:
    :return:
    """

    df_array = list(map(lambda x:get_single_average(k_df_param=df_param,time_span=x,field_param=field_param),array_span_param))
    df_array.append(df_param.loc[:,['date','volume']].set_index(keys='date'))
    return pd.concat(df_array, axis=1)


def add_inc(total_df_param, field_param, days_span_param):

    """
    求取mean30字段未来设定时间的增长率
    :param total_df_param:
    :param field_param:
    :param days_span_param:
    :return:
    """

    df_mean30 = total_df_param.loc[:, ["date", field_param]]
    total_sub = total_df_param.head(len(df_mean30) - days_span_param)
    df_mean30_sub = df_mean30.head(len(df_mean30) - days_span_param)

    # list(map(lambda x:df_mean30.loc[x+5],df_mean30.index))

    df_mean30_sub[field_param + '_future' + str(days_span_param)] = DataFrame(list(map(lambda x: df_mean30.loc[x + days_span_param, field_param], df_mean30_sub.index)))
    # if len(df_m_time_move):
    #     df_mean30_sub[field_param + '_future' + str(days_span_param)] = df_m_time_move
    # else:
    #     df_mean30_sub[field_param + '_future' + str(days_span_param)] = pd.DataFrame.empty

    df_mean30_sub.loc[:,field_param+"_inc_ratio"] = (df_mean30_sub[field_param+'_future' + str(days_span_param)] - df_mean30_sub[field_param]) * 1.0 / df_mean30_sub[field_param]
    # df_mean30_sub["m30inc_ratio"] = (df_mean30_sub.loc[:,"mean30index"+str(days_span_param)] - df_mean30_sub.loc[:,"mean30"])*1.0/df_mean30_sub.loc[:,"mean30"]

    df_mean30_sub = df_mean30_sub.drop(field_param,axis=1)

    return pd.merge(total_sub,df_mean30_sub,on="date")


def get_total_ave_ss(code_param, inc_time_span_param):

    """
    根据k数据整理衍生相应指标（均线，作为label的未来inc），并整理为列，存入csv中。
    :param code_param:
    :param inc_time_span_param:
    :return:
    """

    # 获取stk的k数据
    k_df = get_total_table_data(conn_k, 'k' + code_param)

    # 获取均线
    ave_origin = get_average_array_span(k_df, [7, 14, 30, 60, 180], 'close').reset_index()

    # 列去重
    ave_columns_duplicates = ave_origin.loc[:,~ave_origin.columns.duplicated()]

    # 添加m30inc,前提是前瞻时间天数超过了数据的天数
    if len(ave_origin) > inc_time_span_param:
        ave_with_m30inc = add_inc(ave_columns_duplicates, 'close_mean30', inc_time_span_param)

        return ave_with_m30inc
    else:
        return pd.DataFrame()


# --------------------------------- 以下为均线趋势判断中画图相关子函数 -------------------------------------
def get_stk_relative_ratio_change(code,k_df,index_list):

    """
    本函数主要在绘制个股信息全图时使用，用以计算个股单日变动率与大盘变动率之差
    :param code: 个股代码
    :param k_df: 个股k数据
    :param index_list: 大盘数据列表
    :return:
    """

    # 处理
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


def plot_ave(code_param,ave_df_param,df_all,today_all,save_dir,days,ax_out,title_note,index_list):

    """
    给定某只stk一部分数据，画出其均线图并保存到路径中
    :param code_param:
    :param ave_df_param:
    :param df_all:
    :param today_all:
    :param save_dir:
    :param days:
    :param ax:
    :param title_note:
    :param index_list:
    :return:
    """

    # # 定义线的粗细和mark的大小
    # line = 1
    # marksize = 1

    # fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(13.6, 7.68))
    ax = ax_out

    # 按时间升序对df进行排序
    ave_df_param = ave_df_param.sort_values(by="date",ascending=True).loc[:,~ave_df_param.columns.duplicated()]
    df_all_head = df_all.sort_values(by='date',ascending=False).head(days).sort_values(by='date',ascending=True).reset_index()


    # ------------------- 画“均值图” ------------------------
    x_axis = range(0,len(ave_df_param['date']))
    ax[0,0].cla()
    ax[0,0].plot(x_axis, ave_df_param['close'], 'go--', label=U'close', linewidth=0.5,markersize=1)
    ax[0,0].plot(x_axis, ave_df_param['close_mean7'], 'm*--', label=U'7日均值', linewidth=0.5,markersize=1)
    ax[0,0].plot(x_axis, ave_df_param['close_mean14'], 'k*--', label=U'14日均值',linewidth=0.5,markersize=1)
    ax[0,0].plot(x_axis, ave_df_param['close_mean30'], 'r*--', label=U'30日均值',linewidth=0.5,markersize=1)
    try:
        ax[0,0].plot(x_axis, ave_df_param['close_mean60'], 'b*--', label=U'60日均值',linewidth=0.5,markersize=1)
    except:
        print("画60日均线时出错！")
    try:
        ax[0,0].plot(x_axis, ave_df_param['close_mean180'], 'y*--', label=U'180日均值',linewidth=0.5,markersize=1)
    except:
        print("画180日均线时出错！")


    ax[0,0].set_xticks(x_axis)
    xticklabels = list(ave_df_param['date'].sort_values(ascending=True))
    ax[0,0].set_xticklabels(xticklabels, rotation=90,fontsize=3)
    ax[0,0].set_title(title_note)
    ax[0,0].legend(loc='best',fontsize='xx-small',ncol=3)
    ax[0,0].legend(loc='best', fontsize='xx-small', ncol=3)


    # ------------------- 画交易量变化趋势 ------------------------
    ax[2,1].cla()
    ax[2,1].plot(x_axis,ave_df_param['volume'], 'go--', label=U'volume', linewidth=0.5,markersize=3)

    ax[2,1].set_xticks(x_axis)
    ax[2,1].set_xticklabels(xticklabels, rotation=90,fontsize=3)
    ax[2,1].legend(loc='best', fontsize='xx-small', ncol=3)
    ax[2,1].set_title(code_param + U"交易量")


    # ------------------- 个股从上市以来的整体走势图 ----------------------------------
    df_all = df_all.sort_values(by='date',ascending=True)
    x_axis_all = range(0,len(df_all['date']))
    ax[0,1].cla()
    ax[0,1].plot(x_axis_all,df_all['close'], 'go--', label=U'close', linewidth=0.5,markersize=0.2)

    xticks = range(0,len(df_all['date']),10)
    ax[0,1].set_xticks(xticks)
    xticklabels_all_list = list(df_all['date'].sort_values(ascending=True))
    xticklabels_all = [xticklabels_all_list[n] for n in xticks]
    ax[0,1].set_xticklabels(xticklabels_all, rotation=90,fontsize=3)
    ax[0,1].set_title(code_param + U"全部历史走势")
    ax[0,1].legend(loc='best', fontsize='xx-small', ncol=3)
    ax[0,1].legend(loc='best', fontsize='xx-small', ncol=3)

    # --------------------- 画“市盈率、市净率”图-------------------------

    pe = today_all[today_all.code == code_param]['per'].values[0]
    pb = today_all[today_all.code == code_param]['pb'].values[0]
    ax[1,1].cla()
    ax[1,1].text(0.2,0.2,'市盈率：' +str(pe))
    ax[1,1].text(0.2,0.4,'市净率：' +str(pb))

    # --------------------- 画“成长能力”趋势图-------------------------
    growth = get_ss_sb(code_param,"growth")

    singleGrowth = growth.sort_values(by="date",ascending=True)

    x_axes_growth = range(0,len(singleGrowth['date']))

    # 用于归一化
    m_max = singleGrowth['mbrg'].max()
    m_min = singleGrowth['mbrg'].min()

    np_max = singleGrowth['nprg'].max()
    np_min = singleGrowth['nprg'].min()

    na_max = singleGrowth['nav'].max()
    na_min = singleGrowth['nav'].min()

    e_max = singleGrowth['epsg'].max()
    e_min = singleGrowth['epsg'].min()

    ax[2,0].cla()
    ax[2,0].plot(x_axes_growth, (singleGrowth['mbrg']-m_min)/m_max, 'go--', label=U'主营业务收入增长率',linewidth=0.5,markersize=3)
    ax[2,0].plot(x_axes_growth, (singleGrowth['nprg']-np_min)/np_max, 'y*--', label=U'净利润增长率',linewidth=0.5,markersize=3)
    ax[2,0].plot(x_axes_growth, (singleGrowth['nav']-na_min)/na_max, 'rv--', label=U'净资产增长率',linewidth=0.5,markersize=3)
    ax[2,0].plot(x_axes_growth, (singleGrowth['epsg']-e_min)/e_max, 'b*--', label=U'每股收益增长率',linewidth=0.5,markersize=3)

    ax[2,0].set_xticks(x_axes_growth)

    xticklabels = list(singleGrowth['date'])
    ax[2,0].set_xticklabels(xticklabels, rotation=90,fontsize=4)
    ax[2,0].set_title('growth' + code_param,fontsize=2)
    ax[2,0].legend(loc='best', fontsize='xx-small', ncol=3)



    # ----------------------- 画MACD指标 ----------------------

    ax[1, 0].cla()
    df_macd = get_MACD(df_all_head)

    if len(df_macd):

        # 从index中恢复date
        df_macd = df_macd.sort_values(by='date',ascending=True)

        xtick_macd = range(0,len(df_macd))

        ax[1,0].bar(xtick_macd,df_macd.macd)
        ax[1,0].set_xticks(xtick_macd)
        ax[1,0].set_xticklabels(df_macd.date,rotation=45,fontsize=1)

        ax[1,0].set_title(U'MACD', fontsize=5)

        del xtick_macd

    # ----------------------- 画RSI指标 --------------------------------------
    ax[0,2].cla()
    df_rsi = df_all_head
    df_rsi['RSI5'] = talib.RSI(df_rsi.close, timeperiod=5)
    df_rsi['RSI12'] = talib.RSI(df_rsi.close, timeperiod=12)
    df_rsi['RSI30'] = talib.RSI(df_rsi.close, timeperiod=30)

    xtick_rsi = range(0, len(df_rsi))

    ax[0,2].plot(xtick_rsi, df_rsi.RSI5, 'go--', label=U'RSI5',linewidth=0.5,markersize=1)
    ax[0,2].plot(xtick_rsi, df_rsi.RSI12, 'ro--', label=U'RSI12', linewidth=0.5, markersize=1)
    ax[0,2].plot(xtick_rsi, df_rsi.RSI30, 'yo--', label=U'RSI30', linewidth=0.5, markersize=1)

    ax[0,2].set_xticks(xtick_rsi)
    ax[0,2].set_xticklabels(df_rsi.date, rotation=90, fontsize=1)

    ax[0,2].set_title(U'RSI', fontsize=5)
    ax[0,2].legend(loc='best', fontsize='xx-small', ncol=3)


    # ----------------------- 画KDJ指标 --------------------------------------
    ax[1,2].cla()
    df_kdj = df_all_head
    df_kdj['slowk'], df_kdj['slowd'] = talib.STOCH(df_kdj.high,
                                                   df_kdj.low,
                                                    df_kdj.close,
                                                    fastk_period=9,
                                                    slowk_period=3,
                                                    slowk_matype=0,
                                                    slowd_period=3,
                                                    slowd_matype=0)

    x = range(0,len(df_kdj.close))

    ax[1,2].plot(x,df_kdj.slowk,'r*-',label='slowk',linewidth=0.5,markersize=1)
    ax[1,2].plot(x,df_kdj.slowd,'y*-',label='slowd',linewidth=0.5,markersize=1)

    ax[1, 2].set_xticks(x)
    ax[1, 2].set_xticklabels(df_kdj.date, rotation=90, fontsize=1)
    ax[1, 2].set_title(U'KDJ', fontsize=5)
    ax[1, 2].legend(loc='best', fontsize='xx-small', ncol=3)


    # ----------------------- 画布林线 --------------------------------------
    ax[2,2].cla()
    df_bbands = df_all_head
    upper, middle, lower = talib.BBANDS(
        df_bbands.close,
        timeperiod=20,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0)

    x = range(0,len(df_bbands.close))

    ax[2,2].plot(x,upper,'b*--',label='upper',linewidth=0.5,markersize=1)
    ax[2,2].plot(x,middle,'r*-',label='middle',linewidth=0.5,markersize=1)
    ax[2,2].plot(x,lower,'y*-',label='lower',linewidth=0.5,markersize=1)

    ax[2, 2].set_xticks(x)
    ax[2, 2].set_xticklabels(df_bbands.date, rotation=90, fontsize=1)
    ax[2, 2].set_title(U'布林线', fontsize=5)
    ax[2, 2].legend(loc='best', fontsize='xx-small', ncol=3)



    # ----------------------- 生成图并保存 --------------------------------------
    plt.savefig((save_dir+title_note).replace('*',''),dpi=1200)

    del ave_df_param,\
        df_all_head,\
        df_macd,\
        df_all,\
        growth,\
        singleGrowth,\
        ax,x_axis,x_axis_all,xticklabels,xticklabels_all_list,xticklabels_all,pe,pb,xticks

    gc.collect()



def std_code(code):

    """
    csv文件中，stk的code如果前面是0会被省略，所以需要使用函数进行增加

    :param code:
    :return:
    """
    code_temp = str(code)
    if len(code_temp) < 6:
        diff = 6-len(code_temp)

        for index in range(0,diff):
            code_temp = '0' + code_temp

    return code_temp


def plot_part_ave(length,stk_code,today_all,save_dir,ax,title_note,index_list):

    k_df = get_total_table_data(conn_k, 'k' + stk_code)

    data_part_df = k_df.sort_values(by='date',ascending=False).head(240).sort_values(by='date',ascending=True)

    # df_total = get_average_array_span(data_part_df, [7, 14, 30, 60, 180], 'close')\
    #             .reset_index()\
    #             .sort_values(by='date', ascending=False).head(length)

    data_part_df['close_mean7'] = talib.MA(data_part_df.close, timeperiod=7)
    data_part_df['close_mean14'] = talib.MA(data_part_df.close, timeperiod=14)
    data_part_df['close_mean30'] = talib.MA(data_part_df.close, timeperiod=30)
    data_part_df['close_mean60'] = talib.MA(data_part_df.close, timeperiod=60)
    data_part_df['close_mean180'] = talib.MA(data_part_df.close, timeperiod=180)

    data_part_df = data_part_df.sort_values(by='date', ascending=False).head(length).sort_values(by='date',ascending=True)

    plot_ave(code_param=stk_code,
             ave_df_param=data_part_df,
             df_all=k_df,
             today_all=today_all,
             save_dir=save_dir,
             days=length,
             ax_out=ax,
             title_note=title_note,
             index_list=index_list)

    del k_df,data_part_df
    gc.collect()


def plot_high_level(trend_df,time_span,save_dir):

    save_dir_span = save_dir + str(time_span) + '/'

    if not os.path.exists(save_dir_span):
        os.makedirs(save_dir_span)

    code_list = trend_df.sort_values(by='cov_60', ascending=True).head(50)['code']

    for code in code_list:
        plot_part_ave(60, std_code(code), save_dir_span, 'ave'+str(time_span))

        print("函数plot_high_level：完成" + std_code(code) + "的均线趋势图！")

