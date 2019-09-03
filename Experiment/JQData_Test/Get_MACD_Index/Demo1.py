# encoding=utf-8

"""

测试获取聚宽的MACD指标
"""
from jqdatasdk.technical_analysis import MACD

from JQData_Test.auth_info import *


df = get_price('000001.XSHE', start_date='2015-01-01', end_date='2015-12-31', frequency='5d', fields=None, skip_paused=False, fq='pre')

end = 0