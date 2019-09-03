# encoding = utf-8
import matplotlib
matplotlib.use('Agg')
from Config.AutoStkConfig import *
# from SDK.SDKHeader import *
import talib
import tushare as ts
from SDK.MyTimeOPT import DateStr2Sec
from SDK.MyTimeOPT import get_current_date_str
from pylab import *

# 无法显示汉字及负号
mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

"""
    三次样条拟合测试
"""


import matplotlib.pyplot as plt
import numpy as np


step = 6

sh_index = ts.get_k_data('cyb')

def genStkPic(stk_df, stk_code, root_save_dir):
    """
    函数功能：给定stk的df，已经确定stk当前处于拐点状态，需要将当前stk的信息打印成图片，便于人工判断！
    :param stk_df           从tushare下载下来的原生df
    :param root_save_dir    配置文件中定义的存储路径
    :return:
    """
    """
    规划一下都画哪些图
    1、该stk整体走势，包括60日均线、20日均线和收盘价
    2、stk近几天的MACD走势
    """

    """
    在原数据的基础上增加均线和MACD
    """
    # 按升序排序
    stk_df = stk_df.sort_values(by='date', ascending=True)

    stk_df['M20'] = stk_df['close'].rolling(window=20).mean()
    stk_df['M60'] = stk_df['close'].rolling(window=60).mean()
    stk_df['MACD'], stk_df['MACDsignal'], stk_df['MACDhist'] = talib.MACD(stk_df.close,
                                                                                fastperiod=12, slowperiod=26,
                                                                                signalperiod=9)

    fig, ax = plt.subplots(nrows=3, ncols=1)

    ax[0].plot(range(0, len(stk_df['date'])), stk_df['M20'], 'b--', label='20日均线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['M60'], 'r--', label='60日均线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['close'], 'g*--', label='收盘价', linewidth=0.5, markersize=1)

    ax[1].bar(range(0, len(stk_df['date'])), stk_df['MACD'], label='MACD')

    # 准备下标
    xticks = range(0, len(stk_df['date']), int(math.ceil(len(stk_df['date']) / 40)))
    xticklabels_all_list = list(stk_df['date'].sort_values(ascending=True))
    xticklabels_all = [xticklabels_all_list[n] for n in xticks]

    for ax_sig in ax[0:2]:
        ax_sig.set_xticks(xticks)
        ax_sig.set_xticklabels(xticklabels_all, rotation=90, fontsize=5)
        ax_sig.legend(loc='best', fontsize=5)

    # 画出最近几天的情况
    stk_df_current = stk_df.tail(plot_current_days_amount)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M20'], 'b--', label='20日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M60'], 'r--', label='60日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['close'], 'g*-', label='收盘价', linewidth=1, markersize=5)

    ax[2].set_xticks(list(range(0, len(stk_df_current['date']))))
    ax[2].set_xticklabels(list(stk_df_current['date']), rotation=90, fontsize=5)
    ax[2].legend(loc='best')

    # 保存图片
    current_date = get_current_date_str()
    save_dir = root_save_dir+current_date+'/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.tight_layout()
    plt.savefig(save_dir+str(stk_code)+'.png', dpi=1200)
    plt.close()

# 测试
# genStkPic(stk_df=sh_index, stk_code='cyb',root_save_dir=pic_save_dir_root)


def JudgeCornerPot(stk_df, stk_code):

    """
    函数功能：判断一支标的的拐点
    :return:

    确认是拐点：
        返回
                1、真标志位
                2、向指定路径打印图片
                3、误差
    非拐点：
        返回
                1、假标志位
                2、误差
    """
    sh_index = stk_df
    sh_index['date'] = sh_index.index

    # 按时间降序排序，方便计算macd
    sh_index = sh_index.sort_values(by='date', ascending=True)

    # 在原始df中增加macd信息
    sh_index['MACD'], sh_index['MACDsignal'], sh_index['MACDhist'] = talib.MACD(sh_index.close,
                                                                                fastperiod=12, slowperiod=26,
                                                                                signalperiod=9)

    sh_index = sh_index.dropna(how='any', axis=0).reset_index(drop=True)

    # 获取最后几个值
    sh_index_now = sh_index.tail(cubic_test_last_step)

    # 对MACD进行归一化，以便后面计算误差
    M_max = np.max(sh_index_now['MACD'])
    M_min = np.min(sh_index_now['MACD'])
    sh_index_now['MACD_Std'] = sh_index_now.apply(lambda x: (x['MACD']-M_min)/(M_max-M_min), axis=1)

    # 重置index
    sh_index_now = sh_index_now.reset_index()
    sh_index_now['x'] = sh_index_now.index

    # 对归一化后的MACD进行二次拟合
    c = np.polyfit(np.array(sh_index_now['x']), np.array(sh_index_now['MACD_Std']), 2)

    # 计算其拟合后曲线
    sh_index_now['MACD_Fit'] = sh_index_now.apply(lambda x: c[0]*x['x']**2+c[1]*x['x']+c[2], axis=1)

    # 计算拟合误差
    sh_index_now['MACD_Fit_Err'] = sh_index_now.apply(lambda x: x['MACD_Fit']-x['MACD_Std'], axis=1)

    # 计算误差
    err = np.mean(list(map(lambda x:x**2, sh_index_now['MACD_Fit_Err'])))

    a = c[0]
    b = c[1]
    bottom = -1 * (b / (2 * a))

    if step - 1.5 < bottom < step + 1.5:
        corner_flag = True
    else:
        corner_flag = False

    # 如果当前是拐点，则打印图片保存于指定位置
    if corner_flag:

        # 生成图片
        genStkPic(stk_df=stk_df, stk_code=stk_code,root_save_dir=pic_save_dir_root)

        # 返回字典信息
        return {
            "corner_flag": corner_flag,
            "err": err
        }
    else:
        return {
            "corner_flag": corner_flag,
            "err": err
        }


# 测试一下
result = JudgeCornerPot(stk_df=sh_index, stk_code='cyb')

for idx in sh_index.loc[step:, :].index:
    df_part = sh_index.loc[idx-step:idx, ['MACD', 'date']].reset_index(drop=True)

    # 使用2次曲线拟合判断拐点
    c = np.polyfit(np.array(df_part.index), np.array(df_part['MACD']), 2)
    a = c[0]
    b = c[1]
    bottom = -1*(b/(2*a))

    if step-1.5 < bottom < step + 1.5:
        sh_index.loc[idx, 'corner'] = True
    else:
        sh_index.loc[idx, 'corner'] = False


# 画图展示效果
# trick to get the axes
fig, ax = plt.subplots()

df_normal = sh_index[sh_index.corner==False]
x_normal_axis = list(map(lambda x: DateStr2Sec(x), df_normal['date']))
ax.plot(x_normal_axis, df_normal['MACD'],  'g*')

df_corner = sh_index[sh_index.corner==True]
x_corner_axis = list(map(lambda x: DateStr2Sec(x), df_corner['date']))
ax.plot(x_corner_axis, df_corner['MACD'],  'r*')

# plot data
plt.show()

end = 0
