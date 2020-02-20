# encoding=utf-8
"""
这个脚本是用来存储 stk自动检测 程序的配置信息

"""
import os

from Config.AutoGenerateConfigFile import check_config_file


curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = curPath[:curPath.find("MoDeng\\")+len("MoDeng\\")]  # 获取myProject，也就是项目的根路径
# rootPath = curPath[:curPath.find("MoDeng\\")+len("MoDeng\\")]  # 获取myProject，也就是项目的根路径

# 检查配置
check_config_file()

