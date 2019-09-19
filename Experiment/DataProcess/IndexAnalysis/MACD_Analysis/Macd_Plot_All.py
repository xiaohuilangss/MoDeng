# encoding = utf-8

from SDK.SDKHeader import *
import talib
# ----------------------- 定义子函数 --------------------------------------


def plot_MACD(days,code,title,save_dir):

    df_all = get_total_table_data(conn_k,'k' + code)

    df_all_head = df_all.sort_values(by='date',ascending=False).head(days).sort_values(by='date',ascending=True).reset_index()

    latest_date_in_table = df_all_head.sort_values(by='date',ascending=False).head(1)['date'].values[0]

    # 判断表中最近的日期与当前日期的相差几天，超过2天的不要!
    if minus_date_str(get_current_date_str(), latest_date_in_table) <= 2:

        df_MACD = get_MACD(df_all_head)

        fig,ax = plt.subplots()

        if len(df_MACD):

            xtick_MACD = range(0, len(df_MACD))

            ax.bar(xtick_MACD, df_MACD.MACD)
            ax.set_xticks(xtick_MACD)
            ax.set_xticklabels(df_MACD.date, rotation=90, fontsize=5)
            ax.set_title(code+'-'+title)

        plt.savefig((save_dir+code+title).replace('*',''),dpi=600)
        plt.close('all')


def get_MACD_trend(code,days):

    """
    计算一直stk的MACD的发展趋势
    :param code:
    :param days:
    :return:
    """

    df_all = get_total_table_data(conn_k,'k' + code)
    df_all_head = df_all.sort_values(by='date',ascending=False).head(days*6).sort_values(by='date',ascending=True).reset_index(drop=True)

    latest_date_in_table = df_all_head.sort_values(by='date',ascending=False).head(1)['date'].values[0]

    # 判断表中最近的日期与当前日期的相差几天，超过2天的不要!
    if minus_date_str(get_current_date_str(), latest_date_in_table) <= 2:

        # 计算MACD
        df_all_MACD = get_MACD(df_all_head)

        # 计算趋势
        df_all_MACD['MACD_s1'] = df_all_MACD.MACD.shift(1)
        df_all_MACD['MACD_s1_diff_ratio'] = df_all_MACD.apply(lambda x: (x['MACD'] - x['MACD_s1']) / (x['MACD'] + 0.0000000000001), axis=1)

        # 取最近的趋势均值
        tr = df_all_MACD.sort_values(by='date',ascending=False).head(days).MACD_s1_diff_ratio.mean()

        print('成功完成' + code + '!')
        return {'code':code,'trend':tr}

    else:
        print('完成' + code + '；其可能已经停牌!')
        return {}




# ----------------------- 打印MACD图 --------------------------------------

days_plot = 60
days_filter = 14

save_dir = "F:/MYAI/文档资料/用于读取的文件/"+'MACD' + str(days_filter) + '筛选后'+get_current_date_str()+'/'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# # 遍历所有代码，基于MACD求趋势值
# trend_list = []
# for code in g_total_stk_code:
#     trend_info = get_MACD_trend(code, days_filter)
#     if len(trend_info):
#         trend_list.append(trend_info)


# 遍历所有代码，求RSI值
trend_list = []
for code in g_total_stk_code:

    # 获取该code的数据
    df = get_total_table_data(conn_k,'k'+code)

    # 时间升序后取plot个数据
    df_near = df.sort_values(by='date',ascending=False).head(days_plot).sort_values(by='date',ascending='True')

    # 计算RSI值
    df_near['RSI12'] = talib.RSI(df_near.close, timeperiod=12)

    rsi = df_near.sort_values(by='date',ascending=False).head(1)['RSI12'].values[0]

    trend_list.append({'code':code,'trend':rsi})
    print('完成'+code+'RSI的计算！')

trend_df = pd.DataFrame(trend_list).sort_values(by='trend', ascending=True).head(400)

# 将最小的指定数量的code打印出图
for code in trend_df.code:
    name = g_total_stk_info_mysql[g_total_stk_info_mysql.code == code]['name'].values[0]
    plot_MACD(days_plot, code, name, save_dir)

