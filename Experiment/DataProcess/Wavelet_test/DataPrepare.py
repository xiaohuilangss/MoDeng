# encoding = utf-8

from sdk.SDKHeader import *
import tushare as ts

# 全局变量

code = '300508'


# 获取该stk的历史数据
hist_stk = ts.get_hist_data(code)

# 获取所属大盘的历史数据
hist_class = ts.get_hist_data('cyb').rename(columns={'p_change':'class_p_change','volume':'class_volume'})

# 按日期进行合并
df_merge = pd.concat([hist_stk,hist_class],axis=1).loc[:,['p_change','class_p_change','volume','class_volume']]

#计算个股与大盘变化率之差
df_merge['p_diff'] = df_merge.apply(lambda x:x['p_change'] - x['class_p_change'],axis=1)

df_merge = df_merge.dropna(axis=0,how='any')


# 将成交量归一化
max_v = df_merge.volume.max()
min_v = df_merge.volume.min()

max_v_c = df_merge.class_volume.max()
min_v_c = df_merge.class_volume.min()

df_merge['v_std'] = df_merge.apply(lambda x:(x['volume']-min_v)/(max_v-min_v),axis=1)
df_merge['class_v_std'] = df_merge.apply(lambda x:(x['class_volume']-min_v_c)/(max_v_c-min_v_c),axis=1)


# 添加label（未来一段时间变化率之和）
df_merge = df_merge.reset_index().sort_values(by='index',ascending=True).to_csv('wavelet_test.csv')
    # .rename({'index':'date'})




end = 0



