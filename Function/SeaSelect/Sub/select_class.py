# encoding=utf-8

"""
海选使用的类
"""
import calendar
import math
import talib
import pandas as pd
import numpy as np
import time
import tushare as ts
import wx

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login
from Function.GUI.Sub.sub import text_append_color
from Function.SeaSelect.Sub.reportlab_sub import add_front, print_k_to_pdf, add_tail_page, SeaSelectPdf
from Function.SeaSelect.Sub.select_cmd_class import SelectCmd
from Function.SeaSelect.gen_pic import gen_stk_sea_select_pic
from SDK.MyTimeOPT import add_date_str, get_current_date_str
from itertools import groupby

from SDK.TimeAndSeconds import minute_reckon


class SeaSelect:
    """
    海选的一些底层子函数的实现类
    """
    def __init__(self, stk_code):

        self.stk_code = stk_code

        self.hour_data = None
        self.day_data = None
        self.week_data = None
        self.month_data = None

        self.age = None
        self.cp = None

        self.close_rank = None

        # 通用变量，便于后续功能扩展之用！
        self.general_variable = None

        self.format_k_kind = {
            '半小时线': 'h',
            '周线': 'w',
            '月线': 'm',
            '日线': 'd'
        }

    def k_kind_format(self, k_kind):
        """
        将“半小时线”翻译成'h'等...
        :param k_kind:
        :return:
        """
        return self.format_k_kind.get(k_kind, k_kind)

    @staticmethod
    def down_basic():
        """
        从tushare中下载股票基本数据
        :return:
        """
        df = ts.get_stock_basics().reset_index()
        return dict(df.loc[:, ['code', 'timeToMarket']].to_dict(orient='split')['data'])

    def cal_age(self, code2timeToMarket):
        self.age = int(get_current_date_str()[:4]) - int(str(code2timeToMarket[self.stk_code])[:4])

    def data(self, kind):
        if kind == 'd':
            return self.day_data
        elif kind == 'h':
            return self.hour_data
        elif kind == 'w':
            return self.week_data
        elif kind == 'm':
            return self.month_data

    @staticmethod
    def down_today():
        """
        从tushare中下载当日数据
        :return:
        """
        df_today = ts.get_today_all()
        return dict(df_today.loc[:, ['code', 'changepercent']].to_dict(orient='split')['data'])

    def get_cp(self, ts_today_dict):
        try:
            self.cp = ts_today_dict[self.stk_code]
        except Exception as e_:
            print('类SeaSelect：股票'+self.stk_code + '计算当日涨跌幅出错！原因：\n' + str(e_))

    def down_hour_data(self):
        self.hour_data = get_k_data_JQ(self.stk_code, count=120,
                              end_date=add_date_str(get_current_date_str(), 1), freq='30m')

    def down_day_data(self):
        self.day_data = get_k_data_JQ(self.stk_code, count=400)

    def add_sar(self, kind):
        """
        向df中增加sar指标
        :param kind:
        :return:
        """
        kind = self.k_kind_format(kind)
        self.data(kind)['SAR'] = talib.SAR(self.data(kind).high, self.data(kind).low, acceleration=0.05, maximum=0.2)

    def add_macd(self, kind):
        kind = self.k_kind_format(kind)
        self.data(kind)['MACD'], self.data(kind)['MACDsignal'], self.data(kind)['MACDhist'] = talib.MACD(
            self.data(kind).close,
            fastperiod=6, slowperiod=12,
            signalperiod=9)

    def add_week_month_data(self):
        """
        给定日线数据，计算周线/月线指标！
        :return:
        """

        df = self.day_data

        if len(df) < 350:
            print('函数week_MACD_stray_judge：' + self.stk_code + '数据不足！')
            return False, pd.DataFrame()

        # 规整
        df_floor = df.tail(math.floor(len(df) / 20) * 20 - 19)

        # 增加每周的星期几
        df_floor['day'] = df_floor.apply(
            lambda x: calendar.weekday(int(x['date'].split('-')[0]), int(x['date'].split('-')[1]),
                                       int(x['date'].split('-')[2])), axis=1)

        # 隔着5个取一个
        if df_floor.tail(1)['day'].values[0] != 4:
            df_week = pd.concat([df_floor[df_floor.day == 4], df_floor.tail(1)], axis=0)
        else:
            df_week = df_floor[df_floor.day == 4]

        # 隔着20个取一个（月线）
        df_month = df_floor.loc[::20, :]

        self.week_data = df_week
        self.month_data = df_month

    def add_rsi(self, kind, span):
        kind = self.k_kind_format(kind)
        df = self.data(kind)
        rsi_str = 'RSI' + str(span)
        df[rsi_str] = talib.RSI(df.close, timeperiod=span)

    def judge_rsi_sub(self, kind, span, threshold):
        """
        根据rsi来筛选股票
        :param kind:
        :param span: 5， 12， 30三种选择
        :param threshold:[0.1, 0.3]  rsi所在区间
        :return:
        """
        kind = self.k_kind_format(kind)
        try:
            # 增加rsi指数
            rsi_str = 'RSI' + str(span)
            self.add_rsi(kind, span)

            df = self.data(kind)

            # 判断是否符合标准
            rsi_now = df.tail(1)[rsi_str].values[0]
            if (rsi_now >= threshold[0]) & (rsi_now <= threshold[1]):
                return True
            else:
                return False
        except Exception as e:
            print('函数judge_rsi_sub：出错！\n' + str(e))
            return False

    def sar_stray_judge_sub(self, kind):
        """
        判断sar的反转情况，返回三种值
        -1, 0， 1
        -1：向下反转
        0：未反转
        1：向上反转（后续上涨）
        :return:
        """
        kind = self.k_kind_format(kind)
        df = self.data(kind)

        try:
            df_tail = df.tail(2).reset_index()

            if (df_tail.loc[1, 'SAR'] >= df_tail.loc[1, 'close']) & (df_tail.loc[0, 'SAR'] <= df_tail.loc[0, 'close']):
                return -1
            elif (df_tail.loc[1, 'SAR'] <= df_tail.loc[1, 'close']) & (
                    df_tail.loc[0, 'SAR'] >= df_tail.loc[0, 'close']):
                return 1
            else:
                return 0
        except Exception as e:
            print('sar反转判断失败，原因：\n' + str(e))
            return 0

    def macd_stray_judge(self, kind):

        """
        对macd反转进行判断
        :return:
        """

        kind = self.k_kind_format(kind)

        # 判断背离
        self.add_macd(kind)

        macd_week = self.data(kind).tail(3)['MACD'].values
        if macd_week[1] == np.min(macd_week):
            return True
        else:
            return False

    def cal_close_rank(self, kind, amount):
        """
        计算一个序列数据，最后一个数在当前序列中的水平
        :param amount:
        :param kind:
        :return:
        """
        kind = self.k_kind_format(kind)

        c = np.array(self.data(kind).tail(np.min([len(self.data(kind)), int(amount)]))['close'])
        self.close_rank = list((c - np.min(c)) / (np.max(c) - np.min(c)))[-1]


