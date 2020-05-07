# encoding = utf-8
from Config.GlobalSetting import *


def get_feature_for_case(case_dic,time_step):
    """

    :param case_dic:
    :param time_step:
    :return:

    函数功能：输入一个case，得到该case的feature数据
    case_dict的格式为
            # {"code":***,
            # "start":***,
            # "end":***,
            # "change_ratio":***,
            # "customer_end_index":***}
    """
    # 获取相应stk的k数据
    df_k = get_total_table_data(conn=conn_k,table_name="k"+case_dic["code"])

    case_start_index = df_k[df_k.date == case_dic["start"]].index.values[0]
    feature_start_index = case_start_index-time_step-1
    feature_end_index = case_start_index
    if feature_start_index >= 0:
        return df_k[feature_start_index:feature_end_index].to_json()
    else:
        return {}


"""
函数功能：向case中添加feature数据

@:parameter time_step               决定了搜集多少天的数据，10表示搜集该case发生前10天的数据
@:parameter case_csv_file case      文件路径
@:parameter result_file_url         结果文件存放位置

@:returns                           返回字典，格式如下：
                                        "ration":0.98,
                                        "front_data":list[???]
"""
def prepare_studyData_for_case(time_step,case_csv_file,result_file_url):

    # 从case文件中读取数据
    case_dict_list = read_csv_to_dict_list(case_csv_file)

    case_with_feature = []
    # 遍历整个case
    for case_dict in case_dict_list:
        feature = get_feature_for_case(case_dic=case_dict, time_step=time_step)
        feature_dict = {"feature":feature}
        case_dict.update(feature_dict)
        case_with_feature.append(case_dict)

    # 删除掉feature为空的样本
    json_str = list(filter(lambda x: len(x["feature"]) > 0, case_with_feature))

    # 获取json文件句柄
    with open(result_file_url,encoding="utf-8",mode="w") as f:

        # 将结果保存为json文件
        json.dump(obj=json_str,fp=f)


"""--------------------------------------以下是寻找case相关函数---------------------------------------------"""

