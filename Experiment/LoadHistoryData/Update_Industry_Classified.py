# encoding = utf-8
from sdk.SDKHeader import *

"""
用来更新“行业分类”

为了避开“行业指数”计算中的“新股发行”的问题，行业分类轻易不更新，暂定半年一更新便可。

"""

df_industry = ts.get_industry_classified()

df_industry.to_sql(con=engine_industry, name='industry_info', if_exists='replace',  index=False)