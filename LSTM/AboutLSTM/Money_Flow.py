# encoding=utf-8
from JQData_Test.auth_info import *
import numpy as np
import pandas as pd

"""

本脚本研究stk的资金出入量
"""


"""
接口用法：



字段名	                        含义	                备注
date	                        日期	
sec_code	                    stk代码	
change_pct	                    涨跌幅(%)	
net_amount_main	                主力净额(万)	        主力净额 = 超大单净额 + 大单净额
net_pct_main	                主力净占比(%)	        主力净占比 = 主力净额 / 成交额
net_amount_xl	                超大单净额(万)	        超大单：大于等于50万股或者100万元的成交单
net_pct_xl	                    超大单净占比(%)	        超大单净占比 = 超大单净额 / 成交额
net_amount_l	                大单净额(万)	        大单：大于等于10万股或者20万元且小于50万股或者100万元的成交单
net_pct_l	                    大单净占比(%)	        大单净占比 = 大单净额 / 成交额
net_amount_m	                中单净额(万)	        中单：大于等于2万股或者4万元且小于10万股或者20万元的成交单
net_pct_m	                    中单净占比(%)	        中单净占比 = 中单净额 / 成交额
net_amount_s	                小单净额(万)	        小单：小于2万股或者4万元的成交单
net_pct_s	                    小单净占比(%)	        小单净占比 = 小单净额 / 成交额
"""





df_m_f.plot('date', ['change_pct', 'net_amount_main'], subplots=True)

"""
plot语句

df_m_f.plot('date', ['change_pct', 'net_amount_main'], subplots=True)
"""

end = 0