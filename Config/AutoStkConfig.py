# encoding=utf-8
"""
这个脚本是用来存储 stk自动检测 程序的配置信息

"""
import os

from Config.AutoGenerateConfigFile import checkConfigFile

cubic_test_last_step = 7        # 在曲线拟合时，取最后的几个值进行二次拟合

# 图片存在的路径，如果没有自动创建
# if os.path.exists('C:/Users/paul/Desktop/软件代码/MoDeng/TempPicStore/'):
#     pic_save_dir_root = 'C:/Users/paul/Desktop/软件代码/MoDeng/TempPicStore/'
#
# elif os.path.exists('F:/软件代码/MoDeng/TempPicStore/'):
#     pic_save_dir_root = 'F:/软件代码/MoDeng/TempPicStore/'
#
# else:
#     os.makedirs('C:/Users/paul/Desktop/软件代码/MoDeng/TempPicStore/')
#     pic_save_dir_root = 'C:/Users/paul/Desktop/软件代码/MoDeng/TempPicStore/'

plot_current_days_amount = 40   # 画出近期的stk走势情况，该参数指示最近取的天数
tailLengthForMACD = 150         # 在计算MACD时，因为之用最近的几个数，所以不需要往前延伸太多，以节省计算量

# 关心的stk
stk_list = [
    'cyb',
    'sh',
    'sz',
    '300508',
    '000625',
    '000725',
    '000001',
    '000333',
    '300508',
    '002456',
    '603421',
    '300059',
    '600487',
    '600036'
]

step_corner_detect = 6                  # 在判断拐点的时候，取最近的数据的个数
corner_Pot_Retrospective_Half = 6       # 进行后验检测拐点时，时间窗的一半

curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = curPath[:curPath.find("MoDeng\\")+len("MoDeng\\")]  # 获取myProject，也就是项目的根路径
rootPath = curPath[:curPath.find("MoDeng\\")+len("MoDeng\\")]  # 获取myProject，也就是项目的根路径

MDataPWD = os.path.abspath(rootPath + '/RelativeRank/')

SeaSelectDataPWD = os.path.abspath(rootPath+'/AutoDailyOpt/SeaSelect/')

LastScale = os.path.abspath(rootPath+'/AutoDailyOpt/') + '/LastScale/'

# 检查配置
checkConfigFile()

