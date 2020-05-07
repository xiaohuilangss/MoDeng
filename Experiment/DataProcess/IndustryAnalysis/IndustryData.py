# encoding = utf-8
from sdk.SDKHeader import *


# insert_row_to_database(conn_param=conn_industry,field=['c_nmc','f1','f2'],value=['600','dafjoiewf','0.12586'],table_name='金融',db_name=stk_industry_data_db_name)


# 获取行业分类
industry_info = get_total_table_data(conn = conn_industry,table_name = 'industry_info')

# 获取当天stk情况
stk_total_today = ts.get_today_all()

# 文件存取路径
file_url = "F:/MYAI/文档资料/用于读取的文件/industry/"


# 行业与当天数据进行合并
m_df = pd.merge(stk_total_today, industry_info, on="code")

# 按行业进行分组
group_list = list(m_df.groupby(by="c_name"))


result = list()
for ids in group_list:

    c_name = ids[0]
    c_df = ids[1]

    # 获取行业当天变动均值
    c_change_mean = c_df.changepercent.mean()

    # 获取行业当天的流通总市值
    c_nmc_sum = c_df.nmc.sum()

    result.append({
        "c_name":c_name,
        "c_nmc_sum":c_nmc_sum,
        "date":get_current_date_str()
    })

# 遍历各个行业，将行业变换情况写入数据库
for ind in result:

    insert_row_to_database(conn_industry,ind)




# 将当天的数据备份
result.to_csv(file_url+"industry"+get_current_date_str()+".csv")

# 保存汇总数据
with open(file_url+"industryTotal.csv") as f:
    df_record = pd.read_csv(f)

