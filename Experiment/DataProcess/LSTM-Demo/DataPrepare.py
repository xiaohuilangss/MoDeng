# encoding = utf-8

from SDK.SDKHeader import *

predict_depth = timestep_size = 20
batch_size = 20


# 下载测试数据
df= get_total_table_data(conn_k,'k300508').sort_values(by='date',ascending=True)

# 添加MACD信息
df_MACD = get_MACD(df)

# 添加所属盘的MACD信息
df_belong_MACD = get_MACD(get_total_table_data(conn_k,'kcyb').sort_values(by='date',ascending=True)).rename(columns={'MACD':'belong_MACD','volume':'belong_volume','close':'belong_close'})


df_MACD_concat = pd.concat([df_MACD.set_index(keys='date'),df_belong_MACD.set_index(keys='date').loc[:,['belong_MACD','belong_volume','belong_close']]],axis=1).dropna(axis=0)


# 精简列,并时间降序，用以
df_MACD = df_MACD.loc[:,['close','date','MACD']].sort_values(by='date',ascending=False)

# 增加未来预测天数内天最大值
df_MACD['close_max_' + str(predict_depth)] = df_MACD.close.rolling(window=predict_depth).max()

# 计算“当前值”与“未来10天最大值”之间的变化幅度
df_MACD['inc_ratio_' + str(predict_depth)] = df_MACD.apply(lambda x:(x['close_max_' + str(predict_depth)] - x['close'])/(x['close'] + 0.000000000000001),axis=1)

# 去除存在控制的行
df_MACD = df_MACD.dropna(axis=0)

# 恢复为时间升序
df_MACD = df_MACD.sort_values(by='date',ascending=True)

# 组成学习样本list
example_list = []
for id in df_MACD.loc[predict_depth:,:].index:
    example_list.append(
        np.array([np.array(df_MACD.loc[id-predict_depth:id-1,'MACD']),
         np.array(df_MACD.loc[id - predict_depth: id-1, 'inc_ratio_' + str(predict_depth)])])
    )

# 组成batch
batch_list = []
for i in range(0,len(example_list),batch_size):
    feature = list(map(lambda x:x[0],example_list[i:i+batch_size]))
    label = list(map(lambda x:x[1],example_list[i:i+batch_size]))
    batch_list.append([feature,label])

end = 0
