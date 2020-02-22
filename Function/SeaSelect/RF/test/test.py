# encoding=utf-8

import tushare as ts
import talib

from DataSource.Data_Sub import Index

stk_code = '300183'

df = ts.get_k_data(stk_code)

idx = Index(df)
# idx.add_adosc()
idx.add_obv()

df = idx.stk_df

df.plot('date', ['close', 'OBV'], subplots=True)
