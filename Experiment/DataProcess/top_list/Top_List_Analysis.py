# encoding = utf-8

from sdk.SDKHeader import *

top_df = ts.top_list('2018-01-11')

grouped_df = list(top_df.groupby(by="reason"))