'''
函数功能：后瞻,其返回的是后瞻得到的“极点”，找得到？找不到？找不到返回起始值就可以了，极值是起始值的可能性很小
函数traversal_customer的子函数

返回值的名字就叫：customer_value

@:parameter         bw_df_index_param    起始的后瞻索引
@:parameter         data_df_param        数据源
@:parameter         bw_ep_length_param   后瞻长度
@:parameter         ratio_increase_param 增势？减势？boolean

'''
def backward_explore(bw_df_index_param,data_df_param,bw_ep_length_param,ratio_increase_param):

    # 处理形参
    data_df = data_df_param
    backward_explore_length = bw_ep_length_param
    bw_ex_index = bw_df_index_param+1
    data_len = len(data_df_param)
    ratio_increase = ratio_increase_param
    customer_value = data_df_param.iloc[bw_df_index_param]
    bw_ex_extreme_point = customer_value
    bw_ex_extreme_index = bw_df_index_param
    # ~~~~调试打印
    if g_find_case_debug_enable:
        try:
            write_to_txt(file_url_param=g_debug_file_url + str(customer_value["code"]) + g_find_case_debug_file_name,
                         contents_param="：后瞻进入while之前：" +"\n"+
                                        "索引不能超过数据长度:"+str(bw_ex_index < data_len)+"\n"+
                         "后瞻数据不能低于客数据:"+str((((data_df.iloc[bw_ex_index]["close"] > customer_value["close"]) & ratio_increase) |
                             ((data_df.iloc[bw_ex_index]["close"] < customer_value["close"]) & (not ratio_increase))))+"\n"+
                         "不能超过后瞻距离:"+str(minus_date_str(data_df.iloc[bw_ex_index]["date"],
                                    bw_ex_extreme_point["date"]) <= backward_explore_length)+"\n\n"
                         )
        except:
            print("error")

    # while continue flag
    continue_flag = True

    #-------------------------正文--------------------------------------------------
    while continue_flag:
        # 在“增势”中：
        if ratio_increase:
            try:
                if data_df.iloc[bw_ex_index]["close"] > bw_ex_extreme_point["close"]:
                    bw_ex_extreme_point = data_df.iloc[bw_ex_index]
                    bw_ex_extreme_index = bw_ex_index
                    # ~~~~调试打印
                    if g_find_case_debug_enable:
                        write_to_txt(file_url_param=g_debug_file_url + str(customer_value["code"]) + g_find_case_debug_file_name,
                                     contents_param="当前处于增势，被后瞻对象大于当前极点，当前极点更新为："+"\n"+
                                     str(bw_ex_extreme_point)+"\n"
                                     )
            except:
                print("函数backward_explore：“增势”中出现错误！")

        # 在“减势”中：
        else:
            if data_df.iloc[bw_ex_index]["close"] < bw_ex_extreme_point["close"]:
                bw_ex_extreme_point = data_df.iloc[bw_ex_index]
                bw_ex_extreme_index = bw_ex_index
                # ~~~~调试打印
                if g_find_case_debug_enable:
                    write_to_txt(
                        file_url_param=g_debug_file_url + str(customer_value["code"]) + g_find_case_debug_file_name,
                        contents_param="当前处于减势，被后瞻对象小于当前极点，当前极点更新为：" +
                                       str(bw_ex_extreme_point)+"\n"
                        )

        # 索引自增
        bw_ex_index = bw_ex_index + 1

        # ~~~~调试打印
        if g_find_case_debug_enable:
            write_to_txt(
                file_url_param=g_debug_file_url + str(customer_value["code"]) + g_find_case_debug_file_name,
                contents_param="后瞻索引递增"+"\n\n")

        # 计算是否能够购继续while,之所以在这里判断，而不是先前的在while中进行判断，是因为在第一条不满足时，第三条索引的时候容易出错，python
        # 貌似在判断多个条件“与”的时候，判断一个条件不符合的时候，还继续判断其他的，所以需要这么做。
        # 三个条件满足任何一条都可以跳出while
        # 1、索引不能超过数据长度
        if not (bw_ex_index < data_len):
            continue_flag = False
        # 2、趋势递增时：后瞻数据的值不能低于客数据值；趋势递减时：后瞻数据不能高于客数据值（没有必要）
        # elif(not (((data_df.iloc[bw_ex_index]["close"] > customer_value["close"]) & ratio_increase) |
        #                  ((data_df.iloc[bw_ex_index]["close"] < customer_value["close"]) & (not ratio_increase)))):
        #     continue_flag = False
        # 3、不能超过后瞻距离(后瞻距离加上1是为了处理后瞻距离为1的特殊情况，当为1时，1<1不成立，所以会跳出，导致无法连续)
        # elif(not (minus_date_str(data_df.iloc[bw_ex_index]["date"],
        #                         bw_ex_extreme_point["date"]) < backward_explore_length+1)):
        #     continue_flag = False
        elif not (bw_ex_index-bw_ex_extreme_index) < backward_explore_length+1:
            continue_flag = False


    #-------------------------------------返回结果-------------------------------------
    return {"extreme_value":bw_ex_extreme_point,"extreme_index":bw_ex_index-1}

