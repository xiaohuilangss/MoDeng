# encoding = utf-8

from pylab import *

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


def plot_x_date(code_param, data_df_param, y_axis_info_param):

    ave_df_param = data_df_param.sort_values(by='date',ascending=True)

    # trick to get the axes
    fig, ax = plt.subplots()

    x_axis = range(0, len(ave_df_param['date']))
    for y_axis_info in y_axis_info_param:
        ax.plot(x_axis, ave_df_param[y_axis_info[0]], y_axis_info[1], label=y_axis_info[2])

    xticklabels = list(ave_df_param['date'])
    ax.set_xticklabels(xticklabels, rotation=90)
    ax.set_title('stk'+code_param)
    ax.legend(loc='best')
    plt.show()


def add_axis(ax, df_date_s, x_amount, fontsize=5, rotation=90):
    """
    将字符串列用作x轴标签
    :param ax:
    :param df_date_s:   sh_index['date']
    :param x_amount:    x轴最多40个label，多了太密
    :return:
    """
    xticks = list(range(0, len(df_date_s), int(math.ceil(len(df_date_s) / x_amount))))
    ax.set_xticks(xticks)

    xticklabels_all_list = [str(x).replace('-', '') for x in df_date_s]
    xticklabels_all = [xticklabels_all_list[n] for n in xticks]
    ax.set_xticklabels(xticklabels_all, rotation=rotation, fontsize=fontsize)

    return ax


def addXticklabel_list(ax, label_list, x_amount, fontsize=None, rotation=90):

    """
    将字符串列用作x轴标签,label为list格式
    :param ax:
    :param df_date_S:   sh_index['date']
    :param x_amount:    x轴最多40个label，多了太密
    :return:
    """
    xticks = range(0, len(label_list), int(math.ceil(len(label_list ) / x_amount)))
    xticklabels_all_list = label_list
    xticklabels_all = [xticklabels_all_list[n] for n in xticks]

    ax.set_xticks(xticks)
    if fontsize is not None:
        ax.set_xticklabels(xticklabels_all, rotation=rotation, fontsize=fontsize)
    else:
        ax.set_xticklabels(xticklabels_all, rotation=rotation)

    return ax

