# encoding = utf-8

from sdk.GeneralSub import read_csv_to_dict_list

from Config.GlobalSetting import *
from sdk.DBOpt import *

'''
给定一个case字典，将图形画出来，普通的时间段为蓝色，符合条件的时间段为红色
'''
def plot_case_k(case_dict_list):

    # 读取源数据
    total_data = get_total_table_data(conn=conn_k,table_name="k"+case_dict_list[0]["code"])


    # 获取该数据时间series，递增排序，起始时间段，字典格式{“start”：“2017-09-12”，“end”：“2017-11-09”}
    time_start_end = sorted(total_data.date,reverse=False)
    time_dict_start_end = {"start":time_start_end[0],"end":time_start_end[len(time_start_end)-1]}


    list_date = []
    list_date.append(time_dict_start_end["start"])
    for i in case_dict_list:
        list_date.append(i["start"])
        list_date.append(i["end"])

    list_date.append(time_dict_start_end["end"])


    # 组成时间段列表,字典列表格式，字典内部为：{“start”：起始时间，“end”：结束时间，“isCase”：是否为case}
    list_case_dateSpan = []
    for index in list(range(0,len(list_date)-1,1)):
        if index%2==0:
            isCase_flag = False
        else:
            isCase_flag = True
        list_case_dateSpan.append({"start":list_date[index],"end":list_date[index+1],"isCase":isCase_flag})


    # 画图
    # trick to get the axes
    fig, ax = plt.subplots()

    for case in list_case_dateSpan:

        # 获取本case的时间段，如果是需要的case，则前后都是闭区间，否则，前后都是开区间
        if case["isCase"]:

            # 获取本时间段的数据
            data_case_df = total_data[(total_data.date>=case["start"])&(total_data.date<=case["end"])]
            ax.plot(data_case_df["date"],data_case_df["close"],'r*--')

        else:
            # 获取本时间段的数据
            data_case_df = total_data[(total_data.date>case["start"])&(total_data.date<case["end"])]
            ax.plot(data_case_df["date"],data_case_df["close"],'b*--')

        # 画图、设置x轴
        plt.draw()
        plt.pause(0.3)

    # 最后设置x轴，如果连续设置，会导致后面覆盖前面
    xticklabels = list(map(lambda elem: str(elem)[2:10], total_data['date']))
    ax.set_xticklabels(xticklabels, rotation=90)
    # plt.xticks(xticklabels, rotation=90)
    # plt.legend(loc='best')



# ----------------------------正文------------------------------------

# 从csv文件中读取数据
case_dict_list = read_csv_to_dict_list(g_debug_file_url+"case_2017-11-08.csv")

# 根据code对数据进行分组，返回一个tuple——list的数据格式，tuple具体为：（代码，dataframe数据）
grouped_list = list(DataFrame(case_dict_list).groupby("code"))

# case_dict_list
case_test = grouped_list[1][1].to_dict(orient='records')
plot_case_k(case_test)

end = 0
