# encoding = utf-8

from sdk.SDKHeader import *

today_all = ts.get_today_all()

df_sort = today_all.sort_values(by='changepercent',ascending=False).head(100)

save_dir = "F:/MYAI/文档资料/用于读取的文件/金牛" + get_current_date_str() + "/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


fig, ax = plt.subplots(nrows=3, ncols=3,figsize=(13.6,7.68))

for index in df_sort.index:
    code = df_sort.loc[index,'code']
    name = df_sort.loc[index,'name']

    if is_table_exist(conn_k,stk_k_data_db_name,'k'+code):
        plot_part_ave(
            length=60,
            stk_code=code,
            save_dir=save_dir,
            ax=ax,
            today_all=today_all,
            title_note=name,
            index_list=[])

        print("完成金牛 " + name + " 的均线趋势图！")