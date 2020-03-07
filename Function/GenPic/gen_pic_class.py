# encoding=utf-8

"""
与图片生成相关的类
"""


import multiprocessing
import calendar
import pandas as pd
import talib
import wx
import os

from jqdatasdk import logout
from DataSource.auth_info import jq_login
from Config.GlobalSetting import plot_current_days_amount
from DataSource.Code2Name import code2name
from PIL import Image
from io import BytesIO
from pylab import *
from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df
from SDK.Debug_Sub import debug_print_txt
from SDK.MyTimeOPT import get_current_date_str, get_current_datetime_str, add_date_str
from SDK.PlotOptSub import addXticklabel_list, add_axis

import matplotlib

from SDK.rank_note_class import RankNote

matplotlib.use('agg')

# 解决无法显示汉字和符号的问题
mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


class GenPic:
    """
    图片生成的基类
    """
    def __init__(self):
        self.log = ''

    @staticmethod
    def plot_macd(ax, df, label):
        ax.bar(range(0, len(df)), df['MACD'], label='MACD_' + label)
        ax.plot(range(0, len(df)), df['MACDsignal'], 'g--')
        ax.plot(range(0, len(df)), df['MACDhist'], 'y--')

        return ax

    @staticmethod
    def down_minute_data(stk_code, freq):
        try:
            df = get_k_data_JQ(stk_code, count=300,
                                  end_date=add_date_str(get_current_date_str(), 1), freq=freq)

            # 去掉volume为空的行
            df = df.loc[df.apply(lambda x: not (x['volume'] == 0), axis=1), :]

            # 增加指标计算
            df = add_stk_index_to_df(df)

            if str(df.index[-1]) > get_current_datetime_str():
                df = df[:-1]
            return df

        except Exception as e_:
            # self.log = self.log + '函数down_minute_data：\n %s\n' % str(e_)
            print('函数down_minute_data：\n %s\n' % str(e_))
            return pd.DataFrame()

    @staticmethod
    def gen_hour_macd_values(stk_code, debug=False):

        return GenPic.down_minute_data(stk_code, '30m'), GenPic.down_minute_data(stk_code, '60m')

    @staticmethod
    def plot_w_m(df_w, df_m):
        """

        :param df_w:
        :param df_m:
        :return:
        """
        """ --------------------------------------- 生成图片 -------------------------------------"""
        fig, ax = subplots(ncols=1, nrows=4)

        ax[0].plot(range(0, len(df_w['date'])), df_w['close'], 'g*--', label='close')
        ax[1] = GenPic.plot_macd(ax[1], df_w, 'week')
        ax[1].plot(range(0, len(df_w['date'])), [0 for x in range(0, len(df_w['date']))], 'r--', label='week_MACD')

        ax[2].plot(range(0, len(df_m['date'])), df_m['close'], 'g*--', label='close')
        ax[3] = GenPic.plot_macd(ax[3], df_m, 'month')
        ax[3].plot(range(0, len(df_m['date'])), [0 for x in range(0, len(df_m['date']))], 'r--', label='month_MACD')

        return fig, ax

    @staticmethod
    def convert_pic_to_data(pic_url):
        img = Image.open(pic_url)
        output = BytesIO()  # 如是StringIO分引起TypeError: string argument expected, got 'bytes'
        img.convert("RGB").save(output, "PNG")  # 以BMP格式保存流
        img.close()
        wx_img = wx.Image(output, wx.BITMAP_TYPE_PNG)
        output.close()

        return wx_img

    @staticmethod
    def convert_fig_to_img(fig):
        output = BytesIO()  # BytesIO实现了在内存中读写byte

        fig.canvas.print_png(output, dpi=20)
        output.seek(0)
        img = wx.Image(output, wx.BITMAP_TYPE_ANY)

        output.close()
        plt.close(fig)

        return img

    @staticmethod
    def set_background_color(bc='w'):
        """
        设置背景色
        :param bc:

            b_r：背景红         #FA8072
            b_g：背景绿         #98FB98
            b_y：背景黄         #FFFFE0

        :return:
        """
        if bc is 'b_r':
            plt.rcParams['figure.facecolor'] = 'r'
        elif bc is 'b_g':
            plt.rcParams['figure.facecolor'] = 'g'
        elif bc is 'b_y':
            plt.rcParams['figure.facecolor'] = 'y'
        else:
            plt.rcParams['figure.facecolor'] = 'w'

    @staticmethod
    def gen_day_pic(stk_df, stk_code=''):
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

        # 检查日级别的MACD是否有异常
        attention = False
        MACD_list = stk_df.tail(3)['MACD'].values

        if MACD_list[1] == np.min(MACD_list):
            attention = True

            # 设置背景红
            GenPic.set_background_color('b_r')

        elif MACD_list[1] == np.max(MACD_list):
            attention = True

            # 设置背景绿
            GenPic.set_background_color('b_g')
        else:
            GenPic.set_background_color()

        fig, ax = plt.subplots(nrows=4, ncols=1)

        ax[0].plot(range(0, len(stk_df['date'])), stk_df['M20'], 'b--', label='20日均线', linewidth=1)
        ax[0].plot(range(0, len(stk_df['date'])), stk_df['M60'], 'r--', label='60日均线', linewidth=1)
        ax[0].plot(range(0, len(stk_df['date'])), stk_df['close'], 'g*--', label='收盘价', linewidth=0.5, markersize=1)

        ax[1].bar(range(0, len(stk_df['date'])), stk_df['MACD'], label='MACD')
        ax[1] = GenPic.plot_macd(ax[1], stk_df, 'day')

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
        ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['close'], 'g*-', label='收盘价', linewidth=1,
                   markersize=5)
        ax[3] = GenPic.plot_macd(ax[3], stk_df_current, 'day')

        # 设置标题并返回分析结果
        result_analysis = []
        if MACD_list[1] == np.min(MACD_list):
            title_tmp = stk_code + ' ' + code2name(stk_code) + ' 日级别 MACD 低点！后续数天可能上涨！'
            ax[0].set_title(title_tmp)
            result_analysis.append(title_tmp + RankNote.print_day_close_rank(stk_df))

        elif MACD_list[1] == np.max(MACD_list):
            title_tmp = stk_code + ' ' + code2name(stk_code) + ' 日级别 MACD 高点！后续数天可能下跌！'
            ax[0].set_title(title_tmp)
            result_analysis.append(title_tmp + RankNote.print_day_close_rank(stk_df))

        # 准备下标
        xticklabels_all_list = list(stk_df_current['date'].sort_values(ascending=True))
        xticklabels_all_list = [x.replace('-', '')[2:] for x in xticklabels_all_list]

        for ax_sig in ax[2:4]:
            ax_sig = addXticklabel_list(ax_sig, xticklabels_all_list, 30, rotation=45)
            ax_sig.legend(loc='best', fontsize=5)

        fig.tight_layout()  # 调整整体空白
        plt.subplots_adjust(wspace=0, hspace=1)  # 调整子图间距
        # plt.close()

        return fig, ax, attention, result_analysis

    @staticmethod
    def gen_day_pic_local(stk_df, stk_code='', save_dir=''):
        """
        采用将图片保存到本地的方式
        :param stk_data:
        :param source:
        :param title:
        :param save_dir:
        :return:
        """
        r = GenPic.gen_day_pic(stk_df, stk_code=stk_code)
        fig_tmp = r[0]
        analysis_str = r[3]
        plt.savefig(save_dir, facecolor=fig_tmp.get_facecolor())
        plt.close()

        return analysis_str

    @staticmethod
    def gen_hour_macd_pic(stk_data, debug=False, stk_code=''):

        if debug:
            print('进入GenPic.gen_hour_macd_pic函数！')
            debug_print_txt('macd_hour_pic', stk_code, '\n----------------------\n\n', enable=debug)

        # 生成小时macd数据
        # df_30, df_60 = gen_hour_macd_values(stk_code, source=source, title=title)
        df_30, df_60 = stk_data

        if debug:
            debug_print_txt('macd_hour_pic', stk_code,
                            'df_30原始数据:\n' + str(df_30) + '\n\n' + 'df_60原始数据:\n' + str(df_60) + '\n\n', enable=debug)

        # 根据情况设置背景色
        m30 = df_30.tail(3)['MACD'].values
        m60 = df_60.tail(3)['MACD'].values

        if debug:
            debug_print_txt('macd_hour_pic', stk_code,
                            'm30原始数据:\n' + str(m30) + '\n\n' + 'm60原始数据:\n' + str(m60) + '\n\n')

        if (m30[1] == np.min(m30)) | (m60[1] == np.min(m60)):

            # 设置背景红
            GenPic.set_background_color('b_r')

        elif (m30[1] == np.max(m30)) | (m60[1] == np.max(m60)):

            # 设置背景绿
            GenPic.set_background_color('b_g')
        else:
            GenPic.set_background_color()

        # 调整显示长度
        df_30 = df_30.tail(40)
        df_60 = df_60.tail(40)

        fig, ax = plt.subplots(ncols=1, nrows=4)

        ax[0].plot(range(0, len(df_30)), df_30['close'], 'g*--', label='close_30min')
        ax[1] = GenPic.plot_macd(ax[1], df_30, '30min')

        ax[2].plot(range(0, len(df_60)), df_60['close'], 'g*--', label='close_60min')
        ax[3] = GenPic.plot_macd(ax[1], df_60, '60min')

        # 设置下标
        ax[1] = addXticklabel_list(
            ax[1],
            list([str(x)[-11:-3] for x in df_30['datetime']]),
            15, rotation=0, fontsize=6)

        ax[3] = addXticklabel_list(
            ax[3],
            list([str(x)[-11:-3] for x in df_60['datetime']]),
            15, rotation=0, fontsize=6)

        for ax_sig in ax:
            ax_sig.legend(loc='best')

        # 设置标题
        if m30[1] == np.min(m30):
            title = stk_code + '半小时MACD低点！'

        elif m60[1] == np.min(m60):
            title = stk_code + '小时MACD低点！'

        elif m30[1] == np.max(m30):
            title = stk_code + '半小时MACD高点！'

        elif m60[1] == np.max(m60):
            title = stk_code + '小时MACD高点！'

        else:
            title = stk_code

        ax[0].set_title(title)

        if debug:
            debug_print_txt('macd_hour_pic', stk_code, '结论:' + title + '\n\n')

        fig.tight_layout()
        plt.subplots_adjust(wspace=0, hspace=0.3)  # 调整子图间距

        return fig

    @staticmethod
    def gen_hour_macd_pic_local(stk_data, stk_code, save_dir=''):
        """
        采用将图片保存到本地的方式
        :param stk_data:
        :param source:
        :param title:
        :param save_dir:
        :return:
        """
        fig_tmp = GenPic.gen_hour_macd_pic(stk_data, stk_code=stk_code, debug=True)
        plt.savefig(save_dir, facecolor=fig_tmp.get_facecolor())
        plt.close()

        return None

    @staticmethod
    def gen_hour_idx_pic(stk_df, stk_code='', debug=False):
        """
        打印常用指标
        """
        # 按升序排序
        stk_df_ = stk_df.sort_values(by='datetime', ascending=True)

        """
        增加指标

        'RSI5', 'RSI12', 'RSI30'
        'SAR'
        'slowk', 'slowd'
        'upper', 'middle', 'lower'
        'MOM'
        """
        stk_df_ = add_stk_index_to_df(stk_df_).tail(60)

        GenPic.set_background_color(bc='w')

        result_analysis = []

        # 检查SAR
        attention = False
        sar_tail_origin = stk_df_.tail(2)
        sar_tail = sar_tail_origin.copy()
        sar_tail['compare'] = sar_tail_origin.apply(lambda x: x['SAR'] - x['close'], axis=1)

        title_tmp = stk_code + ' ' + code2name(stk_code)

        if sar_tail.head(1)['compare'].values[0] * sar_tail.tail(1)['compare'].values[0] < 0:
            if sar_tail.tail(1)['SAR'].values[0] < sar_tail.tail(1)['close'].values[0]:
                title_tmp = stk_code + ' ' + code2name(stk_code) + ' 注意 SAR 指标翻转，后续数小时可能上涨！'
                result_analysis.append(title_tmp + RankNote.print_hour_close_rank(stk_df))
                GenPic.set_background_color(bc='b_r')
            else:
                title_tmp = stk_code + ' ' + code2name(stk_code) + ' 注意 SAR 指标翻转，后续数小时可能下跌！'
                result_analysis.append(title_tmp + RankNote.print_hour_close_rank(stk_df))
                GenPic.set_background_color(bc='b_g')

            attention = True

        fig, ax = plt.subplots(nrows=5, ncols=1)

        ax[0].plot(range(0, len(stk_df_['datetime'])), stk_df_['RSI5'], 'b--', label='RSI5线', linewidth=1)
        ax[0].plot(range(0, len(stk_df_['datetime'])), stk_df_['RSI12'], 'r--', label='RSI12线', linewidth=1)
        ax[0].plot(range(0, len(stk_df_['datetime'])), stk_df_['RSI30'], 'g*--', label='RSI30', linewidth=0.5,
                   markersize=1)
        ax[0].plot(range(0, len(stk_df_['datetime'])), [20 for a in range(len(stk_df_['datetime']))], 'b--',
                   linewidth=0.3)
        ax[0].plot(range(0, len(stk_df_['datetime'])), [80 for a in range(len(stk_df_['datetime']))], 'b--',
                   linewidth=0.3)
        ax[0].set_ylim(0, 100)

        ax[1].plot(range(0, len(stk_df_['datetime'])), stk_df_['SAR'], 'r--', label='SAR', linewidth=0.5, markersize=1)
        ax[1].plot(range(0, len(stk_df_['datetime'])), stk_df_['close'], 'g*--', label='close', linewidth=0.5,
                   markersize=1)

        ax[2].plot(range(0, len(stk_df_['datetime'])), stk_df_['slowk'], 'g*--', label='slowk', linewidth=0.5,
                   markersize=1)
        ax[2].plot(range(0, len(stk_df_['datetime'])), stk_df_['slowd'], 'r*--', label='slowd', linewidth=0.5,
                   markersize=1)
        ax[2].plot(range(0, len(stk_df_['datetime'])), [20 for a in range(len(stk_df_['datetime']))], 'b--',
                   linewidth=0.3)
        ax[2].plot(range(0, len(stk_df_['datetime'])), [80 for a in range(len(stk_df_['datetime']))], 'b--',
                   linewidth=0.3)
        ax[2].set_ylim(0, 100)

        ax[3].plot(range(0, len(stk_df_['datetime'])), stk_df_['upper'], 'r*--', label='布林上线', linewidth=0.5,
                   markersize=1)
        ax[3].plot(range(0, len(stk_df_['datetime'])), stk_df_['middle'], 'b*--', label='布林均线', linewidth=0.5,
                   markersize=1)
        ax[3].plot(range(0, len(stk_df_['datetime'])), stk_df_['lower'], 'g*--', label='布林下线', linewidth=0.5,
                   markersize=1)

        ax[4].plot(range(0, len(stk_df_['datetime'])), stk_df_['MOM'], 'g*--', label='MOM', linewidth=0.5, markersize=1)

        # 准备下标
        xlabel_series = stk_df_.apply(lambda x: str(x['datetime'])[2:16].replace('-', ''), axis=1)
        ax[4] = add_axis(ax[4], xlabel_series, 15, rotation=15, fontsize=7)

        for ax_sig in ax:
            ax_sig.legend(loc='best', fontsize=7)

        fig.tight_layout()  # 调整整体空白
        plt.subplots_adjust(wspace=0, hspace=0)  # 调整子图间距
        ax[0].set_title(title_tmp)

        # 打印过程日志
        if debug:
            txt_name = 'hour_index_pic'

            # 打印原始数据
            debug_print_txt(txt_name, stk_code, stk_df_.to_string() + '\n\n')

            # 打印结果
            debug_print_txt(txt_name, stk_code, '结果：\n' + str(result_analysis) + '\n\n')

        return fig, ax, attention, result_analysis

    @staticmethod
    def gen_hour_index_pic_local(stk_data, stk_code, save_dir=''):
        """
        采用将图片保存到本地的方式
        :param stk_data:
        :param source:
        :param title:
        :param save_dir:
        :return:
        """
        if stk_data.empty:
            return '输入数据为空，无法生成图片！'

        r = GenPic.gen_hour_idx_pic(stk_data, stk_code=stk_code, debug=True)
        fig_tmp = r[0]
        analysis_str = r[3]
        plt.savefig(save_dir, facecolor=fig_tmp.get_facecolor())
        plt.close()

        return analysis_str

    @staticmethod
    def gen_w_m_macd_pic(stk_data, stk_code=''):
        """

        :param stk_data:
        :param towho:
        :return:
        """

        df = stk_data
        if len(df) < 350:
            print('函数week_MACD_stray_judge：' + stk_data + '数据不足！')
            return False

        # 规整
        df_floor_origin = df.tail(math.floor(len(df) / 20) * 20 - 19)
        df_floor = df_floor_origin.copy()

        # 增加每周的星期几
        df_floor['day'] = df_floor_origin.apply(
            lambda x: calendar.weekday(int(x['date'].split('-')[0]), int(x['date'].split('-')[1]),
                                       int(x['date'].split('-')[2])), axis=1)

        # 隔着5个取一个
        if df_floor.tail(1)['day'].values[0] != 4:
            df_floor_slice_5_origin = pd.concat([df_floor[df_floor.day == 4], df_floor.tail(1)], axis=0)
        else:
            df_floor_slice_5_origin = df_floor[df_floor.day == 4]

        # 获取最后的日期
        date_last = df_floor_slice_5_origin.tail(1)['date'].values[0]
        df_floor_slice_5 = df_floor_slice_5_origin.copy()

        # 计算指标
        df_floor_slice_5['MACD'], df_floor_slice_5['MACDsignal'], df_floor_slice_5['MACDhist'] = talib.MACD(
            df_floor_slice_5.close,
            fastperiod=6, slowperiod=12,
            signalperiod=9)

        # 隔着20个取一个（月线）
        df_floor_slice_20_origin = df_floor.loc[::20, :]
        df_floor_slice_20 = df_floor_slice_20_origin.copy()

        # 计算指标
        df_floor_slice_20['MACD'], df_floor_slice_20['MACDsignal'], df_floor_slice_20['MACDhist'] = talib.MACD(
            df_floor_slice_20.close,
            fastperiod=4,
            slowperiod=8,
            signalperiod=9)

        GenPic.set_background_color(bc='w')

        """ --------------------------------------- 生成图片 -------------------------------------"""
        fig, ax = GenPic.plot_w_m(df_floor_slice_5, df_floor_slice_20)

        # 增加标题
        plt.title(stk_code + 'month-stray' + date_last)

        return fig

    @staticmethod
    def gen_w_m_macd_pic_local(stk_data, stk_code, save_dir=''):
        """
        采用将图片保存到本地的方式
        :param stk_data:
        :param source:
        :param title:
        :param save_dir:
        :return:
        """
        fig_tmp = GenPic.gen_w_m_macd_pic(stk_data, stk_code)
        plt.savefig(save_dir, facecolor=fig_tmp.get_facecolor())
        plt.close()

    @staticmethod
    def gen_idx_pic(stk_df, stk_code=''):
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
        stk_df_ = add_stk_index_to_df(stk_df).tail(60)

        GenPic.set_background_color(bc='w')

        result_analysis = []

        # 检查SAR
        attention = False
        sar_tail_origin = stk_df_.tail(2)
        sar_tail = sar_tail_origin.copy()
        sar_tail['compare'] = sar_tail_origin.apply(lambda x: x['SAR'] - x['close'], axis=1)

        title_tmp = stk_code + ' ' + code2name(stk_code)

        if sar_tail.head(1)['compare'].values[0] * sar_tail.tail(1)['compare'].values[0] < 0:
            if sar_tail.tail(1)['SAR'].values[0] < sar_tail.tail(1)['close'].values[0]:
                title_tmp = stk_code + ' ' + code2name(stk_code) + ' 注意 SAR 指标翻转，后续数天可能上涨！'
                result_analysis.append(title_tmp + RankNote.print_day_close_rank(stk_df))
                GenPic.set_background_color(bc='b_r')
            else:
                title_tmp = stk_code + ' ' + code2name(stk_code) + ' 注意 SAR 指标翻转，后续数天可能下跌！'
                result_analysis.append(title_tmp + RankNote.print_day_close_rank(stk_df))
                GenPic.set_background_color(bc='b_g')

            attention = True

        fig, ax = plt.subplots(nrows=5, ncols=1)

        ax[0].plot(range(0, len(stk_df_['date'])), stk_df_['RSI5'], 'b--', label='RSI5线', linewidth=1)
        ax[0].plot(range(0, len(stk_df_['date'])), stk_df_['RSI12'], 'r--', label='RSI12线', linewidth=1)
        ax[0].plot(range(0, len(stk_df_['date'])), stk_df_['RSI30'], 'g*--', label='RSI30', linewidth=0.5, markersize=1)
        ax[0].plot(range(0, len(stk_df_['date'])), [20 for a in range(len(stk_df_['date']))], 'b--', linewidth=0.3)
        ax[0].plot(range(0, len(stk_df_['date'])), [80 for a in range(len(stk_df_['date']))], 'b--', linewidth=0.3)
        ax[0].set_ylim(0, 100)

        ax[1].plot(range(0, len(stk_df_['date'])), stk_df_['SAR'], 'r--', label='SAR', linewidth=0.5, markersize=1)
        ax[1].plot(range(0, len(stk_df_['date'])), stk_df_['close'], 'g*--', label='close', linewidth=0.5, markersize=1)

        ax[2].plot(range(0, len(stk_df_['date'])), stk_df_['slowk'], 'g*--', label='slowk', linewidth=0.5, markersize=1)
        ax[2].plot(range(0, len(stk_df_['date'])), stk_df_['slowd'], 'r*--', label='slowd', linewidth=0.5, markersize=1)
        ax[2].plot(range(0, len(stk_df_['date'])), [20 for a in range(len(stk_df_['date']))], 'b--', linewidth=0.3)
        ax[2].plot(range(0, len(stk_df_['date'])), [80 for a in range(len(stk_df_['date']))], 'b--', linewidth=0.3)
        ax[2].set_ylim(0, 100)

        ax[3].plot(range(0, len(stk_df_['date'])), stk_df_['upper'], 'r*--', label='布林上线', linewidth=0.5, markersize=1)
        ax[3].plot(range(0, len(stk_df_['date'])), stk_df_['middle'], 'b*--', label='布林均线', linewidth=0.5, markersize=1)
        ax[3].plot(range(0, len(stk_df_['date'])), stk_df_['lower'], 'g*--', label='布林下线', linewidth=0.5, markersize=1)

        ax[4].plot(range(0, len(stk_df_['date'])), stk_df_['MOM'], 'g*--', label='MOM', linewidth=0.5, markersize=1)

        # 准备下标
        xlabel_series = stk_df_.apply(lambda x: x['date'][2:].replace('-', ''), axis=1)
        ax[0] = add_axis(ax[0], xlabel_series, 40, rotation=45)
        ax[1] = add_axis(ax[1], xlabel_series, 40, rotation=45)
        ax[2] = add_axis(ax[2], xlabel_series, 40, rotation=45)
        ax[3] = add_axis(ax[3], xlabel_series, 40, rotation=45)
        ax[4] = add_axis(ax[4], xlabel_series, 40, rotation=45)

        for ax_sig in ax:
            ax_sig.legend(loc='best', fontsize=5)

        fig.tight_layout()  # 调整整体空白
        plt.subplots_adjust(wspace=0, hspace=0)  # 调整子图间距
        ax[0].set_title(title_tmp)

        return fig, ax, attention, result_analysis

    @staticmethod
    def gen_idx_pic_local(stk_df, stk_code='', save_dir=''):
        """
        采用将图片保存到本地的方式
        :param stk_data:
        :param source:
        :param title:
        :param save_dir:
        :return:
        """
        r = GenPic.gen_idx_pic(stk_df, stk_code=stk_code)
        fig_tmp = r[0]
        analysis_str = r[3]
        plt.savefig(save_dir, facecolor=fig_tmp.get_facecolor())
        plt.close()

        return analysis_str


