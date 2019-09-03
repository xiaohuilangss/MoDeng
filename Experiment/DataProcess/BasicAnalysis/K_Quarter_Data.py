# encoding = utf-8


from SDK.SDKHeader import *
import os

# 获取行业所属证券类型
code_belongto_info = get_stk_belongto_info()

# 获取各个证券类型季度变换率
class_Q = get_class_Q_ratio()

# 获取行业分类信息
industry_info = get_total_table_data(conn=conn_industry, table_name='industry_info')


save_dir = "F:/MYAI/文档资料/用于读取的文件/BasicDataWithQInfo/"
read_dir = "F:/MYAI/文档资料/用于读取的文件/BasicData/"


if not os.path.exists(save_dir):
    os.makedirs(save_dir)


# 遍历stk -》 存在文件：
#                           读取csv为Df
#                           将季度增长率添加到df中
#                           将df存为另一个csv文件


for stk in g_total_stk_code:
    if (not os.path.exists(save_dir+"basicData_Q"+stk+".csv")) & os.path.exists(read_dir+"basicData"+stk+".csv") & is_table_exist(conn=conn_k,database_name=stk_k_data_db_name,table_name='k'+stk):

        with open(read_dir+"basicData"+stk+".csv") as f:
            origin_basic_data = pd.read_csv(f)

            # 将index 有int类型转为字符串类型
            for id in origin_basic_data.index:
                origin_basic_data.loc[id,'index'] = str(origin_basic_data.loc[id,'index'])

            # 设定索引
            origin_basic_data = origin_basic_data.set_index(keys='index')


        # 获取该stkK数据并增加“季度列”
        k_df_with_Q = add_quarter_to_df(get_total_table_data(conn=conn_k, table_name='k' + stk))

        # （添加一）根据K数据获取该stk的季度增长率
        quarter_ratio_df = get_quarter_growth_ratio_df(k_df_with_Q)

        # 季度减一
        quarter_ratio_df = quarter_ratio_df.reset_index()
        quarter_ratio_df['Q_minus'] = quarter_ratio_df.apply(lambda x:minus_quarter(x['quarter']),axis=1)

        # 设置索引
        quarter_ratio_df = quarter_ratio_df.loc[:,['Q_minus','quarter_ration']]\
                                        .set_index(keys='Q_minus')


        # （添加二）添加其所属板块的的增长率
        class_Q_ss = get_stk_classified_Q_ratio(class_Q, code_belongto_info, stk)
        class_Q_ss = class_Q_ss.reset_index()
        class_Q_ss['Q_minus'] = class_Q_ss.apply(lambda x:minus_quarter(x['quarter']), axis=1)
        class_Q_ss = class_Q_ss.loc[:, ['Q_minus', 'quarter_ration']].set_index(keys='Q_minus').rename(columns={'quarter_ration': 'quarter_ration_class'})

        # （添加三）添加该季度起始时的价格
        Q_start_price = get_quarter_start_price_df(k_df_with_Q)


        # 以季度为轴，将该stk的“基本信息”与“季度增长率”合并，并删除有nan的行！
        quarter_df_merged = pd.concat([Q_start_price,quarter_ratio_df, origin_basic_data, class_Q_ss], axis=1, join='inner').dropna(axis=0, how='any')


        if len(quarter_df_merged):

            # A、stk季度增长率 - 所属类季度增长率
            quarter_df_merged['Q_ratio_diff'] = quarter_df_merged.apply(lambda x:x['quarter_ration'] - x['quarter_ration_class'],axis=1)
            quarter_df_merged['stk_code'] = str(stk)

            # B、增加 pb 和 pe 和 每股净资产
            quarter_df_merged['bps'] = quarter_df_merged.apply(lambda x: (x['eps']/(x['roe']+0.0000000000001))*100, axis=1)
            quarter_df_merged['pe']  = quarter_df_merged.apply(lambda x: x['q_start_price']/(x['eps']+0.0000000000001), axis=1)
            quarter_df_merged['pb'] = quarter_df_merged.apply(lambda x: x['q_start_price'] /(x['bps']+0.0000000000001), axis=1)

            # C、增加stk证券类型
            quarter_df_merged['stk_class'] = quarter_df_merged.apply(lambda x: get_class_stk_belong(stk,code_belongto_info), axis=1)

            # D、保存为csv文件
            quarter_df_merged.to_csv(save_dir + "basicData_Q" + stk + ".csv", index=True, index_label='quarter')
        else:
            print(stk + "： 最终没有有效数据！")

    else:
        print("没有找到" + stk + "的含有basic信息的csv! 或者 数据库中没有其K数据！或者 想要的csv已经存在!")

