# encoding = utf-8

from SDK.SDKHeader import *

"""
本文件将原始的basic信息保存到csv文件中
"""

save_dir_origin = "F:/MYAI/文档资料/用于读取的文件/BasicData/"
if not os.path.exists(save_dir_origin):
    os.makedirs(save_dir_origin)



for stk in g_total_stk_code:

    # 如果csv文件已经存在
    if os.path.exists(save_dir_origin+"basicData"+stk+".csv"):

        with open(save_dir_origin+"basicData"+stk+".csv") as f:
            origin_basic_data = pd.read_csv(f,index_col="index")

        # 获取文件中最近的季度，与当前季度比较
        quarter_now = int(get_quarter_date())
        quarter_record = origin_basic_data.index.sort_values(ascending=False)[0]

        if ((quarter_now  - quarter_record) == 2) |  ((quarter_now  - quarter_record) == 98):

            # 为了简单，只下载一个季度的就好了
            if quarter_record%10 == 4:
                quarter_now_df = get_ss_sq_total_basic(stk,str(quarter_record + 97))
            else :
                quarter_now_df = get_ss_sq_total_basic(stk, str(quarter_record + 1))


            # 将本季度的basic信息添加到原有的信息中
            if len(quarter_now_df):
                origin_basic_data = pd.concat(origin_basic_data,quarter_now_df)
                origin_basic_data.to_csv(save_dir_origin + "basicData" + stk + ".csv")
                print("更新" + stk + "的" + str(quarter_record) + "下一个季度的信息成功！")
            else:
                print("更新" + stk + "的" + str(quarter_record) + "下一个季度的信息时失败，该季度数据为空！")
        else:
            print(stk + "的basic信息的csv已经存在，且为最新数据！")

    # 如果csv文件不存在
    else:
        print(stk + "的basic信息的csv文件不存在，从头下载！")

        # 获取单个stk的basic值，以季度为时间轴
        single_stk_df = get_ss_total_basic(stk)
        single_stk_df = single_stk_df.set_index("index")


        single_stk_df.to_csv(save_dir_origin+"basicData"+stk+".csv")



