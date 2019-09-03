# encoding = utf-8
import email
import os, pickle
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.encoders import encode_base64

from SDK.MyTimeOPT import get_current_date_str


def dumpPickle(data, saveLocation, fileName):

    """
    请使用dumpP
    :param data:
    :param saveLocation:
    :param fileName:
    :return:
    """
    os.chdir(saveLocation)                              # 文件存放的路径
    with open(fileName, 'wb') as f:
        pickle.dump(data, f)                            # 导入数据data到文件f中
        print('save data: %s successful' % fileName)


def loadPickle(loadLocation, fileName):
    """
    请使用loadP
    :param loadLocation:
    :param fileName:
    :return:
    """
    os.chdir(loadLocation)              # 文件读取的路径
    with open(fileName, 'rb') as f:
        return pickle.load(f)           # 读取数据


def sendMail(subject, recipient, text, *attachmentFilePaths):
    '''发送邮件函数：参数（邮件主题，邮件内容，邮件附件（可多选））'''
    msg = MIMEMultipart()  # 发送附件时需调用 MIMEMultipart类，创建 MIMEMultipart,并添加信息头

    '''
    MIME邮件的基本信息、格式信息、编码方式等重要内容都记录在邮件内的各种域中，域的基本格式：{域名}：{内容}，域由域名后面跟“：”再加上域的信息内容构成，一条域在邮件中占一行或者多行，
    域的首行左侧不能有空白字符，比如空格或者制表符，占用多行的域其后续行则必须以空白字符开头。域的信息内容中还可以包含属性，属性之间以“;”分隔，属性的格式如下：{属性名称}=”{属性值}”。    
    '''
    senderInfo = loadPickle(os.path.basename('.'), "senderInfo.txt")
    sender = senderInfo.split("?")[0]               # 发件人邮箱
    password = senderInfo.split("?")[1]             # 发件人邮箱密码
    # recipient = senderInfo.split("?")[2]            # 收件人邮箱
    # recipient = [recipient[2:-2]]                   # 将string格式的"['收件人邮箱']"转换成['收件人邮箱']


    msg['From'] = sender
    msg['To'] = ";".join(recipient)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    for attachmentFilePath in attachmentFilePaths:                  # 判断添加哪些附件
        msg.attach(getAttachment(attachmentFilePath))               # 如果入参给定附件文件，使用attach 发放添加msg头信息
    # try:
    mailServer = smtplib.SMTP('smtp.163.com')                       # 连接腾讯邮件的服务器；SMTP（Simple Mail Transfer Protocol）即简单邮件传输协议，用于由源地址到目的地址传送邮件的规则，由它来控制信件的中转方式
    mailServer.ehlo()                                               # 使用starttls 方法必须先 ehlo 判断是否是同一个地址。。。
    mailServer.starttls()                                           # 以下SMTP都会加密;Put the SMTP connection in TLS (Transport Layer Security) mode. All SMTP commands that follow will be encrypted.
    mailServer.ehlo()                                               # You should then call ehlo() again.
    mailServer.login(sender, password)                              # 登录邮箱
    mailServer.sendmail(sender, recipient, msg.as_string())         # 发送邮件（发件人，收件人，发送内容）
    mailServer.close()                                              # 关闭邮件发送服务
    print('Sent email to %s successfully' % recipient)
    # except Exception as e:
    #     print('sendEmai failed %s' % e)


"""
part = MIMEApplication(open('foo.mp3','rb').read()) 
part.add_header('Content-Disposition', 'attachment', filename="foo.mp3") 
msg.attach(part) 
"""


