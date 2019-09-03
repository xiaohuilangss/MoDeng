# encoding=utf-8
from SDK.SDKHeader import *
from DataProcess.Av_Trend_Analysis.PreProcessor import *
from DataProcess.Av_Trend_Analysis.Gen_Graph import *
import os

# date_now = get_current_date_str()
#
# while get_current_datetime_str()[11:] < '22:30:00':
#     time.sleep(1200)
#
# today_all_Flag = False
# while not today_all_Flag:
#     try:
today_all = ts.get_today_all()
#         today_all_Flag = True
#     except:
#         time.sleep(6)
#
# while (get_current_datetime_str()[11:] < '05:30:00')\
#         |\
#     (get_current_date_str() == date_now):
#     time.sleep(1200)
#
#
index_list = get_class_df()
#
# # --------------------------- 更新kdata ----------------------------------------
# update_K_data()
# conn_k.commit()
#
# # --------------------------- 我关心的 -----------------------------------------

code_list_concerned = [
    ('000001',U"平安银行"),
    # ("000625",U"长安汽车"),
    # ("000725",U"京东方"),
    # ("300508",U"东软载波"),
    # ("601989",U"中国重工"),
    # ("000333",U"美的集团"),
    # ("002456",U"欧菲科技"),
    # ("000063",U"中兴通讯"),
    # ("600606",U"绿地控股"),
    # ("600030",U"中信证券"),
    # ('000721',U"西安饮食"),
    # ('002192',U"融捷股份"),
    # ('300369',U"绿盟科技"),
    # ('600567',U"山鹰纸业"),
    # ('600754',U"锦江股份"),
    # ('002012',U'凯恩股份'),
    # ('000898',U'鞍钢股份'),
    # ('002124',U'天邦股份'),
    # ('002256',U'兆新股份'),
    # ('300042',U'朗科科技'),
    # ('600188',U'兖州煤业'),
    ('600212', U'江泉实业')

]


# ------------------------------- 将自己关注的stk生成图 --------------------------------------

save_dir = "F:/MYAI/文档资料/用于读取的文件/" + get_current_date_str() + "数据/" +'我所关心/'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

fig, ax = plt.subplots(nrows=3, ncols=3,figsize=(13.6,7.68))

for code in code_list_concerned:
    plot_part_ave(
        length=60,
        stk_code=code[0],
        save_dir=save_dir,
        ax=ax,
        today_all=today_all,
        title_note='ave'+code[1],
        index_list=index_list)

    print("完成我关心的 "+code[1] + " 的均线趋势图！")




# ------------------------------- 从图片中提取code --------------------------------------

read_dir = "F:/MYAI/文档资料/用于读取的文件/感兴趣/"
file_list = eachFile(read_dir)
code_list = list(map(lambda x:x.split('/')[-1][0:6],file_list))


# ------------------------------- 将手动筛选的stk生成图 --------------------------------------

# save_dir = "F:/MYAI/文档资料/用于读取的文件/感兴趣-详细/"

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for code in code_list:
    name = g_total_stk_info_mysql[g_total_stk_info_mysql.code == code]['name'].values[0]
    plot_part_ave(
        length=60,
        stk_code=code,
        save_dir=save_dir,
        ax=ax,
        today_all=today_all,
        title_note=name,
        index_list=[])

    print("完成我感兴趣的 " + name + " 的详细信息图！")

# ------------------------------- 将牛的stk生成图 --------------------------------------

df_sort = today_all.sort_values(by='changepercent',ascending=False).head(100)

save_dir = "F:/MYAI/文档资料/用于读取的文件/金牛" + get_current_date_str() + "/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

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



# ------------------------------- 完成行业形势图 --------------------------------------

save_dir = "F:/MYAI/文档资料/用于读取的文件/" + get_current_date_str() +"数据/" + '行业走势/'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

date_start = add_date_str(get_current_date_str(),-120)
date_end = get_current_date_str()

industry_data_list = cal_industry_index(date_start,date_end)

for ids in industry_data_list:
    c_name = ids['c_name']

    c_data = ids['c_data']
    if len(c_data) > 0:
        ids_gen_figure(c_name,c_data,save_dir)
    else:
        print('行业'+c_name+' 没有数据，无法打印走势图！')


# --------------------------------- 趋势图生成 ------------------------------------

# gen_trend_csv()
# gen_trend_graph()

# --------------------------------- 板块图生成 ------------------------------------

save_dir = "F:/MYAI/文档资料/用于读取的文件/"+ get_current_date_str() + "数据/" +'各盘趋势/'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

save_bk_graph("cyb", 60, save_dir+"创业板")
save_bk_graph("sh", 60, save_dir + "上证")
save_bk_graph("sz", 60, save_dir + "深成指")
save_bk_graph("sz50", 60, save_dir + "上证50")
save_bk_graph("hs300", 60, save_dir + "沪深300")
save_bk_graph("zxb", 60, save_dir + "中小板")


# 关机
os.system('shutdown -s -f -t 120')







































# for code in g_total_stk_code[300:600]:
#     if not os.path.exists(save_dir+code+'ave'+code+'.png'):
#         plot_part_ave(length=60,
#                       stk_code=code,
#                       today_all=today_all,
#                       save_dir=save_dir,
#                       ax=ax,
#                       title_note='ave'+code,
#                       index_list=index_list)
#         print("完成stk "+code + " 的均线趋势图！")


# for code in g_total_stk_code[600:900]:
#     if not os.path.exists(save_dir+code+'ave'+code+'.png'):
#         plot_part_ave(length=60,
#                       stk_code=code,
#                       today_all=today_all,
#                       save_dir=save_dir,
#                       ax=ax,
#                       title_note='ave'+code,
#                       index_list=index_list)
#         print("完成stk "+code + " 的均线趋势图！")
#
# gc.collect()

# for code in g_total_stk_code[900:1200]:
#     if not os.path.exists(save_dir+code+'ave'+code+'.png'):
#         plot_part_ave(length=60,
#                       stk_code=code,
#                       today_all=today_all,
#                       save_dir=save_dir,
#                       ax=ax,
#                       title_note='ave'+code,
#                       index_list=index_list)
#         print("完成stk "+code + " 的均线趋势图！")

# gc.collect()

# for code in g_total_stk_code[1200:1500]:
#     if not os.path.exists(save_dir+code+'ave'+code+'.png'):
#         plot_part_ave(length=60,
#                       stk_code=code,
#                       today_all=today_all,
#                       save_dir=save_dir,
#                       ax=ax,
#                       title_note='ave'+code,
#                       index_list=index_list)
#         print("完成stk "+code + " 的均线趋势图！")


# plt.clf()
# plt.close('all')


