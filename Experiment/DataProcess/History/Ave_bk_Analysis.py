# encoding=utf-8
from sdk.SDKHeader import *
from Config.GlobalSetting import *
bk = 'cyb'

def plot_ave(code_param,ave_df_param):
    ave_df_param = ave_df_param.sort_values(by='date',ascending=True)

    # trick to get the axes
    fig, ax = plt.subplots()

    # plot data
    # ax.plot(ave_df_param['date'], ave_df_param['close_now'], 'go--', label=U'价格')
    # ax.plot(ave_df_param['date'], ave_df_param['maxdiff'], 'k*--', label=U'与最大值差')
    # ax.plot(ave_df_param['date'], ave_df_param['mindiff'], 'r*--', label=U'与最小值差')
    # ax.plot(ave_df_param['date'], ave_df_param['meandiff'], 'b*--', label=U'与均值差')
    # ax.plot(ave_df_param['date'], ave_df_param['mean'], 'y*--', label=U'均值')

    ax.plot(ave_df_param['date'], ave_df_param['close'], 'go--', label=U'close')
    ax.plot(ave_df_param['date'], ave_df_param['ma5'], 'k*--', label=U'5日均值')
    ax.plot(ave_df_param['date'], ave_df_param['ma10'], 'r*--', label=U'10日均值')
    ax.plot(ave_df_param['date'], ave_df_param['ma20'], 'b*--', label=U'20日均值')
    # ax.plot(ave_df_param['date'], ave_df_param['mean180'], 'y*--', label=U'180日均值')


    # ax.plot(ave_df_param['date'], ave_df_param['close_now'], 'go--', label=U'close')
    # ax.plot(ave_df_param['date'], ave_df_param['30diff60'], 'k*--', label=U'30-60')
    # ax.plot(ave_df_param['date'], ave_df_param['60diff180'], 'r*--', label=U'60-180')


    xticklabels = list(ave_df_param['date'])
    ax.set_xticklabels(xticklabels, rotation=90)
    ax.set_title('Average-Analysis'+code_param)
    ax.legend(loc='best')
    plt.show()

sh_index = ts.get_hist_data(bk)
sh_index['date'] = sh_index.index
sh_index = sh_index.reset_index(drop=True)

# plot_ave(bk,sh_index)

yaxis_info = [
("close","go--",U"close"),
("ma5","k*--",U"5日均线"),
("ma10","ro--",U"10日均线"),
("ma20","b*--",U"20日均线")
]

plot_x_date(code_param=bk,data_df_param=sh_index,y_axis_info_param=yaxis_info)

end=0