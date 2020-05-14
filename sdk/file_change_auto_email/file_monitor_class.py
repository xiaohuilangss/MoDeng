# encoding=utf-8

"""
本脚本实现检测日志功能

原理：
监控文件修改情况，检测到有修改，
便直接将该文件邮件发送给指定联系人
"""
from Config.log import MyLog
from sdk.auto_email.email_class import MyEmail
logger = MyLog('file_monitor').logger

import os
import time


class FileMonitor:
    def __init__(self, monitor_name, file_dir, file_word, recipient, sender_info_json_file, heart_beat_time_span=60*60*24):
        """
        :param file_dir:    被监控文件所在目录
        :param file_word:   被监控文件名关键字
        """
        self.recipient = recipient
        self.monitor_name = monitor_name
        self.heart_beat_time_span = heart_beat_time_span
        self.sender_info_json_file = sender_info_json_file
        self.file_dir = file_dir
        self.file_word = file_word
        
        # 创建email对象
        self.eml = MyEmail()
        
        # 文件列表
        self.file_dict_list = []
        
        # 上次心跳时间
        self.heart_beat_last_time = time.time()
    
    def get_all_file(self):
        """
        根据路径和关键字，找出所有对应的文件
        :return:
        """
        f_name_list = os.listdir(self.file_dir)
        return list(filter(lambda x: self.file_word in x, f_name_list))
    
    @staticmethod
    def gen_file_dict(file_name, update_time, need_to_send):
        """
        
        :param file_name:
        :param update_time:
        :param need_to_send:
        :return:
        """
        return {
            "file_name": file_name,
            "update_time": update_time,
            "need_to_send": need_to_send
        }
    
    def add_new_file(self, f_list):
        """
        将新生成的文件增加到“文件”list中
        :param f_list:
        :return:
        """
        self.file_dict_list = self.file_dict_list + [self.gen_file_dict(
            file_name=x,
            update_time=os.path.getmtime(self.file_dir + x),
            need_to_send=True) for x in f_list]
    
    def check_old_file_change(self):
        """
        检查之前已经登记过的文件有没有改动
        :return:
        """
        if len(self.file_dict_list) > 0:
            for f in self.file_dict_list:
                u_t = os.path.getmtime(self.file_dir + f['file_name'])
                
                if u_t != f['update_time']:
                    f['need_to_send'] = True
                    f['update_time'] = u_t
                    
            logger.debug('已完成对已登记文件的修改检测！')
        else:
            logger.debug('目前没有登记文件！')
            
    def get_new_file(self, file_name_list):
        """
        找出新生成的未登记的文件
        :return:
        """
        if len(self.file_dict_list) == 0:
            return file_name_list
        else:
            file_name_exist = [x['file_name'] for x in self.file_dict_list]
            file_name_new = list(filter(lambda x: x not in file_name_exist, file_name_list))
        return file_name_new
        
    def check_file_change(self):
        """
        检查给定路径下文件，查看标记应该发送的文件（新创建的或者有修改过的）
        :return:
        """
        # 获取该路径下当前的所有相关文件
        f_list_now = self.get_all_file()
        
        # 查找新增文件
        if len(self.file_dict_list) == 0:
            self.add_new_file(f_list_now)
        else:
            # 检查老日志是否需要发送
            self.check_old_file_change()
            
            # 添加新日志
            self.add_new_file(self.get_new_file(f_list_now))
            
    def email_change_file(self, recipient, subject=''):
        """
        将改动的日志作为附件发送
        :param recipient:  ['pwnevy@163.com']
        :param subject:
        :return:
        """

        # 组成待发送日志
        file_dict_to_send = list(filter(lambda x: x['need_to_send'], self.file_dict_list))
        if len(file_dict_to_send) == 0:
            logger.info('没有检测到有改动文件！')
            return
            
        file_path_to_send = [self.file_dir+x['file_name'] for x in file_dict_to_send]
        self.eml.send_email(
            self.monitor_name+':检测到文件改动!',
            recipient,
            '',
            file_path_to_send)
        
        # 复位标志位
        for f_dict in self.file_dict_list:
            f_dict['need_to_send'] = False
        
    def monitor(self, time_span=60*5):
        
        if not self.eml.config_sender_info_by_json(self.sender_info_json_file):
            logger.error('配置发件邮箱出错！')
            return False
        
        run = True
        
        # 循环检测
        while run:
            try:
                self.heart_beat()
                
                # 检查文件
                self.check_file_change()
                
                # 发送变动
                self.email_change_file(self.recipient)
                
                time.sleep(time_span)
                
            except Exception as e_:
                self.eml.send_email(
                    self.monitor_name+'-异常终止！',
                    self.recipient,
                    str(e_)+'/n监控器已停止运行，请检查问题原因并手动启动监控器！')
                run = False
                exit(1)
            
    def heart_beat(self):
        """
        定时心跳
        :return:
        """
        if time.time() - self.heart_beat_last_time > self.heart_beat_time_span:
            self.eml.send_email(self.monitor_name+'-心跳邮件', self.recipient, '')
            self.heart_beat_last_time = time.time()
            
            
if __name__ == '__main__':
    
    email_json = "C:\modeng\data\Email\senderInfo.json"
    
    fm = FileMonitor(
        monitor_name='实验监控器',
        file_dir='C:/Users\Administrator\Desktop\99_1服务器/2020-05-14/',
        file_word='408窗帘',
        sender_info_json_file=email_json,
        recipient=['1210055099@qq.com'],
        heart_beat_time_span=30)
    
    fm.monitor(time_span=10)