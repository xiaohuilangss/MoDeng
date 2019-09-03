# encoding=utf-8
import pandas as pd
import tushare as ts

from CornerDetectAndAutoEmail.Email_Sub import sendmailForStk
from CornerDetectAndAutoEmail.HtmlStr import gen_H_Unit, genH_Intro, H_Head, H_tail
from CornerDetectAndAutoEmail.Sub import JudgeCornerPot
from Config.AutoStkConfig import stk_list


"""
本脚本用来测试自动拐点检测的整个流程

首先整理出日期序列，用这个日期序列模拟每天的运行

"""

# 下载池中的截止到今天的数据，并存在list列表里
stk_data = list(map(lambda x: {'stk_code': x, 'stk_df': ts.get_k_data(x)}, stk_list))


# 整理日期序列
date_list = pd.date_range(start='2018-01-10', end='2018-12-30')

for date in date_list:

    date_str = str(date)[0:10]

    # 遍历stk池
    CornerPot_Judge_result = []
    for stk in stk_list:

        # 取出该stk的数据，并获取截止到当天的数据
        stk_single_df = list(filter(lambda x: x['stk_code']==stk, stk_data))[0]['stk_df']

        # 截取截止当天的数据
        stk_single_df_cut = stk_single_df[stk_single_df['date'] <= date_str]

        # 判断拐点
        stk_single_result = JudgeCornerPot(stk_df=stk_single_df_cut, stk_code=stk, current_date=date_str)

        CornerPot_Judge_result.append(stk_single_result)

    # 整理这一天的，将结果整合为df
    result_df = pd.DataFrame(CornerPot_Judge_result)

    # 判断是否有存在拐点的stk？
    result_df_corner = result_df[result_df['corner_flag']]

    if not result_df_corner.empty:

        # 构造综述信息
        H_Info = genH_Intro(str(list(result_df_corner['stk_code'])))

        # 保存拐点stk的html信息用
        H_Unit = ''
        for idx in result_df_corner.index:

            # 构造html的单位
            stk_code = result_df_corner.loc[idx, 'stk_code']
            stk_name = stk_code

            H_Unit = H_Unit + gen_H_Unit(stk_code, stk_name, date_str)

        # 构造邮件信息
        Html_str = H_Head + H_Info + H_Unit + H_tail

        # 发送邮件
        sendmailForStk(
            fromaddr="ai_report@163.com",
            smtpaddr="smtp.163.com",
            toaddrs=["1234567@qq.com"],
            subject="AI自动报告-V1",
            password="sqm654321",
            html_str=Html_str,
            date_str=date_str,
            corner_pot_list=list(result_df_corner['stk_code'])
        )
    else:
        print(date_str+' ：这一天没有拐点！')

end=0