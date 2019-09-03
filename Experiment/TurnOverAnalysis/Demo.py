# encoding=utf-8

"""


"""
import tushare as ts

from RelativeRank.Sub import relativeRank

df = ts.get_k_data('300508').tail(90)

df['c_rank'] = df.apply(lambda x: relativeRank(df['close'], x['close']), axis=1)

"""
df.plot('date', ['close', 'c_rank'], subplots=True)
"""
end=0