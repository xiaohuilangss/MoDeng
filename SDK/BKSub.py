# encoding = utf-8
from Config.GlobalSetting import *
from SDK.SDKHeader import get_MACD

def save_bk_graph(bk_name,days,save_url):
    """
    将板块信息画图存储
    :param bk_name:
    :param days:
    :param save_url:
    :return:
    """

    sh_index = ts.get_hist_data(bk_name)
    sh_index['date'] = sh_index.index
    sh_index = sh_index.reset_index(drop=True)

    # plot_ave(bk,sh_index)

    yaxis_info = [
    ("close","go--",U"close"),
    ("ma5","k*--",U"5日均线"),
    ("ma10","ro--",U"10日均线"),
    ("ma20","b*--",U"20日均线")
    ]


    save_bk_fig(bk_name, sh_index,days, yaxis_info, save_url)


'''绘制以dataframe的date列为横轴，给定列为纵轴的图
y_axis_info范例：

“列名” “颜色线条属性”  “注释字符串”
[
("mean10","go--",U"10日均值"),
("mean20","k*--",U"20日均值"),
("mean10","ro--",U"10日均值"),
("mean20","b*--",U"20日均值"),
("mean10","yo--",U"10日均值"),
("mean20","m*--",U"20日均值")
]
'''
def save_bk_fig(bk_name, data_df_param, days,y_axis_info_param,save_url):


    ave_df_all = data_df_param.sort_values(by='date',ascending=False)

    ave_df = ave_df_all.head(days)

    ave_df = ave_df.sort_values(by='date',ascending=True)
    ave_df_all = data_df_param.sort_values(by='date', ascending=True)


    # trick to get the axes
    fig, ax = plt.subplots(nrows=2, ncols=2)

    # ----------------------------------- 画近期close价格趋势图 -----------------------------------------------
    x_axis = range(0,len(ave_df['date']))

    for y_axis_info in y_axis_info_param:
        ax[0,0].plot(x_axis, ave_df[y_axis_info[0]], y_axis_info[1], label=y_axis_info[2],linewidth=0.5,markersize=3)

    ax[0,0].set_xticks(x_axis)
    xticklabels = list(ave_df['date'])
    ax[0,0].set_xticklabels(xticklabels, rotation=90,fontsize=3)
    ax[0,0].set_title('stk' + bk_name)
    ax[0,0].legend(loc='best',fontsize='xx-small',ncol=3)


    # ---------------------------------- 画出交易量趋势图 ----------------------------------------------
    ax[0,1].plot(x_axis, ave_df["volume"], "go--", label="volume",linewidth=0.5,markersize=3)

    ax[0,1].set_xticks(x_axis)
    ax[0,1].set_xticklabels(xticklabels, rotation=90,fontsize=3)

    # ---------------------------------- 画出该板块的整个历史趋势图 ------------------------------------
    x_axis_all = range(0, len(ave_df_all['date']))
    ax[1, 1].plot(x_axis_all, ave_df_all["close"], "go--", label="close", linewidth=0.5, markersize=1)

    x_axis_span = range(0,len(ave_df_all['date']),10)
    ax[1,1].set_xticks(x_axis_span)
    xticklabels_all_list = list(ave_df_all['date'])
    xticklabels_all = [xticklabels_all_list[n] for n in x_axis_span]
    ax[1,1].set_xticklabels(xticklabels_all, rotation=90,fontsize=2)


    # ---------------------------------- 画日MACD线 -----------------------------------------------------
    df_MACD = get_MACD(ave_df)

    if len(df_MACD):

        # 从index中恢复date
        df_MACD = df_MACD.sort_values(by='date',ascending=True)

        xtick_MACD = range(0,len(df_MACD))

        ax[1,0].bar(xtick_MACD, df_MACD.MACD)
        ax[1,0].set_xticks(xtick_MACD)
        ax[1,0].set_xticklabels(df_MACD.date,rotation=90,fontsize=3)

        ax[1,0].set_title(U'MACD', fontsize=5)

    plt.savefig(save_url,dpi=1200)
    plt.close()
