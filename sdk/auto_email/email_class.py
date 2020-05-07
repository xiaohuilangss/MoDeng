# encoding=utf-8

"""
有关email类的实现
"""
import email
import json
import os, pickle
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.encoders import encode_base64

from Config.log import logger


class MyEmail:
    def __init__(self):
        self.sender = ''
        self.passwd = ''
        self.smtp_domain = ''
    
    def config_sender_info_by_json(self, json_file_path):
        """
        加载含有发件人账密的json文件，读取账密
        json文件有以下字段：
        sender：发件人账号
        passwd：发件人密码
        smtp_domain：发件邮箱服务器域名
        :return:
        """
        if not os.path.exists(json_file_path):
            logger.error('在路径【%s】没有找到包含发件人账密的json文件！' % json_file_path)
            return False
        
        try:
            with open(json_file_path, 'w') as f:
                data_json = json.load(f)
                self.sender = data_json['sender']
                self.passwd = data_json['passwd']
                self.smtp_domain = data_json['smtp']
            return True
        
        except Exception as e_:
            logger.error('从路径【%s】读取发件人账密时出现异常错误！:\n %s' % (json_file_path, str(e_)))
            return False
        
    @staticmethod
    def get_attachment(attachment_file_path):
        
        """
        获取附件
        :param attachment_file_path: 附件文件路径
        :return:
        """
        
        # 根据 guess_type方法判断文件的类型和编码方式
        content_type, encoding = mimetypes.guess_type(attachment_file_path)
        
        # 如果根据文件的名字/后缀识别不出是什么文件类型,使用默认类型
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        # 根据contentType 判断主类型与子类型
        main_type, sub_type = content_type.split('/', 1)
        file = open(attachment_file_path, 'rb')

        # 根据主类型不同，调用不同的文件读取方法
        if main_type == 'text':
            attachment = MIMEBase(main_type,sub_type)
            attachment.set_payload(file.read())
            encode_base64(attachment)
            
        elif main_type == 'message':
            attachment = email.message_from_file(file)
    
        elif main_type == 'image':
            attachment = MIMEImage(file.read())
    
        # elif mainType == 'audio':  # 音频
        # attachment = MIMEAudio(file.read(), _subType=subType)
    
        else:
            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(file.read())
            encode_base64(attachment)
    
        file.close()
        """
            Content-disposition 是 MIME 协议的扩展,
            MIME 协议指示 MIME 用户代理如何显示附加的文件。
            Content-disposition其实可以控制用户请求所得的内容存为一个文件的时候提供一个默认的文件名，
            文件直接在浏览器上显示或者在访问时弹出文件下载对话框。
            content-disposition = "Content-Disposition" ":" disposition-type *( ";" disposition-parm )。
            # Content-Disposition为属性名 disposition-type是以什么方式下载，
            如attachment为以附件方式下载 disposition-parm为默认保存时的文件名
        """
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_file_path))
        
        return attachment
    
    def send_email(self, subject, recipient, text, *attachment_file_paths):
        """
        发送邮件函数：参数（邮件主题，邮件内容，邮件附件（可多选））
        :param subject:
        :param recipient:
        :param text:
        :param attachment_file_paths:
        :return:
        """
        
        # 发送附件时需调用 MIMEMultipart类，创建 MIMEMultipart,并添加信息头
        msg = MIMEMultipart()
        
        """
        MIME邮件的基本信息、格式信息、编码方式等重要内容都记录在邮件内的各种域中，
        域的基本格式：{域名}：{内容}，域由域名后面跟“：”再加上域的信息内容构成，
        一条域在邮件中占一行或者多行，
        域的首行左侧不能有空白字符，比如空格或者制表符，
        占用多行的域其后续行则必须以空白字符开头。
        域的信息内容中还可以包含属性，属性之间以“;”分隔，
        属性的格式如下：{属性名称}=”{属性值}”。
        """
        
        # 登记基础信息及正文
        msg['From'] = self.sender
        msg['To'] = ";".join(recipient)
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
    
        # 添加附件
        for attachmentFilePath in attachment_file_paths:
            msg.attach(self.get_attachment(attachmentFilePath))
        
        try:
            mail_server = smtplib.SMTP('smtp.163.com')
            mail_server.ehlo()
            mail_server.starttls()
            mail_server.ehlo()
            mail_server.login(self.sender, self.passwd)
            mail_server.sendmail(self.sender, recipient, msg.as_string())
            mail_server.close()
            logger.info('成功向【%s】发送邮件！' % recipient)
            
        except Exception as e_:
            logger.error('发件失败，原因：\n %s' % str(e_))