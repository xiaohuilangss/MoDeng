# encoding=utf-8
from Config.Sub import readConfig
from DataSource.Data_Sub import get_k_data_JQ
from SDK.Gen_Stk_Index_Pic_Sub import gen_Hour_MACD_Pic, gen_Day_Pic, gen_W_M_MACD_Pic, gen_Idx_Pic


def get_pic_dict():
    """
    获取图片字典
    :return:
    """
    dict_stk_list = {
        'index': ['sh', 'sz', 'cyb'],
        'buy': readConfig()['buy_stk'],
        'concerned': readConfig()['concerned_stk']
    }

    pic_dict = {}
    for tab in dict_stk_list.keys():
        stk_list = dict_stk_list[tab]
        stk_list_pic_dict = {}

        for stk in stk_list:
            df = get_k_data_JQ(stk, 400)
            stk_pic_dict = {
                'hour': gen_Hour_MACD_Pic(stk),
                'day': gen_Day_Pic(df, stk_code=stk)[0],
                'wm': gen_W_M_MACD_Pic(stk),
                'index': gen_Idx_Pic(df, stk_code='')[0]
            }

            stk_list_pic_dict[stk] = stk_pic_dict

        # 将page中的stk pic存入字典
        pic_dict[tab] = stk_list_pic_dict

    return pic_dict


if __name__ == '__main__':
    
    from DataSource.auth_info import *
    r = get_pic_dict()
    end = 0