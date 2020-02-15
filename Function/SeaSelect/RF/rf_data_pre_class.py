# encoding=utf-8
import numpy as np
import math
from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df
from DataSource.auth_info import jq_login
from SDK.MyTimeOPT import add_date_str, get_current_date_str

"""
使用随机森林对股票进行预测
本文件存储“数据预处理”相关的类
"""


class StkData:
    """
    本类用来为“随机森林预测价格走势”算法提供“数据预处理”
    """
    def __init__(self, stk_code):

        self.stk_code = stk_code

        self.minute_data = None
        self.day_data = None
        self.week_data = None
        self.month_data = None

        # 通用变量，便于后续功能扩展之用！
        self.general_variable = None

    def down_minute_data(self, m, count=120):
        self.minute_data = get_k_data_JQ(self.stk_code, count=count,
                                         end_date=add_date_str(get_current_date_str(), 1), freq=str(m) + 'm')

    def down_day_data(self, count=400, start_date=None, end_date=None):
        self.day_data = get_k_data_JQ(self.stk_code, count=count, start_date=start_date, end_date=end_date)

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

    @staticmethod
    def normal(list_):
        """
        列表归一化
        :param list_:
        :return:
        """

        c = list_
        return list((c - np.min(c)) / (np.max(c) - np.min(c)))

    @staticmethod
    def cal_rank_sig(sig, total):
        total = np.array(total)
        return len(total[total <= sig]) / len(total) * 100

    @staticmethod
    def cal_rank(list_):
        """
        计算排名
        :return:[0, 100], 排名为0表示为这个序列中的最小值，排名为100表示为这个序列的最大值
        """

        return [StkData.cal_rank_sig(x, list_) for x in list_]


class DataProRF(StkData):
    """
    为随机森林模型提供“数据预处理”的类
    """
    def __init__(self, stk_code):
        super().__init__(stk_code)

        self.feature_col = ['MACD', 'MOM', 'SAR', 'RSI5', 'RSI12', 'RSI30', 'boll_width', 'kd_diff', 'slowd', 'slowk']
        self.feature_rank = [x + '_rank' for x in self.feature_col]
        self.feature_diff = [x + '_diff' for x in self.feature_rank]

        self.label_col = 'increase_rank'

    def add_day_index(self):
        """
        向日线数据中增加常用指标
        :return:
        """
        self.day_data = add_stk_index_to_df(self.day_data)
        # self.day_data = self.day_data.dropna(axis=0)

    def add_day_kd_diff(self):
        """
        向日线数据中增加kd的差值值
        :return:
        """
        self.day_data['kd_diff'] = self.day_data.apply(lambda x: (x['slowk'] - x['slowd']), axis=1)

    def add_day_boll_width(self):
        """
        向日线数据中增加布林线宽度值
        :return:
        """
        self.day_data['boll_width'] = self.day_data.apply(lambda x: x['upper']-x['lower'], axis=1)

    def add_day_rank_col(self, col_name):
        """
        对日线数据的某一个字段进行排名华
        :param col_name:
        :return:
        """
        self.day_data[col_name + '_rank'] = self.cal_rank(self.day_data[col_name])

    def add_day_rank(self, col_list):
        """
        对日线数据进行排名化
        :param col_list: ['MACD', 'MOM', 'SAR', 'RSI5', 'RSI12', 'RSI30', 'boll_width', 'kd_diff', 'slowd', 'slowk']
        :return:
        """

        for col_name in col_list:
            self.add_day_rank_col(col_name)

    def add_day_diff_col(self, col_name):
        """
        获取日线数据指定列前后两天的差值
        :return:
        """

        # 增加前后差值
        self.day_data[col_name + '_last'] = self.day_data[col_name].shift(1)
        self.day_data[col_name + '_diff'] = self.day_data.apply(lambda x: x[col_name] - x[col_name + '_last'], axis=1)

    def add_day_diff(self, col_list):
        """
        向日线数据中增加相应列的前后两天值之差
        :return:
        """

        for col in col_list:
            self.add_day_diff_col(col)

    def add_day_feature(self):
        """
        向日线数据中增加标签
        :return:
        """

        # 向日线数据中增加常用指标
        self.add_day_index()

        # 增加kd均值
        self.add_day_kd_diff()

        # 增加布林宽度
        self.add_day_boll_width()

        # 对指标进行rank化
        self.add_day_rank(self.feature_col)

        # 增加前后差值
        self.add_day_diff(self.feature_rank)

    def add_day_label(self):
        """
        向日线数据中增加“标签”数据,
        计算未来20日收盘价相较于当前的增长率，计算中位数
        :return:
        """

        def ratio_median(rb):
            """
            序列除以首值后，取中位数
            :param rb:
            :return:
            """
            c = rb.values
            return np.median(c/c[0])

        window = 20
        self.day_data['m_median_origin'] = self.day_data['close'].rolling(window=window).apply(ratio_median, raw=False)
        self.day_data['m_median'] = self.day_data['m_median_origin'].shift(-window)

        """
        self.day_data.loc[:, ['close', 'm_median_origin', 'm_median']]
        """

        self.add_day_rank_col('m_median')

        self.day_data['label'] = self.day_data.apply(lambda x: math.ceil(x['m_median_rank']/10), axis=1)

    def pro(self):
        """
        生成训练数据的主函数
        :return:
        """

        # 准备数据
        self.down_day_data()

        # 增加“特征”数据
        self.add_day_feature()

        # 增加“标签”数据
        self.add_day_label()

        # 删除空值
        self.day_data = self.day_data.dropna(axis=0)
        """
        self.day_data.plot('datetime', ['close', 'label', 'm_median'], subplots=True, style=['*--', '*--', '*--'])
        self.day_data.plot('datetime', self.feature_rank + self.feature_diff, subplots=True)
        """

        end = 0


if __name__ == '__main__':

    jq_login()
    data_pro_obj = DataProRF('300183')
    data_pro_obj.pro()

    end = 0