class ExecuteSelectRole:
    """
    主要包含执行保存在json文件中的海选规则的函数，响应灯神中的执行海选命令
    """
    def __init__(self):

        # 加载海选的命令行及规则编辑类
        self.select_cmd = SelectCmd()
        self.rule = self.select_cmd.config

        # 数据填充标志位
        self.day_data_enable = False
        self.week_month_data_enable = False
        self.half_hour_enable = False
        self.age_enable = False

        self.stk_list_ss = []

        self.k_kind_str = {
            'd': '日线',
            'w': '周线',
            'm': '月线',
            'h': '半小时线'
        }
        self.df_basic = pd.DataFrame()
        self.init_stk_data()

        self.format_k_kind = {
            '半小时线': 'h',
            '周线': 'w',
            '月线': 'm',
            '日线': 'd'
        }

    def k_kind_format(self, k_kind):
        """
        将“半小时线”翻译成'h'等...
        :param k_kind:
        :return:
        """
        return self.format_k_kind.get(k_kind, k_kind)

    def get_filter_result(self):
        """
        获取当前 self.stk_list_ss
        :return:
        """
        if len(self.stk_list_ss) == 0:
            return '\n已无符合条件的标的！\n'
        else:
            return '\n' + str([(x.stk_code, code2name(x.stk_code)) for x in self.stk_list_ss]) + '\n'

    def init_stk_data(self):
        """
        初始化股票池
        :return:
        """
        try:
            # 下载基础数据
            self.df_basic = SeaSelect.down_basic()

            # 创建全部股票对象
            stk_list = list(self.df_basic.keys())
            self.stk_list_ss = [SeaSelect(x) for x in stk_list]
            return '股票池初始化成功！'

        except Exception as e_:
            str_ = '股票池初始化失败，原因：\n%s' % str(e_)
            return str_

    def data_prepare(self, k_kind, tc):
        """
        根据k线类型检查下载数据
        :param k_kind:
        :return:
        """
        t_s = time.time()
        text_append_color(tc, '\n开始准备 %s 数据！\n' % k_kind)
        k_kind = self.k_kind_format(k_kind)
        if (k_kind == 'd') | (k_kind == '日线'):

            # 增加日线数据
            if not self.day_data_enable:
                _ = [x.down_day_data() for x in self.stk_list_ss]

                # 过滤掉空值
                self.stk_list_ss = list(filter(lambda x: not x.day_data.empty, self.stk_list_ss))

                self.day_data_enable = True

                text_append_color(tc, '\n%s 数据准备完成！总共耗时%s分钟\n' % (k_kind, minute_reckon(t_s)))
                return '数据准备完毕！'

        elif (k_kind == 'w') | (k_kind == 'm') | (k_kind == '周线') | (k_kind == '月线'):

            # 增加日线数据
            if not self.day_data_enable:
                _ = [x.down_day_data() for x in self.stk_list_ss]

                # 过滤掉空值
                self.stk_list_ss = list(filter(lambda x: not x.day_data.empty, self.stk_list_ss))

                self.day_data_enable = True

            # 增加周/月线数据
            if not self.week_month_data_enable:
                _ = [x.add_week_month_data() for x in self.stk_list_ss]
                self.week_month_data_enable = True

        elif (k_kind == 'h') | (k_kind == '半小时线'):

            # 增加半小时数据
            if not self.half_hour_enable:
                _ = [x.down_hour_data() for x in self.stk_list_ss]
                self.half_hour_enable = True

    def filter_by_macd_stray(self, k_kind, tc):
        """
        应用macd反转规则
        :return:
        """
        try:
            # 准备数据
            self.data_prepare(k_kind, tc)

            # 根据周线反转过滤股票池
            self.stk_list_ss = list(filter(lambda x: x.macd_stray_judge(k_kind), self.stk_list_ss))

            return '%s macd反转规则应用成功！' % self.k_kind_str.get(k_kind, k_kind)

        except Exception as e_:
            return '%s macd反转规则应用失败！原因：\n%s' % (self.k_kind_str.get(k_kind, '未知k线类型'), str(e_))

    def filter_by_sar_stray(self, k_kind, tc):
        """
        应用sar反转规则
        :return:
        """
        try:
            # 准备数据
            self.data_prepare(k_kind, tc)

            # 根据周线反转过滤股票池
            self.stk_list_ss = list(filter(lambda x: x.sar_stray_judge_sub(k_kind) == 1, self.stk_list_ss))

            return '%s sar反转规则应用成功！' % self.k_kind_str.get(k_kind, '未知k线类型')

        except Exception as e_:
            return '%s sar反转规则应用失败！原因：\n%s' % (self.k_kind_str.get(k_kind, '未知k线类型'), str(e_))

    def filter_by_rsi(self, k_kind, span, low, high, tc):
        """
        应用sar反转规则
        :return:
        """
        try:
            # 准备数据
            self.data_prepare(k_kind, tc)

            # 根据反转过滤股票池
            self.stk_list_ss = list(filter(lambda x: x.judge_rsi_sub(self, k_kind, span, [low, high]), self.stk_list_ss))

            return '%s rsi规则应用成功！' % self.k_kind_str.get(k_kind, '未知k线类型')

        except Exception as e_:
            return '%s rsi规则应用失败！原因：\n%s' % (self.k_kind_str.get(k_kind, '未知k线类型'), str(e_))

    def filter_by_age(self, age_low, age_high):
        """
        根据上市年龄筛选标的
        包含边界值
        :return:
        """

        # 准备上市公司的上市年龄数据
        if not self.age_enable:
            _ = [x.cal_age(self.df_basic) for x in self.stk_list_ss]

        # 应用上市年龄过滤规则
        self.stk_list_ss = list(filter(lambda x: (x.age >= float(age_low)) & (x.age <= float(age_high)), self.stk_list_ss))

        return '成功应用上市年龄筛选规则！'

    def filter_by_today_cp(self, cp_low, cp_high):
        """
        根据当日涨跌幅进行筛选
        :return:
        """

        # 下载当天涨跌幅
        df_today = SeaSelect.down_today()

        # 将涨跌幅数据存入通用变量中
        _ = [x.get_cp(df_today) for x in self.stk_list_ss]

        # 应用当日涨跌幅筛选规则
        self.stk_list_ss = list(filter(lambda x: not pd.isnull(x.cp), self.stk_list_ss))
        self.stk_list_ss = list(filter(lambda x: (x.cp >= float(cp_low)) & (x.cp <= float(cp_high)), self.stk_list_ss))

        return '应用当日涨跌幅筛选规则成功！'

    def filter_by_close_rank(self, k_kind, amount, rank_low, rank_high, tc):
        try:
            # 准备数据
            self.data_prepare(k_kind, tc)

            # 计算排名
            _ = [x.cal_close_rank(k_kind, amount) for x in self.stk_list_ss]

            # 根据排名进行过滤
            self.stk_list_ss = list(filter(lambda x: (float(x.close_rank) >= rank_low/100) & (float(x.close_rank) <= rank_high/100), self.stk_list_ss))

            return 'close_rank规则应用成功！'

        except Exception as e_:
            return 'close_rank规则应用失败！原因：\n%s' % str(e_)

    def sea_select(self, tc):
        """
        执行主函数
        :return:
        """

        # 判断规则是否为空！
        if len(self.rule['filter_rule']) == 0:
            text_append_color(tc, '尚未设置过滤规则！无法进行海选！\n')
            return

        # 判断是否设置的报告存放路径
        if self.rule['save_dir'] == '':
            text_append_color(tc, '尚未设置海选报告的存放路径，请在灯神中输入“规则-设置报告存放路径”来设置！')

        # 将规则转为dataframe
        rule_df = pd.DataFrame(self.rule['filter_rule'])

        # 根据优先级对规则进行执行
        rule_priority_group = list(rule_df.groupby(by='priority'))

        # 对优先级进行排序
        rule_list = sorted(rule_priority_group, key=lambda x: x[0], reverse=False)

        # 根据优先级执行筛选规则
        for rule_group_priority in rule_list:

            # 提取该优先级的规则df
            df_rule = rule_group_priority[1]

            for idx in df_rule.index:
                text_append_color(tc, '\n开始执行过滤规则 <%s> ...\n' % df_rule.loc[idx, 'describe'])
                text_append_color(tc, self.rule_execute(df_rule.loc[idx, 'kind'], df_rule.loc[idx, 'data'], tc))
                text_append_color(tc, '\n经过以上筛选后剩余的标的：\n' + self.get_filter_result())

        # 打印结果
        if len(self.stk_list_ss) == 0:
            text_append_color(tc, '没有满足所有海选规则的标的，不需要打印结果报告！')

        else:
            pdf_gen = SeaSelectPdf()

            # 生成图片
            text_append_color(tc, '\n开始打印pdf所需要的图片...\n')
            pdf_gen.gen_sea_select_pic(self.stk_list_ss)

            # 生成pdf
            text_append_color(tc, '\n开始生成最终的pdf报告...\n')
            pdf_gen.gen_pdf(self.stk_list_ss, self.rule['save_dir'] + '/')

            text_append_color(tc, '\n海选结果pdf已经打印，请在：\n' + str(self.rule['save_dir']) + '\n文件夹下查看！\n')

    def rule_execute(self, rule_kind, rule_data, tc):

        rule_ = rule_data

        if rule_kind == 'macd反转':
            r = self.filter_by_macd_stray(rule_['k_kind'], tc)

        elif rule_kind == 'sar反转':
            r = self.filter_by_sar_stray(rule_['k_kind'], tc)

        elif rule_kind == 'rsi':
            r = self.filter_by_rsi(rule_['k_kind'],
                                   float(rule_['rsi_p']),
                                   float(rule_['rsi_low']),
                                   float(rule_['rsi_high']), tc)

        elif rule_kind == '上市年龄':
            r = self.filter_by_age(rule_['age_low'], rule_['age_high'])

        elif rule_kind == 'close_rank':
            r = self.filter_by_close_rank(
                rule_['k_kind'],
                float(rule_['amount']),
                float(rule_['rank_low']),
                float(rule_['rank_high']), tc)

        elif rule_kind == '当日涨跌幅':
            r = self.filter_by_today_cp(rule_['cp_low'], rule_['cp_high'])

        else:
            r = '不识别的规则类型！'

        return r


