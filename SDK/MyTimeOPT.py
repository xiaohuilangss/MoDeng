# coding = utf-8
import time
# from datetime import *
import datetime

import math

'''Function: get current system datetime
:return         datetime string format as:'2017-09-12 12:23:41'
'''

# 转换操作
def convert_datetime_to_str(datetime_param):
    return datetime.date.strftime(datetime_param, '%Y-%m-%d %H:%M:%S')


def convert_date_to_str(date_param):
    return datetime.date.strftime(date_param, '%Y-%m-%d')


def convert_str_to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')


def convert_str_to_date(date_str):
    if len(date_str) > 11:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
    else:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

def date_str_std(date_str):

    date_str_sure = '%s' %date_str
    if not '-' in date_str_sure:
        return convert_date_to_str(datetime.datetime.strptime(date_str_sure, '%Y%m%d').date())
    else:
        return date_str_sure


def convert_time_str_to_second(input_str):
    """
    # 将时间转为秒数
    :param input_str:
    :return:
    """

    result = input_str.strip().split(":")
    if len(result) == 3:
        h, m, s = result
        return int(h) * 3600 + int(m) * 60 + int(float(s))
    elif len(result) == 2:
        h, m = result
        return int(h) * 3600 + int(m) * 60


def s2t(seconds):
    """
    将秒转为字符串形式的时间
    :param seconds:
    :return:
    """

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def DatetimeStr2Sec(s):
    """
    convert a ISO format time to second
    from:2006-04-12 16:46:40 to:23123123
    把一个时间转化为秒
    :param s:
    :return:
    """

    d=datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return time.mktime(d.timetuple())


def DateStr2Sec(s):
    d=datetime.datetime.strptime(s, "%Y-%m-%d")
    return time.mktime(d.timetuple())


def Sec2Datetime(s):
    """
    convert second to a ISO format time
    from: 23123123 to: 2006-04-12 16:46:40
    把给定的秒转化为定义的格式
    :param s:
    :return:
    """

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(s)))


def cal_quarter(date):
    """
    输入日期，输出季度
    输入'2015-03-04'
    输出 '201501'
    :param date:
    :return:
    """

    date_split = date.split("-")
    date_m = date_split[1]

    if (date_m == "01")|(date_m == "02")|(date_m == "03"):
        return date_split[0] + "01"

    if (date_m == "04")|(date_m == "05")|(date_m == "06"):
        return date_split[0] + "02"

    if (date_m == "07")|(date_m == "08")|(date_m == "09"):
        return date_split[0] + "03"

    if (date_m == "10")|(date_m == "11")|(date_m == "12"):
        return date_split[0] + "04"


# 获取操作
def get_current_datetime_str():
    datetime_now = datetime.datetime.now()
    return datetime.datetime.strftime(datetime_now, '%Y-%m-%d %H:%M:%S')


def get_current_date_str():
    datetime_now = datetime.datetime.now()
    return datetime.datetime.strftime(datetime_now, '%Y-%m-%d')


def get_current_date():
    return datetime.datetime.now().date()


def get_datestr_from_datetimestr(datetime_str):
    datetime_inner = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    return datetime.datetime.strftime(datetime_inner, '%Y-%m-%d')


def get_date_from_datetime_str(datetime_param):
    date_str = str(datetime_param)[0:10]
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def get_date_from_datetime(datetime_param):
    datetime_str = datetime.datetime.strftime(datetime_param, '%Y-%m-%d %H:%M:%S')
    date_str = datetime_str[0:10]
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def get_quarter_date():
    """
    计算得到当前所在的季度，201703的格式
    :return:
    """
    date_split_str = get_current_date_str().split('-')
    year_str = date_split_str[0]
    month_str = date_split_str[1]

    year_int = int(year_str)
    month_int = int(month_str)

    # 判断当前季度
    quarter = math.floor((month_int-1)/3) +1
    return year_str + '0'+str(quarter)


"""------------------------------- 加减操作 ----------------------------------"""


def add_date_str(origin_date_str, days):
    """
    字符串格式的时间日期的加减，以天为单位
    将字符串转为日期格式后，进行天数的加减，然后在转回字符串
    :param origin_date_str:
    :param days:
    :return:
    """
    origin_date = convert_str_to_date(origin_date_str)
    return convert_date_to_str(origin_date + datetime.timedelta(days=days))


def minus_date_str(pos_date, net_date):
    return (convert_str_to_date(pos_date) - convert_str_to_date(net_date)).days


def minus_datetime_str(pos_date, net_date):
    sec = (convert_str_to_date(pos_date) - convert_str_to_date(net_date)).seconds
    days = sec % (60*60*24)
    minutes = (sec - days*60*60*24) % (60*60)
    secs = sec-days*60*60*24-minutes*60*60
    return days, minutes, secs


""" ------------------------------- timestamp与datetime之间的转换 --------------------------------- """


def get_date_from_timestamp(timestamp_para):
    date_str = get_datestr_from_datetimestr(str(timestamp_para))
    return convert_str_to_date(date_str)