class GenPicWx(GenPic):
    def __init__(self):
        super().__init__()

    # @staticmethod
    # def gen_half_hour_sar(df_30, debug=False):
    #     """
    #     给定半小时数据，为其增加指标，并按时间进行截取
    #     （为海选功能设计的函数）
    #     :param df_30_:
    #     :return:
    #     """
    #     try:
    #         # 去掉volume为空的行
    #         df_30_ = df_30.loc[df_30.apply(lambda x: not (x['volume'] == 0), axis=1), :]
    #
    #         # 添加SAR指标
    #         df_30_['SAR'] = talib.SAR(df_30_.high, df_30_.low, acceleration=0.05, maximum=0.2)
    #
    #         # 生成图片
    #         df_30_ = df_30_.dropna()
    #
    #         if str(df_30_.index[-1]) > get_current_datetime_str():
    #             df_30_ = df_30_[:-1]
    #
    #         return df_30_
    #     except Exception as e:
    #         print('计算小时sar数据出错，原因：\n' + str(e) + '\n' + '输入数据为：\n')
    #         print(df_30.to_string())
    #         return pd.DataFrame()

    # @staticmethod
    # def gen_hour_macd_values(stk_code, source='jq', title='', debug=False):
    #     if debug:
    #         print('开始下载' + str(stk_code) + '的小时数据！')
    #
    #     if source == 'jq':
    #         df_30 = get_k_data_JQ(stk_code, count=300,
    #                               end_date=add_date_str(get_current_date_str(), 1), freq='30m')
    #         df_60 = get_k_data_JQ(stk_code, count=300,
    #                               end_date=add_date_str(get_current_date_str(), 1), freq='60m')
    #
    #     elif source == 'ts':
    #         df_30 = my_pro_bar(stk_code, start=add_date_str(get_current_date_str(), -20), freq='30min')
    #         df_60 = my_pro_bar(stk_code, start=add_date_str(get_current_date_str(), -20), freq='60min')
    #
    #     # 去掉volume为空的行
    #     df_30 = df_30.loc[df_30.apply(lambda x: not (x['volume'] == 0), axis=1), :]
    #     df_60 = df_60.loc[df_60.apply(lambda x: not (x['volume'] == 0), axis=1), :]
    #
    #     # 增加指标计算
    #     df_30 = add_stk_index_to_df(df_30)
    #     df_60 = add_stk_index_to_df(df_60)
    #
    #     # 生成图片
    #     df_30 = df_30.dropna()
    #     df_60 = df_60.dropna()
    #
    #     if str(df_60.index[-1]) > get_current_datetime_str():
    #         df_60 = df_60[:-1]
    #
    #     if str(df_30.index[-1]) > get_current_datetime_str():
    #         df_30 = df_30[:-1]
    #
    #     return df_30, df_60

    @staticmethod
    def gen_hour_index_pic_wx(stk_data, source='jq', title='', debug=False):
        # 清楚时间未到的数据
        df_30 = stk_data.loc[stk_data.apply(lambda x: not (x['volume'] == 0), axis=1), :]

        fig_tmp = GenPic.gen_hour_idx_pic(df_30, stk_code='', debug=True)[0]
        img = GenPic.convert_fig_to_img(fig_tmp)
        return img

    @staticmethod
    def gen_hour_macd_pic_wx(stk_data, source='jq', title=''):
        """

        :param stk_data:
        :param source:
        :param title:
        :return:
        """
        fig_tmp = GenPic.gen_hour_macd_pic(stk_data, debug=True)
        img = GenPic.convert_fig_to_img(fig_tmp)
        return img

    @staticmethod
    def gen_w_m_macd_pic_wx(stk_data):
        fig_tmp = GenPic.gen_w_m_macd_pic(stk_data)
        img = GenPic.convert_fig_to_img(fig_tmp)
        return img

    @staticmethod
    def gen_day_pic_wx(stk_df, stk_code=''):
        r_tuple = GenPic.gen_day_pic(stk_df, stk_code=stk_code)
        fig_tmp = r_tuple[0]
        img = GenPic.convert_fig_to_img(fig_tmp)
        return img, r_tuple[3]


