# encoding=utf-8

import smtplib
import traceback
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import io
import tushare as ts
# from General.GlobalSetting import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from CornerDetectAndAutoEmail.HtmlStr import addInfoToMsg

"""
@subject:       邮件主题
@msg:           邮件内容
@toaddrs:       收信人的邮箱地址
@fromaddr:      发信人的邮箱地址
@smtpaddr:      smtp服务地址，可以在邮箱看，比如163邮箱为smtp.163.com

@password:      发信人的邮箱密码
"""


def sendmail(subject, MIMEText_Input, MIMEImageList, toaddrs, fromaddr, smtpaddr, password):
    """
    本函数更为通用，制定收发人信息以及邮件的text和图片之后，就可以发送
    :param subject:
    :param MIMEText_Input:
    :param MIMEImageList:
    :param toaddrs:
    :param fromaddr:
    :param smtpaddr:
    :param password:
    :return:
    """

    mail_msg = MIMEMultipart('related')
    if not isinstance(subject, str):
        subject = str(subject, 'utf-8')

    mail_msg['Subject'] = subject
    mail_msg['From'] = fromaddr
    mail_msg['To'] = ','.join(toaddrs)

    # 向消息中加载text
    mail_msg.attach(MIMEText_Input)

    # 加载所需要的图片
    for img in MIMEImageList:
        mail_msg.attach(img)

    try:
        s = smtplib.SMTP()
        s.connect(smtpaddr)             # 连接smtp服务器
        s.helo(smtpaddr)
        s.ehlo(smtpaddr)
        s.login(fromaddr, password)     # 登录邮箱

        s.sendmail(fromaddr, toaddrs, mail_msg.as_string())  # 发送邮件
        s.quit()
        print('邮件发送成功！')
        return 0

    except :
        print("Error: unable to send email")
        print(traceback.format_exc())
        return -1


def sendmailForStk(subject, html_str, toaddrs, fromaddr, smtpaddr, password, date_str, corner_pot_list):

    mail_msg = MIMEMultipart('related')
    if not isinstance(subject, str):
        subject = str(subject, 'utf-8')

    mail_msg['Subject'] = subject
    mail_msg['From'] = fromaddr
    mail_msg['To'] = ','.join(toaddrs)

    # 加载相应图片
    addInfoToMsg(mail_msg, html_str, date_str, corner_pot_list)

    try:
        s = smtplib.SMTP()
        s.connect(smtpaddr)             # 连接smtp服务器
        s.helo(smtpaddr)
        s.ehlo(smtpaddr)
        s.login(fromaddr, password)     # 登录邮箱

        s.sendmail(fromaddr, toaddrs, mail_msg.as_string())  # 发送邮件
        s.quit()
    except :
        print("Error: unable to send email")
        print(traceback.format_exc())


    """
    邮箱密码：123456@test
    邮箱授权码：sqm654321
    """

if __name__ == '__main__':
    # fromaddr = "your email@163.com"
    fromaddr = "ai_report@163.com"
    smtpaddr = "smtp.163.com"

    toaddrs = ["1234567@qq.com"]
    subject = "AI自动报告-V1"
    # password = "87315287"
    password = "sqm654321"
    # msg = ts.get_latest_news(top=5,show_content=True).loc[0,"content"]
    # msg = '<html><body><h1>Hello</h1>' +\
    #       '<p><img src = "cid:0"></p>' +\
    #     '</body></html>'

    msg = '测试一下能否发送成功！'

    sendmailForStk(subject, msg, toaddrs, fromaddr, smtpaddr, password)
