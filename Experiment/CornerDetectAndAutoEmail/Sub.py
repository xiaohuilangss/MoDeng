# encoding = utf-8
from email.mime.image import MIMEImage


from Config.AutoStkConfig import *
import talib
from talib import MA_Type

import tushare as ts
from SDK.DataPro import normalize
from SDK.MyTimeOPT import DateStr2Sec
from SDK.MyTimeOPT import get_current_date_str
from pylab import *
import pandas as pd


# 无法显示汉字及负号
from SDK.PlotOptSub import addXticklabel, addXticklabel_list

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False


def genMIMEImageList(pic_dir_list):

    """
    在使用邮箱发送消息时，对在html中使用的图片，需要在msg中加载，本函数根据图片的路径依次将其添加
    :param pic_dir_list:
    :return:
    """
    msgImage_list = []

    for dir in pic_dir_list:

        # 测试添加png类型的图片
        fp_ave = open(dir, 'rb')
        msgImage_ave = MIMEImage(fp_ave.read())
        msgImage_ave.add_header('Content-ID', '<' + dir.replace('.png', '').replace(pic_save_dir_root, '') + '>')
        msgImage_list.append(msgImage_ave)
        fp_ave.close()

    return msgImage_list


def genStkPicForQQ(stk_df, stk_code=''):
    """
    函数功能：给定stk的df，已经确定stk当前处于拐点状态，需要将当前stk的信息打印成图片，便于人工判断！
    :param stk_df           从tushare下载下来的原生df
    :param root_save_dir    配置文件中定义的存储路径
    :return:                返回生成图片的路径
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

    fig, ax = plt.subplots(nrows=4, ncols=1)

    ax[0].plot(range(0, len(stk_df['date'])), stk_df['M20'], 'b--', label='20日均线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['M60'], 'r--', label='60日均线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['close'], 'g*--', label='收盘价', linewidth=0.5, markersize=1)

    ax[1].bar(range(0, len(stk_df['date'])), stk_df['MACD'], label='MACD')

    # 准备下标
    xticklabels_all_list = list(stk_df['date'].sort_values(ascending=True))
    xticklabels_all_list = [x.replace('-', '')[2:] for x in xticklabels_all_list]

    for ax_sig in ax[0:2]:
        ax_sig = addXticklabel_list(ax_sig, xticklabels_all_list, 30, rotation=45)
        ax_sig.legend(loc='best', fontsize=5)

    # 画出最近几天的情况（均线以及MACD）
    stk_df_current = stk_df.tail(plot_current_days_amount)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M20'], 'b--', label='20日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M60'], 'r--', label='60日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['close'], 'g*-', label='收盘价', linewidth=1, markersize=5)
    ax[3].bar(range(0, len(stk_df_current['date'])), stk_df_current['MACD'], label='MACD')

    # 准备下标
    xticklabels_all_list = list(stk_df_current['date'].sort_values(ascending=True))
    xticklabels_all_list = [x.replace('-', '')[2:] for x in xticklabels_all_list]

    for ax_sig in ax[2:4]:
        ax_sig = addXticklabel_list(ax_sig, xticklabels_all_list, 30, rotation=45)
        ax_sig.legend(loc='best', fontsize=5)

    fig.tight_layout()                          # 调整整体空白
    plt.subplots_adjust(wspace=0, hspace=1)     # 调整子图间距

    # 检查日级别的MACD是否有异常
    attention = False
    MACD_list = stk_df_current.tail(3)['MACD'].values

    if MACD_list[1] == np.min(MACD_list):
        plt.title(stk_code + '日级别 MACD 见底了！')
        attention = True
    elif MACD_list[1] == np.max(MACD_list):
        plt.title(stk_code + '日级别 MACD 到顶了！')
        attention = True

    return fig, ax, attention


def genStkPic(stk_df, stk_code, current_date, root_save_dir, pic_name='stk_A_C_M.png'):
    """
    函数功能：给定stk的df，已经确定stk当前处于拐点状态，需要将当前stk的信息打印成图片，便于人工判断！
    :param stk_df           从tushare下载下来的原生df
    :param root_save_dir    配置文件中定义的存储路径
    :return:                返回生成图片的路径
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

    fig, ax = plt.subplots(nrows=4, ncols=1)

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

    # 画出最近几天的情况（均线以及MACD）
    stk_df_current = stk_df.tail(plot_current_days_amount)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M20'], 'b--', label='20日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M60'], 'r--', label='60日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['close'], 'g*-', label='收盘价', linewidth=1, markersize=5)

    ax[2].set_xticks(list(range(0, len(stk_df_current['date']))))
    ax[2].set_xticklabels(list(stk_df_current['date']), rotation=90, fontsize=5)
    ax[2].legend(loc='best')

    ax[3].bar(range(0, len(stk_df_current['date'])), stk_df_current['MACD'], label='MACD')
    ax[3].set_xticks(list(range(0, len(stk_df_current['date']))))
    ax[3].set_xticklabels(list(stk_df_current['date']), rotation=90, fontsize=5)
    ax[3].legend(loc='best')

    # 保存图片
    save_dir = root_save_dir+current_date+'/'+str(stk_code)+'/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.tight_layout()
    plt.savefig(save_dir+pic_name, dpi=300)
    plt.close()

    return save_dir+pic_name