def getAttachment(attachmentFilePath):                                  # 获取附件，参数：文件路径
    contentType, encoding = mimetypes.guess_type(attachmentFilePath)    # 根据 guess_type方法判断文件的类型和编码方式

    if contentType is None or encoding is not None:         # 如果根据文件的名字/后缀识别不出是什么文件类型
        contentType = 'application/octet-stream'            # 使用默认类型，usable for a MIME content-type header.

    mainType, subType = contentType.split('/', 1)           # 根据contentType 判断主类型与子类型
    file = open(attachmentFilePath, 'rb')

    if mainType == 'text':                                  # 根据主类型不同，调用不同的文件读取方法
        attachment = MIMEBase(mainType, subType)            # A subclass of MIMENonMultipart, the MIMEText class is used to create MIME objects of major type text.
        attachment.set_payload(file.read())                 # Set the entire message object’s payload（负载） to payload.
        encode_base64(attachment)                           # Encodes the payload into base64 form and sets the Content-Transfer-Encoding header to base64.
    elif mainType == 'message':
        attachment = email.message_from_file(file)          # 使用message_from_file方法，Return a message object structure tree from an open file object

    elif mainType == 'image':  # 图片
        attachment = MIMEImage(file.read())                 #A subclass of MIMENonMultipart, the MIMEImage class is used to create MIME message objects of major type image.

    #elif mainType == 'audio':  # 音频
        #attachment = MIMEAudio(file.read(), _subType=subType)  #A subclass of MIMENonMultipart, the MIMEAudio class is used to create MIME message objects of major type audio.

    else:
        attachment = MIMEBase(mainType, subType)        # The MIMEBase class always adds a Content-Type header (based on _maintype, _subtype, and _params), and a MIME-Version header (always set to 1.0).
        attachment.set_payload(file.read())             # Set the entire message object’s payload（负载） to payload.
        encode_base64(attachment)                       # Encodes the payload into base64 form and sets the Content-Transfer-Encoding header to base64.

    file.close()
    """
        Content-disposition 是 MIME 协议的扩展，MIME 协议指示 MIME 用户代理如何显示附加的文件。Content-disposition其实可以控制用户请求所得的内容存为一个文件的时候提供一个默认的文件名，
        文件直接在浏览器上显示或者在访问时弹出文件下载对话框。 content-disposition = "Content-Disposition" ":" disposition-type *( ";" disposition-parm ) 。    
            """
    attachment.add_header('Content-Disposition', 'attachment',   filename=os.path.basename(attachmentFilePath))  #Content-Disposition为属性名 disposition-type是以什么方式下载，如attachment为以附件方式下载 disposition-parm为默认保存时的文件名
    return attachment

# dumpPickle(data="ai_report@163.com?myDBpassword?['1234567@qq.com']", saveLocation=os.path.basename('.'), fileName="senderInfo.txt")


if __name__ == "__main__":
    # senderInfo = loadPickle(os.path.basename('.'), "senderInfo.txt")
    # sender = senderInfo.split("?")[0]               # 发件人邮箱
    # password = senderInfo.split("?")[1]             # 发件人邮箱密码
    # recipient = senderInfo.split("?")[2]            # 收件人邮箱
    # recipient = [recipient[2:-2]]                   # 将string格式的"['收件人邮箱']"转换成['收件人邮箱']
    # sendMail('pdf测试邮件', recipient, '测试一下以附件的方式发送pdf的可行性', U'日度用电报告2018-09-11.pdf')

    senderInfo = loadPickle(os.path.basename('.'), "senderInfo.txt")
    sender = senderInfo.split("?")[0]  # 发件人邮箱
    password = senderInfo.split("?")[1]  # 发件人邮箱密码
    # recipient = senderInfo.split("?")[2]            # 收件人邮箱
    # recipient = [recipient[2:-2]]                   # 将string格式的"['收件人邮箱']"转换成['收件人邮箱']

    recipient = ['1234567@qq.com',
                 '3303366489@qq.com',
                 '2314923644@qq.com',
                 '3122140480@qq.com',
                 '1959148913@qq.com',
                 '2384205754@qq.com',
                 '2959544903@qq.com',
                 '1156668277@qq.com',
                 '2624822992@qq.com',
                 '1170200744@qq.com',
                 '313201657@qq.com',
                 '2897475285@qq.com']

    sendMail("A股日报" + get_current_date_str(), recipient, '', U"A股日报" + get_current_date_str() + ".pdf")


