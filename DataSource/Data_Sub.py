# encoding=utf-8

"""
与数据源相关的一些子函数
"""
import jqdatasdk
import tushare as ts
from SDK.MyTimeOPT import get_current_date_str
import jqdatasdk as jq


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


def get_k_data_JQ(stk_code, count=None, start_date=None, end_date=get_current_date_str(), freq='daily'):
    """
    使用JQData来下载stk的历史数据
    :param stk_code:
    :param amount:
    :return:
    """
    if stk_code in ['sh', 'sz', 'cyb']:

        stk_code_normal = {
            'sh': '000001.XSHG',
            'sz': '399001.XSHE',
            'cyb': '399006.XSHE'
        }[stk_code]
        df = jqdatasdk.get_price(stk_code_normal, frequency=freq, count=count, start_date=start_date,
                                 end_date=end_date)
    else:
        df = jqdatasdk.get_price(jqdatasdk.normalize_code(stk_code), frequency=freq, count=count,
                                 end_date=end_date, start_date=start_date)

    df['datetime'] = df.index
    df['date'] = df.apply(lambda x: str(x['datetime'])[:10], axis=1)

    return df


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