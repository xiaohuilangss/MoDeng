#!/usr/bin/python

#-*-coding:UTF-8-*-

import smtplib

from email.mime.text import MIMEText

mailto_list=['1234567@qq.com']           #收件人(列表)

mail_host="smtp.163.com"            #使用的邮箱的smtp服务器地址，这里是163的smtp地址

mail_user="test"                           #用户名

mail_postfix="163.com"                     #邮箱的后缀，网易就是163.com

def send_mail(to_list,sub,content):

    me="hello"+"<"+mail_user+"@"+mail_postfix+">"

    msg = MIMEText(content,_subtype='plain')

    msg['Subject'] = sub

    msg['From'] = me

    msg['To'] = ";".join(to_list)                #将收件人列表以‘；’分隔




    """
    邮箱密码：123456@test
    邮箱授权码：sqm654321
    """
    server = smtplib.SMTP()
    server.connect(mail_host)                            #连接服务器
    server.helo(mail_host)
    server.ehlo(mail_host)
    server.login("ai_report@163.com", "sqm654321")    #登录操作,密码是授权码，而不是邮箱登录密码
    server.sendmail("ai_report@163.com", to_list, msg.as_string())
    server.close()

    return True



for i in range(1):                             #发送1封，上面的列表是几个人，这个就填几

    if send_mail(mailto_list,"电话","电话是XXX辅导辅导辅导"):  #邮件主题和邮件内容

        #这是最好写点中文，如果随便写，可能会被网易当做垃圾邮件退信
        print("done!")