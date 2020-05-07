# encoding = utf-8

# 根据均线来找出相应趋势的stk

from sdk.SDKHeader import *


def gen_trend_csv():

    # 结果保存路径
    save_dir = "F:/MYAI/文档资料/用于读取的文件/av_trend_record/"


    # 获取所有stk的近期均线趋势
    result = list()
    ts = [14,30,60,180]

    for stk in g_total_stk_code:

        if is_table_exist(conn_k,stk_k_data_db_name,'k'+stk):

            result.append(get_ts_cov(stk, ts, 4))
            print(stk+'结果成功获得！')

    result_df = pd.DataFrame(result)


    # 将文件保存为csv
    result_df.to_csv(save_dir+'av_trend'+get_current_date_str()+'.csv')