# encoding=utf-8

"""
本脚本用于定时将大盘以及关心的stk的走势情况发送到邮箱，每天一次！

"""
import matplotlib

from Config.GlobalSetting import g_total_stk_info_mysql
from HuiCe.Sub import getNameByStkCode
import time


matplotlib.use('Agg')
from CornerDetectAndAutoEmail.Email_Sub import sendmail
from CornerDetectAndAutoEmail.HtmlStr import *
from CornerDetectAndAutoEmail.Sub import genStkPic, genMIMEImageList, genStkIdxPic
from Config.AutoStkConfig import stk_list
from SDK.MyTimeOPT import get_current_date_str
import tushare as ts
from apscheduler.schedulers.blocking import BlockingScheduler


def dailyStkInfoEmail():
    """
    定时器每天要执行的函数,发送所关心的基本的stk信息
    :return:
    """

    """ -------------------------- 组织html --------------------------- """

    # 构造html的单位
    H_str = '' + H_Head                     # html字符串
    date_str = get_current_date_str()       # 获取当前日期
    pic_dir_list = []                       # 用以保存用到的图片的路径

    """ 制定html """
    for stk in stk_list:
        stk_df = ts.get_k_data(stk)

        # 生成图片
        pic_dir_stk = genStkPic(stk_df,
                                stk,
                                date_str,
                                pic_save_dir_root,
                                pic_name='stk_A_C_M.png')

        pic_dir_index = genStkIdxPic(stk_df,
                                     stk,
                                     date_str,
                                     pic_save_dir_root,
                                     pic_name='stk_idx.png')

        pic_dir_list.append(pic_dir_stk)
        pic_dir_list.append(pic_dir_index)

        # 构造html
        H_str = H_str + gen_H_Unit(stk_code=stk,
                                   stk_name=getNameByStkCode(g_total_stk_info_mysql, stk),
                                   pic_dir=pic_dir_stk.replace(pic_save_dir_root, ''))\
                    + gen_H_Unit(stk_code=stk,
                                   stk_name=getNameByStkCode(g_total_stk_info_mysql, stk),
                                   pic_dir=pic_dir_index.replace(pic_save_dir_root, ''))

        print('完成'+str(stk) + '  的邮件内容！')

    H_str = H_str + H_tail

    """ ------------------- 生成需要的图片 ----------------------- """
    msgImage_list = genMIMEImageList(pic_dir_list)

    """ -------------------- 邮件发送 ----------------------- """

    while True:
        mail_return = sendmail(
            subject='Darling, daily report for you!',
            MIMEText_Input=MIMEText(H_str, 'html', 'utf-8'),
            MIMEImageList=msgImage_list,
            toaddrs=["your email@163.com", "189916591@qq.com"],
            fromaddr="ai_report@163.com",
            smtpaddr="smtp.163.com",
            password="sqm654321")
        if mail_return == 0:
            break
        else:
            print('邮件发送失败！原因：'+str(mail_return)+'\n将延时后重发！')
            time.sleep(20)


def dailyStkInfoEmail_input(stk_list):
    """
    定时器每天要执行的函数,发送所关心的基本的stk信息
    :return:
    """

    """ -------------------------- 组织html --------------------------- """

    # 构造html的单位
    H_str = '' + H_Head                     # html字符串
    date_str = get_current_date_str()       # 获取当前日期
    pic_dir_list = []                       # 用以保存用到的图片的路径

    """ 制定html """
    for stk in stk_list:
        stk_df = ts.get_k_data(stk)

        # 生成图片
        pic_dir_stk = genStkPic(stk_df,
                                stk,
                                date_str,
                                pic_save_dir_root,
                                pic_name='stk_A_C_M.png')

        pic_dir_index = genStkIdxPic(stk_df,
                                     stk,
                                     date_str,
                                     pic_save_dir_root,
                                     pic_name='stk_idx.png')

        pic_dir_list.append(pic_dir_stk)
        pic_dir_list.append(pic_dir_index)

        # 构造html
        H_str = H_str + gen_H_Unit(stk_code=stk,
                                   stk_name=getNameByStkCode(g_total_stk_info_mysql, stk),
                                   pic_dir=pic_dir_stk.replace(pic_save_dir_root, ''))\
                    + gen_H_Unit(stk_code=stk,
                                   stk_name=getNameByStkCode(g_total_stk_info_mysql, stk),
                                   pic_dir=pic_dir_index.replace(pic_save_dir_root, ''))

        print('完成'+str(stk) + '  的邮件内容！')

    H_str = H_str + H_tail

    """ ------------------- 生成需要的图片 ----------------------- """
    msgImage_list = genMIMEImageList(pic_dir_list)

    """ -------------------- 邮件发送 ----------------------- """

    while True:
        mail_return = sendmail(
            subject='Darling, daily report for you!',
            MIMEText_Input=MIMEText(H_str, 'html', 'utf-8'),
            MIMEImageList=msgImage_list,
            toaddrs=["your email@163.com", "189916591@qq.com"],
            fromaddr="ai_report@163.com",
            smtpaddr="smtp.163.com",
            password="sqm654321")
        if mail_return == 0:
            break
        else:
            print('邮件发送失败！原因：'+str(mail_return)+'\n将延时后重发！')
            time.sleep(20)


# 函数测试
# dailyStkInfoEmail()

if __name__ == '__main__':

    """ ------------------ 启动定时器 --------------------- """
    sched = BlockingScheduler()
    sched.add_job(func=dailyStkInfoEmail, trigger='cron', day_of_week='mon-fri', hour=5, minute=0, misfire_grace_time=3600, coalesce=True)
    # sched.add_job(func=dailyStkInfoEmail, trigger='interval', minutes=5)
    sched.start()