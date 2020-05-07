#encoding = utf-8
from Config.GlobalSetting import conn_k,conn_basic,conn_industry,total_stk_info_table_name,plt
from sdk.DBOpt import *
import numpy as np



def get_ss_K_by_date_span(stk_code,date_start,date_end,outstanding):

    """
    获取某只stk指定时间段内的close数据

    :param industry_code_list:
    :param date:
    :return:

    {'code':300508,
    'data_df':df}

    """

    # 读取K数据，并根据起止时间对数据进行截取
    data_k = get_total_table_data(conn=conn_k,table_name='k'+stk_code)

    data_k_date_specified = data_k[(data_k.date>=date_start)&(data_k.date<=date_end)]\
                                .loc[:,['date','close']]\
                                .set_index(keys='date',drop=True)

    # 计算流通市值
    data_k_date_specified['nmc'+stk_code] = data_k_date_specified['close']*outstanding

    # 只取流通市值
    data_ncm_date = data_k_date_specified.loc[:,'nmc'+stk_code]

    return {'code':stk_code,
            'data_df':data_ncm_date}



def cal_industry_index(date_start,date_end):
    """
    计算指定时间内的行业指数

    :param date_start:
    :param date_end:
    :return:
    """

    # 获取行业分类信息
    industry_info = get_total_table_data(conn=conn_industry, table_name='industry_info')

    # 获取stk基本信息
    stk_basic = get_total_table_data(conn=conn_basic,table_name=total_stk_info_table_name)\
                    .loc[:,['code','outstanding','totals']]

    # 行业与基本数据合并
    industry_list = list(pd.merge(stk_basic, industry_info, on="code").groupby(by='c_name'))

    # 最终结果（行业/日期-指数）
    ids_list = []

    # 遍历行业：
    for ids in industry_list:

        # 获取行业名字
        c_name = ids[0]

        # 获取行业代码列表及相应的流通股本
        code_info_df = ids[1].loc[:,['code','outstanding']].reset_index(drop=True)

        # 获取该行业各只stk的流通市值，得到list列表形式
        c_date_list = []
        for stk_index in code_info_df.index:

            stk_code = code_info_df.loc[stk_index,'code']
            stk_outstanding = code_info_df.loc[stk_index,'outstanding']

            data_ss = get_ss_K_by_date_span(stk_code,date_start,date_end,stk_outstanding)['data_df']

            c_date_list.append(data_ss)

        # 按照日期合并同一行业内各只stk的数据
        c_date_df = pd.concat(c_date_list,axis=1)

        # 对df中的空值进行处理
        if len(c_date_df.loc[:,c_date_df.isnull().any()==True].columns):

            print('行业：'+c_name+' 数据中存在空值，调用空值处理函数进行处理！')
            c_date_df = nan_pro(c_date_df,date_start,stk_basic)


        # 按日期求取行业指数
        c_date_df['industry_index'] = c_date_df.apply(lambda x:x.sum(),axis=1)

        # 若没有行业数据，则打印信息
        if len(c_date_df) == 0:
            print('行业：' + c_name + ' 没有相应数据！')

        ids_list.append({'c_name':c_name,
                        'c_data':c_date_df})

        print('行业：' + c_name + ' 数据处理完成！')

    return ids_list



def nan_pro(input_df,date_start,stk_basic):


    """

    函数功能：处理指定行业中数据的nan值


    输入数据类型：

                nmc601333  nmc000996  nmc002492  nmc600751  nmc600004  nmc601919
    2017-09-12   301.2516    54.7860    34.5940   121.6107   280.3495   615.4616
    2017-09-13   297.2952    55.4070    34.2410   123.1875   280.3495   610.1164
    2017-09-14   305.2080    54.0615    34.0645   122.7933   277.6598   597.1352
    2017-09-15   302.9472    54.3720    33.4997   121.6107   275.1770   579.5724
    2017-09-18   295.5996    54.6135    33.2526   122.2020   277.0391   582.6268

    :param input_df:
    :param date_start:
    :param stk_basic:
    :return:
    """


    # 获取有空值的stk代码列表（列名），分为 “任何有nan的列” 和 “全部为nan的列”
    nan_any_df = input_df.loc[:,input_df.isnull().any()==True]
    code_any_list = list(map(lambda x:x.replace('nmc',''),nan_any_df.columns))


    # 分两种情况讨论，全部为nan的和部分为nan的
    # 按时间升序排序
    df_sorted = input_df.sort_index(ascending=True)


    # 遍历有空值的stk代码
    for code in code_any_list:

        # 获取第一个空值的索引号
        first_nan_index = np.where(np.isnan(df_sorted['nmc'+code]))[0][0]

        # （一）如果该列的第一值就是空值，则从K数据中找出时间上最近的数据进行填充，如果不是第一个，则取前一个值进行填充
        if first_nan_index == 0:

            # 从K数据中找出时间上最近的close数据
            k_data = get_total_table_data(conn=conn_k,table_name='k'+code)

            # 找出距离“起始时间”最近的数据，先往前找，再往后找。
            nearly_df = k_data[k_data.date<=date_start]

            if(len(nearly_df) == 0):
                nearly_close = k_data[k_data.date>=date_start]\
                                .sort_values(by='date', ascending=True)\
                                .head(1)['close'].values[0]
            else:
                nearly_close = nearly_df\
                            .sort_values(by='date',ascending=False)\
                            .head(1)['close'].values[0]

            # 从stk基本信息中获取流通股数量
            outstanding = stk_basic[stk_basic.code==code]['outstanding'].values[0]

            # 计算起始市值
            nmc_start = nearly_close*outstanding

            # 遍历该列，对nan值进行补充
            for indexs in df_sorted.index:

                if np.isnan(df_sorted.loc[indexs,'nmc'+code]):
                    df_sorted.loc[indexs, 'nmc' + code] = nmc_start
                else:
                    nmc_start=df_sorted.loc[indexs,'nmc'+code]


        #（二）如果该列的第一个非空值，则遍历该列的每一个值，进行空值弥补
        else:
            nmc_start = df_sorted.head(1)['nmc'+code].values[0]

            # 遍历该列，对nan值进行补充
            for indexs in df_sorted.index:

                if np.isnan(df_sorted.loc[indexs, 'nmc' + code]):
                    df_sorted.loc[indexs, 'nmc' + code] = nmc_start
                else:
                    nmc_start = df_sorted.loc[indexs, 'nmc' + code]

    return df_sorted

# def get_stk_industry(code,industry_info):


def ids_gen_figure(c_name, data_df_param,save_url):

    """
    生成行业趋势图

    :param c_name:
    :param data_df_param:
    :param save_url:
    :return:
    """

    ave_df_param = data_df_param

    # trick to get the axes
    fig, ax = plt.subplots()

    x_axis = range(0,len(ave_df_param.index))

    ax.plot(x_axis, ave_df_param['industry_index'], 'go--',linewidth=0.5,markersize=3)

    ax.set_xticks(x_axis)
    xticklabels = list(map(lambda x:str(x),ave_df_param.index))
    ax.set_xticklabels(xticklabels, rotation=90,fontsize=4)
    ax.set_title(c_name)
    ax.legend(loc='best')
    plt.savefig(save_url+c_name,dpi=1000)
    # plt.show()
    plt.close()






# ------------------- 以下代码用于测试 -----------------------

# result = cal_industry_index('2017-09-12','2017-10-18')

