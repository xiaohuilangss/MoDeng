
# encoding = utf-8

from sdk.SDKHeader import *

# ------------------------------- 全局数据准备 --------------------------------------

today_all_Flag = False
while not today_all_Flag:
    try:
        today_all = ts.get_today_all()
        today_all_Flag = True
    except:
        time.sleep(6)

index_list = get_class_df()



# ------------------------------- 从图片中提取code --------------------------------------

read_dir = "F:/MYAI/文档资料/用于读取的文件/感兴趣/"
file_list = eachFile(read_dir)
code_list = list(map(lambda x:x.split('/')[-1][0:6],file_list))


# ------------------------------- 将自己关注的stk生成图 --------------------------------------

save_dir = "F:/MYAI/文档资料/用于读取的文件/感兴趣-详细/"

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

fig, ax = plt.subplots(nrows=3, ncols=2,figsize=(13.6,7.68))

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