def genStkIdxPic(stk_df, stk_code, current_date, root_save_dir, pic_name='stk_idx.png'):
    """
    打印常用指标
    """
    # 按升序排序
    stk_df = stk_df.sort_values(by='date', ascending=True)

    """
    增加指标

    'RSI5', 'RSI12', 'RSI30'
    'SAR'
    'slowk', 'slowd'
    'upper', 'middle', 'lower' 
    'MOM'
    """
    stk_df = add_stk_index_to_df(stk_df).tail(60)

    fig, ax = plt.subplots(nrows=5, ncols=1)

    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI5'], 'b--', label='RSI5线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI12'], 'r--', label='RSI12线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI30'], 'g*--', label='RSI30', linewidth=0.5, markersize=1)

    ax[1].plot(range(0, len(stk_df['date'])), stk_df['SAR'], 'g*--', label='SAR', linewidth=0.5, markersize=1)

    ax[2].plot(range(0, len(stk_df['date'])), stk_df['slowk'], 'g*--', label='slowk', linewidth=0.5, markersize=1)
    ax[2].plot(range(0, len(stk_df['date'])), stk_df['slowd'], 'r*--', label='slowd', linewidth=0.5, markersize=1)

    ax[3].plot(range(0, len(stk_df['date'])), stk_df['upper'], 'r*--', label='布林上线', linewidth=0.5, markersize=1)
    ax[3].plot(range(0, len(stk_df['date'])), stk_df['middle'], 'b*--', label='布林均线', linewidth=0.5, markersize=1)
    ax[3].plot(range(0, len(stk_df['date'])), stk_df['lower'], 'g*--', label='布林下线', linewidth=0.5, markersize=1)

    ax[4].plot(range(0, len(stk_df['date'])), stk_df['MOM'], 'g*--', label='MOM', linewidth=0.5, markersize=1)

    # 准备下标
    xlabel_series = stk_df.apply(lambda x: x['date'][2:].replace('-', ''), axis=1)
    ax[0] = addXticklabel(ax[0], xlabel_series, 40, rotation=45)
    ax[1] = addXticklabel(ax[1], xlabel_series, 40, rotation=45)
    ax[2] = addXticklabel(ax[2], xlabel_series, 40, rotation=45)
    ax[3] = addXticklabel(ax[3], xlabel_series, 40, rotation=45)
    ax[4] = addXticklabel(ax[4], xlabel_series, 40, rotation=45)

    for ax_sig in ax:
        ax_sig.legend(loc='best', fontsize=5)

    # 保存图片
    save_dir = root_save_dir + current_date + '/' + str(stk_code) + '/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.tight_layout()
    plt.savefig(save_dir + pic_name, dpi=300)
    plt.close()

    return save_dir + pic_name


