# encoding=utf-8
from Config.Sub import dict_stk_list
from DataSource.Data_Sub import get_k_data_JQ
from SDK.Gen_Stk_Pic_Sub import gen_Hour_MACD_Pic_wx, \
    gen_Day_Pic_wx, gen_W_M_MACD_Pic_wx, gen_Idx_Pic_wx
from pylab import *


def get_pic_dict():
    """
    获取图片字典
    :return:
    """
    # 判断结果list
    result_analysis_list = []

    pic_dict = {}
    for tab in dict_stk_list.keys():
        stk_list = dict_stk_list[tab]
        stk_list_pic_dict = {}

        for stk_info in stk_list:
            stk = stk_info[1]
            df = get_k_data_JQ(stk, 400)

            # 其他指标
            r_tuple_index_pic = gen_Idx_Pic_wx(df, stk_code=stk)
            result_analysis_list = result_analysis_list + r_tuple_index_pic[1]

            # 日线分析结果汇总
            r_tuple_day_pic = gen_Day_Pic_wx(df, stk_code=stk)
            result_analysis_list = result_analysis_list + r_tuple_day_pic[1]

            stk_pic_dict = {
                'hour': gen_Hour_MACD_Pic_wx(stk),
                'day': r_tuple_day_pic[0],
                'wm': gen_W_M_MACD_Pic_wx(stk),
                'index': r_tuple_index_pic[0]
            }

            stk_list_pic_dict[stk] = (stk_info[0], stk_pic_dict)

        # 将page中的stk pic存入字典
        pic_dict[tab] = stk_list_pic_dict

    return pic_dict, result_analysis_list


if __name__ == '__main__':
    
    from DataSource.auth_info import *
    r = get_pic_dict()
    end = 0