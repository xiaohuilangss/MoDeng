# encoding = utf-8
# !/usr/bin/python
# coding:utf-8


# from email import Header

# fromaddr = "ai_report@163.com"
fromaddr = "your email@163.com"
smtpaddr = "smtp.163.com"

toaddrs = ["1234567@qq.com"]
subject = "AI自动报告-V1"
# password = "myDBpassword"
password = "87315287"


#!/usr/bin/env python3
#coding: utf-8
import smtplib
from email.mime.text import MIMEText

sender = fromaddr
receiver = toaddrs
subject = '本日报告'
smtpserver = 'smtp.163.com'
username = fromaddr
password = password

msg = MIMEText('下午开会')

msg['Subject'] = subject

smtp = smtplib.SMTP()
smtp.connect('smtp.163.com')
smtp.login(username, password)
smtp.sendmail(sender, receiver, msg.as_string())
smtp.quit()