if __name__ == '__main__':

    ec = ExecuteSelectRole()
    ec.sea_select('')

    jq_login()

    # 下载基础数据
    df_basic = SeaSelect.down_basic()

    # 下载当天涨跌幅
    df_today = SeaSelect.down_today()

    # 创建全部股票对象
    stk_list = list(df_basic.keys())
    stk_list_ss = [SeaSelect(x) for x in stk_list]

    # 填入年龄
    [x.cal_age(df_basic) for x in stk_list_ss]

    # 删除小于4岁的孩子
    stk_list_ss = list(filter(lambda x: x.age > 4, stk_list_ss))

    # 计算增长率
    # [x.get_cp(df_today) for x in stk_list_ss]

    # 过滤掉涨幅小于4%
    # stk_list_ss = list(filter(lambda x: not pd.isnull(x.cp), stk_list_ss))
    # stk_list_ss = list(filter(lambda x: x.cp > 0.04, stk_list_ss))

    # 获取day数据
    [x.down_day_data() for x in stk_list_ss]

    # 删除数据day数据为空的单位
    stk_list_ss = list(filter(lambda x: not x.day_data.empty, stk_list_ss))

    # 计算周月数据
    [x.add_week_month_data() for x in stk_list_ss]

    # 为周数据增加macd
    [x.add_macd('w') for x in stk_list_ss]

    # 判断周反转
    stk_list_ss = list(filter(lambda x: x.macd_stray_judge('w'), stk_list_ss))

    # 计算价格排名
    [x.cal_close_rank('d') for x in stk_list_ss]

    print(str([x.stk_code for x in stk_list_ss]))

    stk_list_ss = list(sorted(stk_list_ss, key=lambda x: x.close_rank))[:12]

    stk_list = [x.stk_code for x in stk_list_ss]
    print(str(stk_list))

    for stk in stk_list:

        # 将选定的股票的走势图打印到本地
        gen_stk_sea_select_pic(stk)

    print('开始生成pdf...')

    c = canvas.Canvas(U"魔灯海选" + get_current_date_str() + ".pdf", pagesize=letter)
    c = add_front(c, '魔灯每日股票海选结果' + get_current_date_str(), '本文档由免费开源的量化投资软件“魔灯”自动生成 末尾公众号内有软件介绍', pagesize=letter)
    for stk in stk_list:
        c = print_k_to_pdf(c, stk, get_current_date_str())
    c = add_tail_page(c)
    c.save()

    end = 0