'''
遍历“客数据”
函数find_change_ratio_span的子函数

@:return
若找到案例，则返回案例信息：

'''
def master_process(index_param, data_df_param, ratio_param, backward_explore_ratio_param):

    #---------------------形参赋值------------------
    index = index_param
    data_df = data_df_param
    if ratio_param>0:
        ratio_increase = True
    else:
        ratio_increase = False

    data_len = len(data_df_param)
    backward_explore_ratio = backward_explore_ratio_param


    #---------------------正文----------------------
    # 主值有效标志位
    master_valid_flag = False

    # 赋值主客数据
    master_value = data_df.iloc[index]
    customer_value = None

    # 根据主数据遍历客数据,赋值只起到初始化的作用，随意一个值便可
    customer_end_index= index + 1

    # 遍历客数据
    for customer_index in list(range(index + 1,data_len,1)):

        # 获取客数据
        customer_value = data_df.iloc[customer_index]

        # 主客数据对比
        # 1、a客数据发展趋势不对，直接返回
        #    b、客数据在没有符合条件之前出现了低于或者高于主数据的情况，这意味着当前主数据是可以抛弃的
        if ((customer_value["close"] - master_value["close"] <0) & ratio_increase)\
            |\
            ((customer_value["close"] - master_value["close"] >0) & (not ratio_increase)):

                # ~~~~调试打印
                if g_find_case_debug_enable:
                    write_to_txt(file_url_param=g_debug_file_url+str(master_value["code"])+g_find_case_debug_file_name,
                                 contents_param="---------------------------------------------------------"+"\n"
                                                +"customer_value:"+"\n"
                                                +str(customer_value)+"\n"
                                                +"master_value"+"\n"
                                                +str(master_value)+"\n"
                                                +"increase:"
                                                +str(ratio_increase)+"\n"
                                                +"客数据不符合趋势要求!"+"\n\n")
                return {"customer_end_index":customer_index}

        # 2、如果客数据满足条件,客值继续往后延伸探索，在“后瞻率”的限制下，找到一个最高点
        #   a、上涨，涨幅大于设定值
        #   b、下跌，跌幅大于设定值
        elif(
                        ratio_increase & ((customer_value["close"] - master_value["close"])/customer_value["close"] > ratio_param)
                        |
                            (not ratio_increase) & ((customer_value["close"] - master_value["close"])/customer_value["close"] < ratio_param)
             ):
            # 获取当前的“案例”的时间跨度,将用索引跨度代替时间跨度来进行后瞻
            # case_span_now = minus_date_str(customer_value["date"],master_value["date"])
            case_span_now = customer_index - index

            # 获取后瞻距离加上1是为了防止后瞻距离为0的情况
            backward_explore_length = math.floor(case_span_now*backward_explore_ratio)+1

            # ~~~~调试打印
            if g_find_case_debug_enable:
                write_to_txt(file_url_param=g_debug_file_url + str(master_value["code"]) + g_find_case_debug_file_name,
                             contents_param="准备进入后瞻！\n "+
                             "当前主数据：" +
                             str(master_value)+"\n"+
                             "当前客数据:"+
                             str(customer_value)+"\n"+
                             "案例当前的时间跨度："+
                             str(case_span_now)+"\n"+
                             "当前允许的后瞻距离："+
                             str(backward_explore_length)+"\n\n")


            # 进行后瞻操作，若后瞻起始点是当前stk的终点，则不进行“后瞻”(返回经过后瞻后的最终极点)
            if (backward_explore_length > 0)&(customer_index<data_len-1):
                bw_return = backward_explore(bw_df_index_param=customer_index,data_df_param=data_df,bw_ep_length_param=backward_explore_length,ratio_increase_param=ratio_increase)
                customer_value = bw_return["extreme_value"]
                customer_end_index = bw_return["extreme_index"]
            else:
                # 保存结束时customer_index
                customer_end_index = customer_index

            # “案例有效标志位”置true
            master_valid_flag = True

            # 结束客数据的遍历
            break

        # 3、客数据继续递增
        else:
            # 保存结束时customer_index
            customer_end_index = customer_index
            continue


    # 客数据遍历完之后，根据“主数据是否有效标志位”来判断是否生成案例
    if master_valid_flag:
        return {"code":master_value["code"],
                "start":master_value["date"],
                "end":customer_value["date"],
                "change_ratio":(customer_value["close"]-master_value["close"])/master_value["close"],
                "customer_end_index":customer_end_index}
    else:
        return {"customer_end_index":customer_end_index}


'''
本程序用于筛选特定的case（案例），作为机器学习的学习数据

当前要筛选的case有：

1、找出一个stk其涨幅不低于30%（手动设置）的时间段
'''


'''
函数功能：找出变化率超过设定值的时间段
@:return 字典，{“time_start”：***，“time_end”：***，“code”：***,"ratio_final":***}
'''
def find_change_ratio_span(code_param, ratio_param, backward_explore_ratio):

    # 如果相应的表不存在，返回一个空的字典
    if not is_table_exist(conn_k,database_name=stk_k_data_db_name,table_name="k"+code_param):
        print("函数find_change_ratio_span：不存在表：k"+code_param)
        return {}

    # 获取相应的数据,去重、按时间升序排序、reset index
    data_df = get_total_table_data(conn=conn_k,table_name="k"+code_param)\
        .drop_duplicates()\
        .sort_values(by="date",ascending=True)\
        .reset_index(drop=True)

    # 测试代码,将原始数据打印到csv文件，用于测试
    if g_find_case_debug_enable:
        data_df.to_csv(g_debug_file_url+str(code_param)+".csv")

    # 定义返回值，list字典格式
    result = []

    master_index = 0

    while(master_index<len(data_df)-1):

        # 处理该主数据 返回字典格式：
        # {"code":***,
        # "start":***,
        # "end":***,
        # "change_ratio":***,
        # "customer_end_index":***}
        master_result = master_process(master_index, data_df, ratio_param, backward_explore_ratio)
        master_index = master_result["customer_end_index"]
        if len(master_result) > 1:
            result.append(master_result)

    # 主数据遍历完，返回结果
    return result

