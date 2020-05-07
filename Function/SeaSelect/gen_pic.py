# encoding=utf-8

"""
股票选好后，需要将该股票的信息打印到pdf中，便于主观分析
此脚本存放生成pdf相关的代码

要实现的功能是：
给定一个 股票代码，将该股票的信息打印到pdf中

"""
import os

from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login, logout
from Function.GenPic.gen_pic_class import GenPic
from Global_Value.file_dir import sea_select_pic_dir
from sdk.Gen_Stk_Pic_Sub import gen_hour_macd_values, gen_hour_index_pic_local, \
    gen_day_pic_local, gen_w_m_macd_pic_local, gen_idx_pic_local
from sdk.MyTimeOPT import get_current_date_str, get_current_datetime_str


def gen_stk_sea_select_pic(stk_code):

    try:
        jq_login()

        # 保存路径
        save_dir = sea_select_pic_dir + get_current_date_str() + '/'

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 准备 小时 和 日线 数据
        df_hour = gen_hour_macd_values(stk_code)
        df_day = get_k_data_JQ(stk_code, 800)

        # 定义图片名称
        file_name = stk_code + '.png'

        # 生成小时图片
        GenPic.gen_hour_macd_pic_local(df_hour, stk_code, save_dir + 'h_' + file_name)
        gen_hour_index_pic_local(df_hour[0], stk_code, save_dir + 'h_idx_' + file_name)
        gen_day_pic_local(df_day, stk_code, save_dir + 'd_' + file_name)
        gen_w_m_macd_pic_local(df_day, stk_code, save_dir + 'wm_' + file_name)
        gen_idx_pic_local(df_day, stk_code, save_dir + 'd_idx_' + file_name)

    except Exception as e:
        print('生成股票走势图失败！原因：\n' + str(e))
    finally:
        logout()


if __name__ == '__main__':
    jq_login()

    """ --------------------- 生成相关图片 ------------------------ """

    """ --------------------- 读取图片生成pdf ------------------------ """

    end = 0