class GenListPic:
    def __init__(self, stk_list, pool, save_dir):
        self.save_dir = save_dir
        self.pool = pool
        self.stk_list = stk_list

        self.log = ''

    def update_all_pic(self):
        """
        更新所有图片
        :return:
        """

        # init update pic
        pool = self.pool

        hour_pic = {
            'h': self.gen_stk_list_kind_pic('h', pool),
            'h_idx': self.gen_stk_list_kind_pic('h_idx', pool)
        }
        day_pic = {
            'd': self.gen_stk_list_kind_pic('d', pool),
            'd_idx': self.gen_stk_list_kind_pic('d_idx', pool),
            'wm': self.gen_stk_list_kind_pic('wm', pool)
        }
        pool.close()
        pool.join()

        return hour_pic, day_pic

    def gen_stk_list_kind_pic(self, kind, pool):
        """
    	造图片，存本地
    	:param kind:
    	h:小时
    	h_idx:小时idx
    	d:天
    	wm:周、月
    	idx: 指数
    	:return:

    	返回的图片应该 执行page和行号，便于更新！
    	以多层字典的方式返回结果，第一层区分page，第二层区分行号！
    	"""

        jq_login()

        """ 在外部下载需要的数据，防止多进程中重复连接聚宽 """
        r_dic = {}
        for stk in self.stk_list:

            if kind is 'h':
                r_dic[stk + '_d'] = GenPic.gen_hour_macd_values(stk)
            elif kind is 'h_idx':
                r_dic[stk + '_d'] = GenPic.gen_hour_macd_values(stk)[0]
            elif kind is 'd':
                r_dic[stk + '_d'] = get_k_data_JQ(stk, 400)
            elif kind is 'wm':
                r_dic[stk + '_d'] = get_k_data_JQ(stk, count=400,
                                                        end_date=get_current_date_str()).reset_index()
            elif kind is 'd_idx':
                r_dic[stk + '_d'] = get_k_data_JQ(stk, 400)
        logout()

        """ 生成pic """
        for stk in self.stk_list:

            # 保存路径
            save_dir = self.save_dir + get_current_date_str() + '/' + stk + kind + '/'
            file_name = get_current_datetime_str()[:-3].replace(':', '').replace(' ', '').replace('-', '') + '.png'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            try:
                if kind is 'h':
                    r_dic[stk + '_res'] = pool.apply_async(GenPic.gen_hour_macd_pic_local, (
                        r_dic[stk + '_d'], stk, save_dir + file_name))

                elif kind is 'h_idx':
                    r_dic[stk + '_res'] = pool.apply_async(GenPic.gen_hour_index_pic_local,
                                                                 (r_dic[stk + '_d'], stk, save_dir + file_name))
                elif kind is 'd':
                    r_dic[stk + '_res'] = pool.apply_async(GenPic.gen_day_pic_local,
                                                                 (r_dic[stk + '_d'], stk, save_dir + file_name))
                elif kind is 'wm':
                    r_dic[stk + '_res'] = pool.apply_async(GenPic.gen_w_m_macd_pic_local,
                                                                 (r_dic[stk + '_d'], stk, save_dir + file_name))
                elif kind is 'd_idx':
                    r_dic[stk + '_res'] = pool.apply_async(GenPic.gen_idx_pic_local,
                                                                 (r_dic[stk + '_d'], stk, save_dir + file_name))

            except Exception as e_:
                self.log = self.log + '函数 gen_stk_list_kind_pic：\n%s\n' % str(e_)
                print('函数 gen_stk_list_kind_pic：\n%s\n' % str(e_))

            # 在字典中保存图片路径
            r_dic[stk + '_url'] = save_dir + file_name

        return r_dic


