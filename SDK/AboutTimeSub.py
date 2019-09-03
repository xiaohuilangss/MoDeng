# encoding = utf-8
from Config.GlobalSetting import *

# 与时间相关的自定义函数文件


# 将“2017.8”转成“2017.08”，否则在画图时会出现错乱，因为画图时8会大于12
def stdMonthDate(month_str):

    str_split = month_str.split('.')
    if int(str_split[1]) <10:
        str_split[1] = "0"+str_split[1]

    return str_split[0]+'.'+str_split[1]


def stdMonthDate2ISO(month_str):
    """
    函数功能：将“2017.8”转成“2017-08-01”，便于将其转为秒数以实现时间轴对齐
    :param month_str:
    :return:
    """
    str_split = month_str.split('.')
    if (int(str_split[1]) < 10) & (len(str_split[1]) == 1):     # 添加后一句判断是为了防止加0过度的情况，如果原先的格式已经是标准格式，则不需要再添加0
        str_split[1] = "0"+str_split[1]

    return str_split[0]+'-'+str_split[1] + '-01'


def convertQuarter2Value(quarter):

    """
    函数功能：'2018.2' --> 2018.5

    有些展示的数据，其时间轴为季度，
    对这些数据进行展示的时候，为了时间轴能够对齐，需要将季度转为合适的绝对值数
    :param: quarter 季度日期，格式如2018.3
    :return:
    """

    year, quarter = quarter.split('.')

    if quarter == '1':
        q_value = 0
    elif quarter == '2':
        q_value = 0.25
    elif quarter == '3':
        q_value = 0.5
    elif quarter == '4':
        q_value = 0.75

    return float(year) + q_value


def convertValue2Quarter(value):

    """
    函数功能：2018.5 --> '2018.2'
    :return:
    """
    decimal = value%1

    if decimal == 0:
        q_str = '1'
    elif decimal == 0.25:
        q_str = '2'
    elif decimal == 0.5:
        q_str = '3'
    elif decimal == 0.75:
        q_str = '4'

    year_str = str(math.floor(value))

    return year_str + '.' + q_str