def genStkIdxPicForQQ(stk_df, stk_code=''):

    """
    打印常用指标
    """
    # 按升序排序
    stk_df = stk_df.sort_values(by='date', ascending=True)

    """
    增加指标
    
    'RSI5', 'RSI12', 'RSI30'
    'SAR'
    'slowk', 'slowd'
    'upper', 'middle', 'lower' 
    'MOM'
    """
    stk_df = add_stk_index_to_df(stk_df).tail(60)

    fig, ax = plt.subplots(nrows=5, ncols=1)

    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI5'], 'b--', label='RSI5线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI12'], 'r--', label='RSI12线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI30'], 'g*--', label='RSI30', linewidth=0.5, markersize=1)
    ax[0].plot(range(0, len(stk_df['date'])), [20 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[0].plot(range(0, len(stk_df['date'])), [80 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[0].set_ylim(0, 100)

    ax[1].plot(range(0, len(stk_df['date'])), stk_df['SAR'], 'r--', label='SAR', linewidth=0.5, markersize=1)
    ax[1].plot(range(0, len(stk_df['date'])), stk_df['close'], 'g*--', label='close', linewidth=0.5, markersize=1)

    ax[2].plot(range(0, len(stk_df['date'])), stk_df['slowk'], 'g*--', label='slowk', linewidth=0.5, markersize=1)
    ax[2].plot(range(0, len(stk_df['date'])), stk_df['slowd'], 'r*--', label='slowd', linewidth=0.5, markersize=1)
    ax[2].plot(range(0, len(stk_df['date'])), [20 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[2].plot(range(0, len(stk_df['date'])), [80 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[2].set_ylim(0, 100)

    ax[3].plot(range(0, len(stk_df['date'])), stk_df['upper'], 'r*--', label='布林上线', linewidth=0.5, markersize=1)
    ax[3].plot(range(0, len(stk_df['date'])), stk_df['middle'], 'b*--', label='布林均线', linewidth=0.5, markersize=1)
    ax[3].plot(range(0, len(stk_df['date'])), stk_df['lower'], 'g*--', label='布林下线', linewidth=0.5, markersize=1)

    ax[4].plot(range(0, len(stk_df['date'])), stk_df['MOM'], 'g*--', label='MOM', linewidth=0.5, markersize=1)

    # 准备下标
    xlabel_series = stk_df.apply(lambda x: x['date'][2:].replace('-', ''), axis=1)
    ax[0] = addXticklabel(ax[0], xlabel_series, 40, rotation=45)
    ax[1] = addXticklabel(ax[1], xlabel_series, 40, rotation=45)
    ax[2] = addXticklabel(ax[2], xlabel_series, 40, rotation=45)
    ax[3] = addXticklabel(ax[3], xlabel_series, 40, rotation=45)
    ax[4] = addXticklabel(ax[4], xlabel_series, 40, rotation=45)

    for ax_sig in ax:
        ax_sig.legend(loc='best', fontsize=5)

    fig.tight_layout()  # 调整整体空白
    plt.subplots_adjust(wspace=0, hspace=0)  # 调整子图间距

    # 检查SAR
    attention = False
    sar_tail = stk_df.tail(2)
    sar_tail['compare'] = sar_tail.apply(lambda x: x['SAR'] - x['close'], axis=1)

    if sar_tail.head(1)['compare'].values[0]*sar_tail.tail(1)['compare'].values[0] < 0:
        plt.title(stk_code + ' 注意 SAR 指标异动！')
        attention = True

    return fig, ax, attention


def IsPotInCurveMedian(y_axis, median_neighbourhood):
    """
    该函数用于判断当前点是否在序列拟合成的抛物线的中点
    :param x_axis:
    :param y_axis:
    :param median_neighbourhood: 中点判断的邻域，百分比，在此区域内可认为是中点
    :return:
    """

    # 中间点邻域大小
    m_neigh = len(y_axis)*median_neighbourhood/2.0

    # 统一格式
    x_axis_array = np.array(range(0, len(y_axis)))
    y_axis_array = np.array(y_axis)

    # 对MACD进行归一化，以便后面计算误差
    M_max = np.max(y_axis_array)
    M_min = np.min(y_axis_array)
    y_axis_array_std = np.array(list(map(lambda x: (x-M_min)/(M_max-M_min), y_axis_array)))

    # 对归一化后的MACD进行二次拟合
    c = np.polyfit(x_axis_array, y_axis_array_std, 2)

    # 计算其拟合后曲线
    y_axis_fit = np.array(list(map(lambda x: c[0]*x**2+c[1]*x+c[2], x_axis_array)))

    # 计算误差
    err = np.mean(y_axis_fit-y_axis_array_std)

    a = c[0]
    b = c[1]
    bottom = -1 * (b / (2 * a))

    # 数据长度
    data_length = len(y_axis)

    if (data_length-1)/2.0 - m_neigh < bottom < (data_length-1)/2.0 + m_neigh:
        corner_flag = True
    else:
        corner_flag = False

    # 计算当前距离拐点的距离
    corner_dist_ratio = (bottom-(data_length/2-1))/data_length

    return {
        'corner_flag': corner_flag,
        'err': err,
        'corner_dist_ratio': corner_dist_ratio
    }


def JudgeCornerPot(stk_df, stk_code, current_date, debug=False):

    """
    函数功能：判断一支标的的拐点
    :return:
    :param debug 为真是不打印图片

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
    sh_index = stk_df.tail(100)
    # sh_index['date'] = sh_index.index

    # 按时间降序排序，方便计算MACD
    sh_index = sh_index.sort_values(by='date', ascending=True)

    # 在原始df中增加MACD信息
    sh_index['MACD'], sh_index['MACDsignal'], sh_index['MACDhist'] = talib.MACD(sh_index.close,
                                                                                fastperiod=12, slowperiod=26,
                                                                                signalperiod=9)

    # sh_index_dropna = sh_index.dropna(how='any', axis=0).reset_index(drop=True)
    sh_index_dropna = sh_index

    # 获取最后几个值
    sh_index_now = sh_index_dropna.tail(cubic_test_last_step)

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
    err = np.mean(list(map(lambda x: x**2, sh_index_now['MACD_Fit_Err'])))

    a = c[0]
    b = c[1]
    bottom = -1 * (b / (2 * a))

    if step_corner_detect - 1.5 < bottom < step_corner_detect + 1.5:
        corner_flag = True
    else:
        corner_flag = False

    # 如果当前是拐点，则打印图片保存于指定位置
    if corner_flag:

        # 生成图片
        if not debug:
            genStkPic(stk_df=stk_df, stk_code=stk_code, root_save_dir=pic_save_dir_root, current_date=current_date)

        # 返回字典信息
        return {
            "corner_flag": corner_flag,
            "err": err,
            "stk_code": stk_code
        }
    else:
        return {
            "corner_flag": corner_flag,
            "err": err,
            "stk_code": stk_code
        }


def callback():
    """
    函数功能：计时器的回调函数，相当于实际的主函数
    :return:
    """

    # 遍历stk仓
    result_list = []
    for stk in stk_list:

        # 下载该stk的数据
        stk_df = ts.get_k_data(stk)

        # 判断拐点
        stk_Judge_result = JudgeCornerPot(stk_code=stk, stk_df=stk_df)

        # 汇集判断结果
        result_list.append(stk_Judge_result)

    # 将结果整合为df
    result_df = pd.DataFrame(result_list)

    # 判断是否有存在拐点的stk？
    result_df_corner = result_df[result_df['corner_flag']]

    if not result_df_corner.empty:
        for idx in result_df_corner.index:

            idx

    end=0


def add_stk_index_to_df(stk_df):
    """
    向含有“收盘价（close）”的df中添加相关stk指标

    :param stk_df:
    :return:
    """
    """
    准备指标：
    MACD
    RSI
    KD
    SAR
    BRAR
    BIAS
    """
    stk_df['MACD'], stk_df['MACDsignal'], stk_df['MACDhist'] = talib.MACD(stk_df.close,
                                                                          fastperiod=12, slowperiod=26,
                                                                          signalperiod=9)

    # 添加rsi信息
    stk_df['RSI5'] = talib.RSI(stk_df.close, timeperiod=5)
    stk_df['RSI12'] = talib.RSI(stk_df.close, timeperiod=12)
    stk_df['RSI30'] = talib.RSI(stk_df.close, timeperiod=30)

    # 添加SAR指标
    stk_df['SAR'] = talib.SAR(stk_df.high, stk_df.low, acceleration=0.05, maximum=0.2)

    # 添加KD指标
    stk_df['slowk'], stk_df['slowd'] = talib.STOCH(stk_df.high,
                                                   stk_df.low,
                                                   stk_df.close,
                                                    fastk_period=9,
                                                    slowk_period=3,
                                                    slowk_matype=0,
                                                    slowd_period=3,
                                                    slowd_matype=0)

    # 添加布林线
    stk_df['upper'], stk_df['middle'], stk_df['lower'] = talib.BBANDS(stk_df['close'], matype=MA_Type.T3)

    # 计算close动量
    stk_df['MOM'] = talib.MOM(stk_df['close'], timeperiod=5)

    return stk_df


def genSingleStkTrainData(stk_K_df, M_int, stk_code, stk_name):
    """
    生成一支stk的训练数据
    添加指标和均线拐点标签
    :param stk_K_df:
    :return:
    """

    sh_index = stk_K_df

    # 按升序排序
    stk_df = sh_index.sort_values(by='date', ascending=True)

    # 添加指标
    stk_df = add_stk_index_to_df(stk_df)

    # 计算收盘价均线，根据均线计算拐点
    stk_df['M'+str(M_int)] = stk_df['close'].rolling(window=M_int, center=True).mean()

    # 计算收盘价均线（先验数据）
    stk_df['M'+str(M_int)+'pre'] = stk_df['close'].rolling(window=M_int, center=False).mean()

    # 求解均线后验拐点
    for idx in stk_df.loc[corner_Pot_Retrospective_Half:len(stk_df) - corner_Pot_Retrospective_Half, :].index:

        # 进行二次曲线拟合
        r = IsPotInCurveMedian(
            y_axis=stk_df.loc[idx - corner_Pot_Retrospective_Half:idx + corner_Pot_Retrospective_Half, 'M21'],
            median_neighbourhood=0.1)

        stk_df.loc[idx, 'corner_flag_M21'] = r['corner_flag']
        stk_df.loc[idx, 'err_M21'] = r['err']
        stk_df.loc[idx, 'corner_dist_ratio'] = math.atan(r['corner_dist_ratio'])

    # 取出秒数轴用于后续的横坐标
    stk_df['second'] = stk_df.apply(lambda x: DateStr2Sec(x['date']), axis=1)

    sh_index = stk_df.dropna(how='any')

    return sh_index


def sliceDfToTrainData(df, length, feature_cols, label_col, norm_flag=False):
    """
    函数功能：

    专门为LSTM模型准备训练数据之用！

    给定原始数据df、序列长度length以及作为标签的列的名字，
    根据这些信息，将df切片，生成（feature，label）的list

    :param df:
    :param length:
    :param label_col:
    :return:
    """

    # 重置索引
    df = df.reset_index()

    # 进行数据切片
    r_list = []
    for idx in df.loc[0:len(df) - length - 1, :].index:

        # 取出这一段的df
        df_seg = df.loc[idx:idx + length, feature_cols + [label_col[0]]]

        # 是否对输入数据进行归一化
        if norm_flag:
            for col in feature_cols:
                df_seg[col] = normalize(df_seg.loc[:, col])

        r_list.append(
            (
                df_seg.loc[:, feature_cols].values,
                df_seg.loc[:, [label_col[0]]].values
            )
        )

    return r_list

# --------------------------- 测试 -------------------------------


if __name__ == '__main__':

    stk_K = ts.get_k_data('300508')

    r = genStkIdxPic(stk_K, '300508', get_current_date_str(), pic_save_dir_root, pic_name='stk_idx.png')
    end = 0