class GenPicPdf:
    def __init__(self, stk_list, process, save_dir):
        self.save_dir = save_dir
        self.pool = multiprocessing.Pool(process)
        self.stk_list = stk_list

    def gen_local_pic(self):
        g = GenListPic(self.stk_list, self.pool, self.save_dir)

        r = g.update_all_pic()

        # 总结图片路径
        pic_url = {}
        for stk in self.stk_list:
            pic_url[stk] = {
                'd': r[1]['d'][stk + '_url'],
                'd_idx': r[1]['d_idx'][stk + '_url'],
                'wm': r[1]['wm'][stk + '_url'],
                'h': r[0]['h'][stk + '_url'],
                'h_idx': r[0]['h_idx'][stk + '_url']
            }

        return pic_url


if __name__ == '__main__':
    # jq_login()
    # GenPic.gen_hour_macd_pic_local(
    #     (GenPic.down_minute_data('300183', '30m'), GenPic.down_minute_data('300183', '60m')),
    #     '300183', save_dir='C:/Users\paul\Desktop\新建文件夹 (2)/')

    pool = multiprocessing.Pool(4)
    stk_list = ['300183', '000001', '603421']
    g = GenListPic(stk_list, pool, 'C:/Users\paul\Desktop\新建文件夹 (2)/')
    r = g.update_all_pic()
    print(g.log)

    # 总结图片路径
    pic_url = {}
    for stk in stk_list:
        pic_url[stk] = {
            'd': r[1]['d'][stk+'_url'],
            'd_idx': r[1]['d_idx'][stk + '_url'],
            'wm': r[1]['wm'][stk + '_url'],
            'h': r[0]['h'][stk + '_url'],
            'h_idx': r[0]['h_idx'][stk + '_url']
        }

    end = 0