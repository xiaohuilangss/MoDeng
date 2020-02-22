# encoding=utf-8

"""
与数据源相关的一些子函数
"""
import jqdatasdk
import talib
import tushare as ts
import jqdatasdk as jq

from SDK.MyTimeOPT import get_current_date_str
from talib import MA_Type
import pandas as pd


def get_RT_price(stk_code, source='jq'):

    if source == 'jq':
        # 使用聚宽数据接口替代
        if stk_code in ['sh', 'sz', 'cyb']:
            stk_code_normal = {
                'sh': '000001.XSHG',
                'sz': '399001.XSHE',
                'cyb': '399006.XSHE'
            }[stk_code]

        else:
            stk_code_normal = jq.normalize_code(stk_code)

        current_price = float(
            jq.get_price(stk_code_normal, count=1, end_date=get_current_date_str())['close'].values[0])

    elif source == 'ts':
        # 获取实时价格
        current_price = float(ts.get_realtime_quotes(stk_code)['price'].values[0])

    return current_price


def get_current_price_JQ(stk_code):

    # 使用聚宽数据接口替代
    if stk_code in ['sh', 'sz', 'cyb']:
        stk_code_normal = {
            'sh': '000001.XSHG',
            'sz': '399001.XSHE',
            'cyb': '399006.XSHE'
        }[stk_code]

    else:
        stk_code_normal = jq.normalize_code(stk_code)

    current_price = float(jq.get_price(stk_code_normal, count=1, end_date=get_current_date_str())['close'].values[0])

    return current_price


def get_all_stk():
    """
    使用tushare获取所有数据列表
    :return:
    """
    df = ts.get_stock_basics()

    return list(df.index)


class Index:
    """
    指标计算类
    """
    def __init__(self, stk_df):
        self.stk_df = stk_df
        
    def add_cci(self, time_period):
        self.stk_df['cci' + str(time_period)] = talib.CCI(
            self.stk_df['high'].values,
            self.stk_df['low'].values,
            self.stk_df['close'].values,
            timeperiod=time_period)
        
    def add_rsi(self, time_period):
        self.stk_df['RSI' + str(time_period)] = talib.RSI(self.stk_df.close, timeperiod=time_period)

    def add_macd(self):
        self.stk_df['MACD'], self.stk_df['MACDsignal'], self.stk_df['MACDhist'] = talib.MACD(self.stk_df.close,
                                                                              fastperiod=12, slowperiod=26,
                                                                              signalperiod=9)

    def add_sar(self):
        self.stk_df['SAR'] = talib.SAR(self.stk_df.high, self.stk_df.low, acceleration=0.05, maximum=0.2)
        
    def add_mom(self, time_period=5):
        self.stk_df['MOM'] = talib.MOM(self.stk_df['close'], timeperiod=time_period)
        
    def add_boll(self):
        self.stk_df['upper'], self.stk_df['middle'], self.stk_df['lower'] = talib.BBANDS(self.stk_df['close'], matype=MA_Type.T3)
        
    def add_kd(self):
        self.stk_df['slowk'], self.stk_df['slowd'] = talib.STOCH(self.stk_df.high,
                                                                   self.stk_df.low,
                                                                   self.stk_df.close,
                                                                   fastk_period=9,
                                                                   slowk_period=3,
                                                                   slowk_matype=0,
                                                                   slowd_period=3,
                                                                   slowd_matype=0)
        
    def add_ad(self):
        self.stk_df['AD'] = talib.AD(self.stk_df.high, self.stk_df.low, self.stk_df.close, self.stk_df.volume)
        
    def add_adosc(self, fast_period=3, slow_period=10):
        self.stk_df['ADOSC'] = talib.ADOSC(self.stk_df.high, self.stk_df.low, self.stk_df.close, self.stk_df.volume, fastperiod=fast_period, slowperiod=slow_period)

    def add_obv(self):
        self.stk_df['OBV'] = talib.OBV(self.stk_df.close, self.stk_df.volume)
        
        
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


def get_k_data_JQ(stk, count=None, start_date=None, end_date=get_current_date_str(), freq='daily'):
    """
    使用JQData来下载stk的历史数据
    :param stk_code:
    :param amount:
    :return:
    """
    if pd.isnull(end_date):
        end_date = get_current_date_str()
    try:

        # 增加以兼容list的情况
        if isinstance(stk, list):
            stk_code = [jqdatasdk.normalize_code(x) for x in stk]

            df = jqdatasdk.get_price(stk_code, frequency=freq, count=count,
                                     end_date=end_date, start_date=start_date)

        elif stk in ['sh', 'sz', 'cyb', 'hs300', 'sz50', 'zz500']:
            stk_code_normal = JQMethod.get_index_jq_code(stk)
            df = jqdatasdk.get_price(stk_code_normal, frequency=freq, count=count, start_date=start_date,
                                     end_date=end_date)
        else:
            df = jqdatasdk.get_price(jqdatasdk.normalize_code(stk), frequency=freq, count=count,
                                     end_date=end_date, start_date=start_date)

        if df.empty:
            return df

        df['datetime'] = df.index
        df['date'] = df.apply(lambda x: str(x['datetime'])[:10], axis=1)

        return df
    except Exception as e:
        print('函数get_k_data_JQ：出错！错误详情：\n' + str(e))
        return pd.DataFrame()


def ts_code_normalize(code):
    """
    规整tushare 代码
    :return:
    """

    if code in ['sh', 'sz', 'cyb']:

        return {
            'sh': '000001.SH',
            'sz': '399001.SZ',
            'cyb': '399006.SZ'
        }[code]

    if code[0] == '6':
        code_normal = code+'.SH'
    else:
        code_normal = code+'.SZ'

    return code_normal


def my_pro_bar(stk_code, start, end=get_current_date_str(), adj='qfq', freq='D'):

    if stk_code in ['sh', 'sz', 'cyb']:
        df = ts.pro_bar(ts_code=ts_code_normalize(stk_code), asset='I', start_date=start, end_date=end, freq=freq)
    else:
        df = ts.pro_bar(ts_code=ts_code_normalize(stk_code), start_date=start, end_date=end, adj=adj, freq=freq)
    if freq == 'D':
        df = df.rename(columns={'trade_date': 'date'}).sort_values(by='date', ascending=True)
        df['date'] = df.apply(lambda x: x['date'][:4]+'-'+x['date'][4:6]+'-'+x['date'][6:], axis=1)
    elif 'min' in freq:
        df = df.rename(columns={'trade_time': 'time'}).sort_values(by='time', ascending=True)
    return df


class JQMethod:
    def __init__(self):
        pass

    @staticmethod
    def get_index_jq_code(index_str):
        """
        将 字符格式的指数转为聚宽代码
        :param index_str:
        :return:
        """
        index_str_2_jq_dict = {
            'sh': '000001.XSHG',
            'sz': '399001.XSHE',
            'cyb': '399006.XSHE',
            'zz500': '000905.XSHG',
            'hs300': '000300.XSHG',
            'sz50': '000016.XSHG'
        }

        return index_str_2_jq_dict.get(index_str, index_str)


if __name__ == '__main__':
    df = my_pro_bar('300183', start='2019-01-01')
    df.plot('date', ['close'])
    end = 0