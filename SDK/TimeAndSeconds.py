# encoding = utf-8
import time
import datetime


def minute_reckon(t_s):
    """
    计时（分钟） 计算耗时函数
    :param t_s:
    :return:
    """
    return '%0.3f' % ((time.time()-t_s)/60)


def minute_reckon_print(t_s, note=''):
    print(note + '总耗时' + minute_reckon(t_s) + '分钟！')


def DatetimeStr2Sec(s):

    '''
    convert a ISO format time to second
    from:2006-04-12 16:46:40 to:23123123
    把一个时间转化为秒
    '''

    d=datetime.datetime.strptime(s,"%Y-%m-%d %H:%M:%S")
    return time.mktime(d.timetuple())


def DateStr2Sec(s):

    d=datetime.datetime.strptime(s,"%Y-%m-%d")
    return time.mktime(d.timetuple())


def Sec2Datetime(s):

    '''
    convert second to a ISO format time
    from: 23123123 to: 2006-04-12 16:46:40
    把给定的秒转化为定义的格式
    '''

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(s)))