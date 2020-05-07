# encoding=utf-8
"""
配置日志模块
配置教程 https://www.cnblogs.com/liujiacai/p/7804848.html

"""
import logging
import logging.handlers
import os

from Global_Value.file_dir import rootPath

root_path = rootPath


class MyLog:
    def __init__(self):
        
        # 定义日志格式
        self.format = logging.Formatter('%(asctime)s -> %(filename)s ->'
                                        ' [line:%(lineno)d] -> %(funcName)s -> [%(levelname)s]: %(message)s')
        
        self.logger = logging.getLogger('python-web')
        self.logger.setLevel(logging.DEBUG)
        self.root_path = root_path
        
        # 为了杜绝logger对象多次生成时重复打印的情况，需要进行判断
        if not self.logger.handlers:
            self.config_log_console(level=logging.WARNING)
            self.config_log_file(level=logging.WARNING)
    
    def config_log_file(self, save_dir_relative='\logs/', file_name='log_', level=logging.WARNING, time_span=10,
                        backupCount=100):
        """
        配置打印文件
        :param save_dir_relative:
        :param file_name:
        :param level: 打印日志文件的级别  logging.WARNING
        :param time_span: 日志文件按时间分割，分割间隔
        :return:
        """
        # 定义一个打印到文件中的
        log_dir = self.root_path + save_dir_relative
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        fh = logging.handlers.TimedRotatingFileHandler(filename=log_dir + file_name + str(level) + '.log', when='M',
                                                       interval=time_span,
                                                       backupCount=backupCount, encoding='utf-8')
        # fh = logging.FileHandler(log_dir + file_name + get_current_date_str() + '.log', mode='w', encoding='UTF-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.format)
        self.logger.addHandler(fh)
    
    def config_log_console(self, level):
        """
        配置命令行文件的打印格式
        :return:
        """
        ch = logging.StreamHandler()
        ch.setLevel(level=level)
        ch.setFormatter(self.format)
        self.logger.addHandler(ch)


# 实例一个logging对象
ml = MyLog()
logger = ml.logger
if __name__ == '__main__':
    # logging.debug('这是debug信息！')
    
    logger.debug('这是debug信息！')
    logger.info('这是debug信息！')
    logger.warning('这是debug信息！')
    logger.error('这是debug信息！')
    logger.fatal('这是debug信息！')


