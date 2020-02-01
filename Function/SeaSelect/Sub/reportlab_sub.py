# encoding = utf-8
import math

import datetime

import PIL
import os
import tushare as ts
import numpy as np
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df
from DataSource.auth_info import jq_login, logout
from Global_Value.file_dir import sea_select_pic_dir, rootPath

from SDK.AboutTimeSub import convertValue2Quarter, stdMonthDate2ISO, convertQuarter2Value, stdMonthDate
from SDK.Gen_Stk_Pic_Sub import gen_hour_macd_pic_local, gen_hour_index_pic_local, gen_day_pic_local, \
    gen_w_m_macd_pic_local, gen_idx_pic_local, gen_hour_macd_values
from SDK.MyTimeOPT import Sec2Datetime, DatetimeStr2Sec, DateStr2Sec, add_date_str, get_current_date_str
import pandas as pd
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.pagesizes import letter

# 画图相关
from reportlab.graphics.shapes import Drawing, colors, Auto
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('song', 'SURSONG.TTF'))
pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))

from reportlab.lib import fonts
fonts.addMapping('song', 0, 0, 'song')
fonts.addMapping('song', 0, 1, 'song')
fonts.addMapping('song', 1, 0, 'hei')
fonts.addMapping('song', 1, 1, 'hei')

# 获取纸面的高度和宽度
w = letter[0]
h = letter[1]


def add_front(canvas_param, theme, subtitle, pagesize=letter):
    """
    函数功能：为pdf文档添加功能，分“主题”、“副标题”两部分
    :param canvas:
    :param pagesize: 页面大小，默认A4
    :param theme: 主题字符串
    :param subtitle: 副标题字符串
    :return:
    """
    PAGE_WIDTH = pagesize[0]
    PAGE_HEIGHT = pagesize[1]

    # 设置主标题字体并打印主标题
    canvas_param.setFont("song", 30)
    canvas_param.drawString((PAGE_WIDTH-stringWidth(theme, fontName='song', fontSize=30))/2.0, PAGE_HEIGHT*0.618, theme)

    # 设置副标题字体并打印副标题
    canvas_param.setFont("song", 14)
    canvas_param.drawString((PAGE_WIDTH-stringWidth(subtitle, fontName='song', fontSize=14))/2.0, PAGE_HEIGHT*0.15, subtitle)

    canvas_param.showPage()

    return canvas_param


def add_legend(draw_obj, chart, pos_x, pos_y):

    """
    函数功能：voltGroupDisplayByBar函数的子函数
    :param draw_obj:
    :param chart:
    :return:
    """
    legend = Legend()
    legend.alignment = 'right'
    legend.fontName = 'song'
    legend.columnMaximum = 2
    legend.x = pos_x
    legend.y = pos_y
    legend.colorNamePairs = Auto(obj=chart)
    draw_obj.add(legend)


def extract_point_from_df_date_x(df_origin, date_col, y_col, timeAxis='day'):

    """
    函数功能：从一个dataframe中提取两列，组成point列表格式，以供ReportLab画图之用
                同时将日期中的时间提取出来，转为秒。

                本函数主要用来画当日数据！因为将datetime中的date去掉了，只保留time。

    :param df_origin:
    :param x_col:
    :param y_col:
    :return:
    """

    # 将“data”列中的数据解析后，作为新的列增加到df中
    # df_origin = ExtractJsonToColum(df_row=df_origin, col='data')
    # if len(df_origin) == 0:
    #     return []

    # 按时间排序，并删除空值
    df_origin = df_origin.sort_values(by=date_col, ascending=True)
    df_origin = df_origin[~df_origin[y_col].isnull()]

    # if len(df_origin) == 0:
    #     print('函数 ExtractPointFromDf_DateX：删除空值后，dataframe为空！入参df中不含指定列')
    #     return df_origin

    # 提取时间，并将时间转为秒
    if timeAxis == 'day':
        df_origin['time'] = df_origin.apply(lambda x: DateStr2Sec(str(x[date_col])), axis=1)

    elif timeAxis == 'datetime':
        df_origin['time'] = df_origin.apply(lambda x: DatetimeStr2Sec(str(x[date_col])), axis=1)

    elif timeAxis == 'quarter':
        df_origin['time'] = df_origin.apply(lambda x: convertQuarter2Value(str(x[date_col])), axis=1)

    elif timeAxis == 'year':
        df_origin['time'] = df_origin.apply(lambda x: x[date_col], axis=1)

    elif timeAxis == 'month':
        df_origin['time'] = df_origin.apply(lambda x: DateStr2Sec(stdMonthDate2ISO(str(x[date_col]))),axis=1)

    # 单独取出相应两列，准备转成point格式
    df_part = df_origin.loc[:, ['time', y_col]]

    # 将df转为array
    point_array = list(map(lambda x: (x[0], float(x[1])), df_part.values))

    return point_array


def gen_lp_drawing(data, data_note, width=letter[0] * 0.8, height=letter[1] * 0.25, time_axis='day', y_min_zero=False,
                   line_width=1.5, marker_size=5):
    """
    函数功能：生成Drawing之用
    :return:
    """

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()

    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义颜色集
    barFillColors = [
        colors.red, colors.green, colors.blue, colors.darkgoldenrod,
        colors.pink, colors.purple, colors.lightgreen, colors.darkblue, colors.lightyellow,
        colors.fidred, colors.greenyellow, colors.gray, colors.white,colors.blueviolet, colors.lightgoldenrodyellow]

    for i in range(0, len(data)):
        lp.lines[i].name = data_note[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=marker_size)
        lp.lines[i].strokeWidth = line_width
        lp.lines[i].strokeColor = barFillColors[i]

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    x_min = data[0][0][0]
    x_max = data[0][-1][0]

    lp.xValueAxis.valueMin = x_min
    lp.xValueAxis.valueMax = x_max

    if time_axis == 'day':
        step = int(((x_max - x_min) / (60 * 60 * 24)) / 30) + 1

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), 60 * 60 * 24 * step)]
        lp.xValueAxis.labelTextFormat = lambda x: str(Sec2Datetime(x)[0:10])
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18
        if y_min_zero:
            lp.yValueAxis.valueMin = 0

        # lp.yValueAxis.valueMax = 50
        # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]

    elif time_axis == 'quarter':

        step = int(((x_max - x_min)/0.25) / 30) + 1

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), int(math.ceil(0.25 * step)))]
        lp.xValueAxis.labelTextFormat = lambda x: convertValue2Quarter(x)
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif time_axis == 'year':

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), 1)]
        lp.xValueAxis.labelTextFormat = lambda x: str(x)
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif time_axis == 'month':

        lp.xValueAxis.valueSteps = list(map(lambda x:x[0],data[0]))
        lp.xValueAxis.labelTextFormat = lambda x: str(Sec2Datetime(x))[0:7]
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-20)

    return drawing


def gen_bar_drawing(data, data_note, width=letter[0] * 0.8, height=letter[1] * 0.25):
    """
    函数功能：生成Drawing之用
    :return:
    """
    data_value = list(map(lambda x:x[1],data))

    data_finale = [tuple(data_value)]

    drawing = Drawing(width=width, height=height)


    bc = VerticalBarChart()

    # bc.x = 50
    # bc.y = 50
    # bc.height = 125
    bc.width = width
    bc.data = data_finale
    # bc.valueAxis.valueMin = 0
    bc.barSpacing = 0

    # bc.valueAxis.valueMax = 50
    # bc.valueAxis.valueStep = 10
    # bc.categoryAxis.style = 'stacked'
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30

    barFillColors = [
        colors.red, colors.green, colors.white, colors.blue, colors.yellow,
        colors.pink, colors.purple, colors.lightgreen, colors.darkblue, colors.lightyellow,
        colors.fidred, colors.greenyellow, colors.gray, colors.blueviolet, colors.lightgoldenrodyellow]

    for i in range(len(data_finale)):
        bc.bars[i].name = data_note[i]

        # 最多只支持15种颜色，多出的设置为红色
        if i < 15:
            bc.bars[i].fillColor = barFillColors[i]
        else:
            bc.bars[i].fillColor = colors.red

    # x_min = data[0][0]
    # x_max = data[-1][0]

    # bc.xValueAxis.valueMin = x_min
    # lp.xValueAxis.valueMax = x_max

    # step = int(((x_max - x_min) / (60 * 60 * 24)) / 15) + 1

    # bc.categoryAxis.categoryNames = [str(Sec2Datetime(x))[0:10] for x in range(int(x_min), int(x_max), 60 * 60 * 24 * step)]

    drawing.add(bc)

    # 增加legend
    # add_legend(drawing, bc, pos_x=10, pos_y=-10)

    return drawing


def rpl_stk_page(canvas_para, stk_code):
    """
    函数功能：在pdf中增加bk信息，篇幅为一整页，或者更多，以页为单位
    :param stk_code:
    :param days:        用于指示近期的期限，比如近30天
    :return:
    """

    # 插入字符串，用以表明stk代码及名称
    canvas_para.setFont("song", 10)
    if stk_code in ['sh', 'sz', 'cyb']:
        stk_name = stk_code

    else:
        stk_name = code2name(stk_code)

    # 打印stk代码和名字
    canvas_para.drawString(20, letter[1] - 10, stk_code + ' ' + stk_name + ' ' + '日线数据')

    # 准备数据
    df_stk = ts.get_hist_data(stk_code)
    df_stk['date'] = df_stk.index
    df_stk = df_stk.reset_index(drop=True)

    close = extract_point_from_df_date_x(df_stk, 'date', 'close')

    data = [tuple(close)]
    data_name = ['close']

    drawing_ave = gen_lp_drawing(data=data, data_note=data_name, height=letter[1] * 0.1, line_width=0.5, marker_size=2)
    renderPDF.draw(drawing=drawing_ave, canvas=canvas_para, x=10, y=letter[1] * 0.85)

    # 按时间降序排序，方便计算MACD
    df_stk = df_stk.sort_values(by='date', ascending=True)

    # 加入各种指标
    df_stk = add_stk_index_to_df(df_stk)

    # 去除空值，截取最新数据
    df_stk = df_stk.dropna(axis=0, how='any').tail(40)

    close = extract_point_from_df_date_x(df_stk, 'date', 'close')
    sar = extract_point_from_df_date_x(df_stk, 'date', 'SAR')

    MACD = extract_point_from_df_date_x(df_stk, 'date', 'MACD')

    data = [tuple(close), tuple(sar)]
    data_name = ['close', 'sar']

    drawing_ave = gen_lp_drawing(data=data, data_note=data_name, height=letter[1] * 0.1, line_width=1.5, marker_size=5)
    renderPDF.draw(drawing=drawing_ave, canvas=canvas_para, x=10, y=letter[1] * 0.7)

    drawing_MACD = gen_bar_drawing(data=MACD, data_note=['MACD'], height=letter[1] * 0.1)
    renderPDF.draw(drawing=drawing_MACD, canvas=canvas_para, x=10, y=letter[1]*0.5)

    # 整理kdj信息
    slowk = extract_point_from_df_date_x(df_stk, 'date', 'slowk')
    slowd = extract_point_from_df_date_x(df_stk, 'date', 'slowd')
    data_kdj = [tuple(slowk), tuple(slowd)]
    data_kdj_note = ['k', 'd']

    drawing_kdj = gen_lp_drawing(data=data_kdj, data_note=data_kdj_note, height=letter[1] * 0.1)
    renderPDF.draw(drawing=drawing_kdj, canvas=canvas_para, x=10, y=letter[1] * 0.4)

    # 画图RSI信息
    RSI5 = extract_point_from_df_date_x(df_stk, 'date', 'RSI5')
    RSI12 = extract_point_from_df_date_x(df_stk, 'date', 'RSI12')
    RSI30 = extract_point_from_df_date_x(df_stk, 'date', 'RSI30')

    data_RSI = [tuple(RSI5), tuple(RSI12), tuple(RSI30)]
    data_RSI_note = ['RSI5', 'RSI12', 'RSI30']

    drawing_RSI = gen_lp_drawing(data=data_RSI, data_note=data_RSI_note, height=letter[1] * 0.1)
    renderPDF.draw(drawing=drawing_RSI, canvas=canvas_para, x=10, y=letter[1] * 0.25)

    # 画图布林线
    upper = extract_point_from_df_date_x(df_stk, 'date', 'upper')
    middle = extract_point_from_df_date_x(df_stk, 'date', 'middle')
    lower = extract_point_from_df_date_x(df_stk, 'date', 'lower')

    data_BOLL = [tuple(upper), tuple(middle), tuple(lower)]
    data_BOLL_note = ['上线', '中线', '下线']

    drawing_BOLL = gen_lp_drawing(data=data_BOLL, data_note=data_BOLL_note, height=letter[1] * 0.1)
    renderPDF.draw(drawing=drawing_BOLL, canvas=canvas_para, x=10, y=letter[1] * 0.1)

    canvas_para.showPage()

    return canvas_para


def rpl_stk_hour_page(canvas_para, stk_code):
    """
    函数功能：在pdf中增加bk信息，篇幅为一整页，或者更多，以页为单位
    :param stk_code:
    :param days:        用于指示近期的期限，比如近30天
    :return:
    """

    # 插入字符串，用以表明stk代码及名称
    canvas_para.setFont("song", 10)
    if stk_code in ['sh', 'sz', 'cyb']:
        stk_name = stk_code

    else:
        stk_name = code2name(stk_code)

    # 打印stk代码和名字
    canvas_para.drawString(20, letter[1] - 10, stk_code + ' ' + stk_name + ' ' + '小时数据')

    # 准备数据
    df_stk = get_k_data_JQ(stk_code, start_date=add_date_str(get_current_date_str(), -200), freq='30m')
    df_stk['date'] = df_stk.reset_index().index
    df_stk = df_stk.reset_index(drop=True)

    close = extract_point_from_df_date_x(df_stk, 'date', 'close', timeAxis='year')

    data = [tuple(close)]
    data_name = ['close']

    drawing_ave = gen_lp_drawing(data=data, data_note=data_name, height=letter[1] * 0.1, line_width=0.5, marker_size=2, time_axis='year')
    renderPDF.draw(drawing=drawing_ave, canvas=canvas_para, x=10, y=letter[1] * 0.85)

    # 按时间降序排序，方便计算MACD
    df_stk = df_stk.sort_values(by='date', ascending=True)

    # 加入各种指标
    df_stk = add_stk_index_to_df(df_stk)

    # 去除空值，截取最新数据
    df_stk = df_stk.dropna(axis=0, how='any').tail(40)

    close = extract_point_from_df_date_x(df_stk, 'date', 'close', timeAxis='year')
    sar = extract_point_from_df_date_x(df_stk, 'date', 'SAR', timeAxis='year')

    MACD = extract_point_from_df_date_x(df_stk, 'date', 'MACD', timeAxis='year')

    data = [tuple(close), tuple(sar)]
    data_name = ['close', 'sar']

    drawing_ave = gen_lp_drawing(data=data, data_note=data_name, height=letter[1] * 0.1, line_width=1.5, marker_size=5, time_axis='year')
    renderPDF.draw(drawing=drawing_ave, canvas=canvas_para, x=10, y=letter[1] * 0.7)

    drawing_MACD = gen_bar_drawing(data=MACD, data_note=['MACD'], height=letter[1] * 0.1)
    renderPDF.draw(drawing=drawing_MACD, canvas=canvas_para, x=10, y=letter[1]*0.5)

    # 整理kdj信息
    slowk = extract_point_from_df_date_x(df_stk, 'date', 'slowk', timeAxis='year')
    slowd = extract_point_from_df_date_x(df_stk, 'date', 'slowd', timeAxis='year')
    data_kdj = [tuple(slowk), tuple(slowd)]
    data_kdj_note = ['k', 'd']

    drawing_kdj = gen_lp_drawing(data=data_kdj, data_note=data_kdj_note, height=letter[1] * 0.1, time_axis='year')
    renderPDF.draw(drawing=drawing_kdj, canvas=canvas_para, x=10, y=letter[1] * 0.4)

    # 画图RSI信息
    RSI5 = extract_point_from_df_date_x(df_stk, 'date', 'RSI5', timeAxis='year')
    RSI12 = extract_point_from_df_date_x(df_stk, 'date', 'RSI12', timeAxis='year')
    RSI30 = extract_point_from_df_date_x(df_stk, 'date', 'RSI30', timeAxis='year')

    data_RSI = [tuple(RSI5), tuple(RSI12), tuple(RSI30)]
    data_RSI_note = ['RSI5', 'RSI12', 'RSI30']

    drawing_RSI = gen_lp_drawing(data=data_RSI, data_note=data_RSI_note, height=letter[1] * 0.1, time_axis='year')
    renderPDF.draw(drawing=drawing_RSI, canvas=canvas_para, x=10, y=letter[1] * 0.25)

    # 画图布林线
    upper = extract_point_from_df_date_x(df_stk, 'date', 'upper', timeAxis='year')
    middle = extract_point_from_df_date_x(df_stk, 'date', 'middle', timeAxis='year')
    lower = extract_point_from_df_date_x(df_stk, 'date', 'lower', timeAxis='year')

    data_BOLL = [tuple(upper), tuple(middle), tuple(lower)]
    data_BOLL_note = ['上线', '中线', '下线']

    drawing_BOLL = gen_lp_drawing(data=data_BOLL, data_note=data_BOLL_note, height=letter[1] * 0.1, time_axis='year')
    renderPDF.draw(drawing=drawing_BOLL, canvas=canvas_para, x=10, y=letter[1] * 0.1)

    canvas_para.showPage()

    return canvas_para


def add_money_supply_aage(canvas_para):
    """
    函数功能：在pdf中增加货币供应页
    :param canvas_para:
    :return:
    """

    c = canvas_para

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '货币供应')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)


    # 画货币供应量
    money_supply = ts.get_money_supply().replace('--', np.nan)
    money_supply['date'] = money_supply.apply(lambda x: stdMonthDate2ISO(x['month']), axis=1)

    # 画货币量曲线图
    m0 = extract_point_from_df_date_x(money_supply, 'date', 'm0')
    m1 = extract_point_from_df_date_x(money_supply, 'date', 'm1')
    m2 = extract_point_from_df_date_x(money_supply, 'date', 'm2')

    data_supply = [tuple(m0), tuple(m1), tuple(m2)]
    data_supply_note = ['m0', 'm1', 'm2']

    money_drawing = gen_lp_drawing(data=data_supply, data_note=data_supply_note, height=letter[1] * 0.2)
    renderPDF.draw(drawing=money_drawing, canvas=c, x=10, y=letter[1] * 0.7)

    # 画货币量增长率曲线图
    m0_yoy = extract_point_from_df_date_x(money_supply, 'date', 'm0_yoy')
    m1_yoy = extract_point_from_df_date_x(money_supply, 'date', 'm1_yoy')
    m2_yoy = extract_point_from_df_date_x(money_supply, 'date', 'm2_yoy')

    data_supply_yoy = [tuple(m0_yoy), tuple(m1_yoy), tuple(m2_yoy)]
    data_supply_yoy_note = ['m0增长率', 'm1增长率', 'm2增长率']

    money_yoy_drawing = gen_lp_drawing(data=data_supply_yoy, data_note=data_supply_yoy_note, height=letter[1] * 0.2)
    renderPDF.draw(drawing=money_yoy_drawing, canvas=c, x=10, y=letter[1] * 0.4)

    c.showPage()

    return c


def add_reserve_base_rate_page(canvas_para):
    """
    函数功能：在pdf中增加准备金基率
    :param canvas_para:
    :return:
    """

    c = canvas_para

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '存款准备金基率')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)

    # 画银行准备金基率
    df_rbr = ts.get_rrr().replace('--', np.nan)
    # df_rbr['date'] = df_rbr.apply(lambda x: stdMonthDate2ISO(x['month']), axis=1)

    # 提取相关数据
    pot_before = extract_point_from_df_date_x(df_rbr, 'date', 'before')
    pot_now = extract_point_from_df_date_x(df_rbr, 'date', 'now')
    pot_changed = extract_point_from_df_date_x(df_rbr, 'date', 'changed')

    data_rbr = [tuple(pot_now)]
    data_rbr_note = ['准备金基率']

    money_drawing = gen_lp_drawing(data=data_rbr, data_note=data_rbr_note, height=letter[1] * 0.2)
    renderPDF.draw(drawing=money_drawing, canvas=c, x=10, y=letter[1] * 0.7)

    c.showPage()

    return c


def add_quarter_gdp_page(canvas_para):

    """
    函数功能：增加季度GDP页
    :param canvas_para:
    :return:
    """

    c = canvas_para

    gdp_quarter = ts.get_gdp_quarter()

    gdp_yoy = extract_point_from_df_date_x(df_origin=gdp_quarter, date_col='quarter', y_col='gdp_yoy', timeAxis='quarter')
    pi_yoy = extract_point_from_df_date_x(df_origin=gdp_quarter, date_col='quarter', y_col='pi_yoy', timeAxis='quarter')
    si_yoy = extract_point_from_df_date_x(df_origin=gdp_quarter, date_col='quarter', y_col='si_yoy', timeAxis='quarter')

    ti_yoy = extract_point_from_df_date_x(df_origin=gdp_quarter, date_col='quarter', y_col='ti_yoy', timeAxis='quarter')


    gdp_pull_drawing = gen_lp_drawing([tuple(gdp_yoy), tuple(pi_yoy), tuple(si_yoy), tuple(ti_yoy)],
                                      data_note=['GDP同比增长率','第一产业增长率','第二产业增长率','第三产业增长率'],
                                      time_axis='quarter')

    renderPDF.draw(drawing=gdp_pull_drawing, canvas=c, x=10, y=letter[1] * 0.6)

    c.showPage()

    return c


def add_demands_for_gdp_page(canvas_para):

    """
    函数功能：三大需求对GDP的贡献
    :param canvas_para:
    :return:
    """

    c = canvas_para

    gdp_for = ts.get_gdp_for()

    end_for = extract_point_from_df_date_x(df_origin=gdp_for, date_col='year', y_col='end_for', timeAxis='year')
    asset_for = extract_point_from_df_date_x(df_origin=gdp_for, date_col='year', y_col='asset_for', timeAxis='year')
    goods_for = extract_point_from_df_date_x(df_origin=gdp_for, date_col='year', y_col='goods_for', timeAxis='year')

    gdp_for_drawing = gen_lp_drawing([tuple(end_for), tuple(asset_for), tuple(goods_for)], ['最终消费支出贡献率', '资本形成总额贡献率', '货物和服务净出口贡献率'], time_axis='year')

    renderPDF.draw(drawing=gdp_for_drawing, canvas=c, x=10, y=letter[1] * 0.6)

    for_rate = extract_point_from_df_date_x(df_origin=gdp_for, date_col='year', y_col='for_rate', timeAxis='year')
    asset_rate = extract_point_from_df_date_x(df_origin=gdp_for, date_col='year', y_col='asset_rate', timeAxis='year')
    goods_rate = extract_point_from_df_date_x(df_origin=gdp_for, date_col='year', y_col='goods_rate', timeAxis='year')


    gdp_for_drawing = gen_lp_drawing([tuple(for_rate), tuple(asset_rate), tuple(goods_rate)], ['最终消费支出拉动(百分点)', '资本形成总额拉动(百分点)', '货物和服务净出口拉动(百分点)'], time_axis='year')

    renderPDF.draw(drawing=gdp_for_drawing, canvas=c, x=10, y=letter[1] * 0.2)

    c.showPage()

    return c


def add_gdp_pull_page(canvas_para):

    """
    函数功能：展示三个产业对GDP的拉动情况
    :param canvas_para:
    :return:
    """

    c = canvas_para

    gdp_pull = ts.get_gdp_pull()

    gdp_yoy = extract_point_from_df_date_x(df_origin=gdp_pull, date_col='year', y_col='gdp_yoy', timeAxis='year')
    pi = extract_point_from_df_date_x(df_origin=gdp_pull, date_col='year', y_col='pi', timeAxis='year')
    si = extract_point_from_df_date_x(df_origin=gdp_pull, date_col='year', y_col='si', timeAxis='year')
    industry = extract_point_from_df_date_x(df_origin=gdp_pull, date_col='year', y_col='industry', timeAxis='year')
    ti = extract_point_from_df_date_x(df_origin=gdp_pull, date_col='year', y_col='ti', timeAxis='year')


    gdp_pull_drawing = gen_lp_drawing([tuple(gdp_yoy), tuple(pi), tuple(si), tuple(industry), tuple(ti)],
                                      data_note=['GDP同比增长率','第一产业拉动率','第二产业拉动率','工业拉动率','第三产业拉动率'],
                                      time_axis='year')

    renderPDF.draw(drawing=gdp_pull_drawing, canvas=c, x=10, y=letter[1] * 0.6)

    c.showPage()

    return c


def add_cpi_page(canvas_para, length):
    """
    函数功能：增加CPI页
    :param canvas_para:
    :return:
    """

    c = canvas_para

    cpi_df = ts.get_cpi()
    cpi_df['month'] = cpi_df.apply(lambda x: stdMonthDate(x['month']), axis=1)
    cpi_df = cpi_df.sort_values(by='month', ascending=False).head(length).sort_values(by='month', ascending=True)

    cpi = extract_point_from_df_date_x(df_origin=cpi_df, date_col='month', y_col='cpi', timeAxis='month')

    gdp_pull_drawing = gen_lp_drawing([tuple(cpi)],
                                      data_note=['CPI增长率'],
                                      time_axis='month')

    renderPDF.draw(drawing=gdp_pull_drawing, canvas=c, x=10, y=letter[1] * 0.6)

    c.showPage()

    return c


def add_ppi_page(canvas_para, length):
    """
    函数功能：工业品出厂价格指数
    :param canvas_para:
    :return:
    """

    c = canvas_para

    ppi_df = ts.get_ppi()
    ppi_df['month'] = ppi_df.apply(lambda x:stdMonthDate(x['month']), axis=1)
    ppi_df = ppi_df.sort_values(by='month',ascending=False).head(length).sort_values(by='month',ascending=True)

    ppiip = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='ppiip', timeAxis='month')
    ppi = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='ppi', timeAxis='month')
    qm = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='qm', timeAxis='month')
    rmi = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='rmi', timeAxis='month')
    pi = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='pi', timeAxis='month')


    ppi_industry_drawing = gen_lp_drawing([tuple(ppiip), tuple(ppi), tuple(qm), tuple(rmi), tuple(pi)],
                                          data_note=['工业品出厂价格指数',
                                               '生产资料价格指数',
                                               '采掘工业价格指数',
                                               '原材料工业价格指数',
                                               '加工工业价格指数'],
                                          time_axis='month')

    renderPDF.draw(drawing=ppi_industry_drawing, canvas=c, x=10, y=letter[1] * 0.6)

    cg = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='cg', timeAxis='month')
    food = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='food', timeAxis='month')
    clothing = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='clothing', timeAxis='month')
    roeu = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='roeu', timeAxis='month')
    dcg = extract_point_from_df_date_x(df_origin=ppi_df, date_col='month', y_col='dcg', timeAxis='month')


    ppi_life_drawing = gen_lp_drawing([tuple(cg), tuple(food), tuple(clothing), tuple(roeu), tuple(dcg)],
                                      data_note=['生活资料价格指数',
                                               '食品类价格指数',
                                               '衣着类价格指数',
                                               '一般日用品价格指数',
                                               '耐用消费品价格指数'],
                                      time_axis='month')

    renderPDF.draw(drawing=ppi_life_drawing, canvas=c, x=10, y=letter[1] * 0.2)

    c.showPage()

    return c


def add_shibor_page(canvas_para, year_start='2006', year_end=str(datetime.datetime.now().year + 1)):
    """
    函数功能：增加银行间拆借利率页
    :param canvas_para:
    :return:
    """
    c = canvas_para

    date_list = pd.date_range(start=year_start, end=year_end, freq='12M')
    year_list = [str(x)[0:4] for x in date_list]

    df_shibor_list = []
    for year in year_list:
        shibor_this = ts.shibor_data(year)
        df_shibor_list.append(shibor_this)

    df_shibor = pd.concat(df_shibor_list,axis=0).sort_values(by='date', ascending=True)

    ON = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='ON', timeAxis='datetime')
    W1 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='1W', timeAxis='datetime')
    W2 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='2W', timeAxis='datetime')
    M1 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='1M', timeAxis='datetime')
    M3 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='3M', timeAxis='datetime')
    M6 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='6M', timeAxis='datetime')
    M9 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='9M', timeAxis='datetime')
    Y1 = extract_point_from_df_date_x(df_origin=df_shibor, date_col='date', y_col='1Y', timeAxis='datetime')

    shibor_drawing = gen_lp_drawing([tuple(ON)], data_note=['隔夜拆放利率'], time_axis='day', height=letter[1] * 0.1)
    renderPDF.draw(drawing=shibor_drawing, canvas=c, x=10, y=letter[1] * 0.85)

    shibor_drawing = gen_lp_drawing([tuple(W1)], data_note=['1周拆放利率'], time_axis='day', height=letter[1] * 0.1)
    renderPDF.draw(drawing=shibor_drawing, canvas=c, x=10, y=letter[1] * 0.7)

    shibor_drawing = gen_lp_drawing([tuple(W2)], data_note=['2周拆放利率'], time_axis='day', height=letter[1] * 0.1)
    renderPDF.draw(drawing=shibor_drawing, canvas=c, x=10, y=letter[1] * 0.55)

    shibor_drawing = gen_lp_drawing([tuple(M1)], data_note=['1月拆放利率'], time_axis='day', height=letter[1] * 0.1)
    renderPDF.draw(drawing=shibor_drawing, canvas=c, x=10, y=letter[1] * 0.4)

    shibor_drawing = gen_lp_drawing([tuple(M3),
                                     tuple(M6),
                                     tuple(M9),
                                     tuple(Y1)],

                                    data_note=['3月拆放利率',
                                               '6月拆放利率',
                                               '9月拆放利率',
                                               '1年拆放利率'],

                                    time_axis='day', height=letter[1] * 0.25)

    renderPDF.draw(drawing=shibor_drawing, canvas=c, x=10, y=letter[1] * 0.1)

    c.showPage()
    return c


def add_lpr_page(canvas_para, year_start='2013', year_end=str(datetime.datetime.now().year + 1)):
    """
    函数功能：增加贷款利率页
    :param canvas_para:
    :return:
    """
    c = canvas_para

    date_list = pd.date_range(start=year_start, end=year_end, freq='12M')
    year_list = [str(x)[0:4] for x in date_list]

    df_Lpr_list = []
    for year in year_list:
        lpr_this = ts.lpr_data(year)
        df_Lpr_list.append(lpr_this)

    df_Lpr = pd.concat(df_Lpr_list, axis=0).sort_values(by='date', ascending=True).drop_duplicates(subset='1Y',keep='first')

    Y1 = extract_point_from_df_date_x(df_origin=df_Lpr, date_col='date', y_col='1Y', timeAxis='datetime')
    lpr_drawing = gen_lp_drawing([tuple(Y1)], data_note=['1年贷款基础利率'], time_axis='day', height=letter[1] * 0.3, y_min_zero=True)
    renderPDF.draw(drawing=lpr_drawing, canvas=c, x=10, y=letter[1] * 0.6)

    # 画均值贷款利率
    # df_Lpr_ma_list = []
    # for year in year_list:
    #     lpr_ma_this = ts.lpr_ma_data(year)
    #     df_Lpr_ma_list.append(lpr_ma_this)
    #
    # df_Lpr_ma = pd.concat(df_Lpr_ma_list, axis=0).sort_values(by='date', ascending=True)\
    #     .drop_duplicates(subset=['1Y_5', '1Y_10', '1Y_20'], keep='first')\
    #     .apply(lambda x:x.replace('---',nan), axis=1)
    #
    # Y1_5 = ExtractPointFromDf_DateX(df_origin=df_Lpr_ma, date_col='date', y_col='1Y_5', timeAxis='datetime')
    # Y1_10 = ExtractPointFromDf_DateX(df_origin=df_Lpr_ma, date_col='date', y_col='1Y_10', timeAxis='datetime')
    # Y1_20 = ExtractPointFromDf_DateX(df_origin=df_Lpr_ma, date_col='date', y_col='1Y_20', timeAxis='datetime')
    #
    # lpr_ma_drawing = genLPDrawing([tuple(Y1_5),tuple(Y1_10),tuple(Y1_20)],
    #                               data_note=['1年贷款基础利率-M5','1年贷款基础利率-M10','1年贷款基础利率-M20'],
    #                               timeAxis='day',
    #                               height=letter[1] * 0.3)
    #
    # renderPDF.draw(drawing=lpr_ma_drawing, canvas=c, x=10, y=letter[1] * 0.2)


    c.showPage()
    return c


def add_tail_page(canvas_param, pagesize=letter):
    """
    函数功能：为pdf文档添加功能，分“主题”、“副标题”两部分
    :param canvas:
    :param pagesize: 页面大小，默认A4
    :param theme: 主题字符串
    :param subtitle: 副标题字符串
    :return:
    """
    PAGE_WIDTH = pagesize[0]
    PAGE_HEIGHT = pagesize[1]

    # 设置主标题字体并打印主标题
    canvas_param.setFont("song", 20)
    canvas_param.drawString(20, PAGE_HEIGHT * 0.75, '联系我们：')
    canvas_param.drawString(20, PAGE_HEIGHT * 0.7, '魔灯量化（微信公众号）')

    # 插入小时macd图
    image_file = PIL.Image.open(rootPath + 'Function\SeaSelect\Sub\modeng.jpg')
    canvas_param.drawImage(ImageReader(image_file), x=w * 0.3, y=h * 0.3, height=0.3 * h, width=0.4 * w,
                preserveAspectRatio=True)

    canvas_param.showPage()

    return canvas_param


def print_k_to_pdf(c, stk_code, date):
    """
    将一只股票的走势图打印到pdf中的一页
    :param c:
    :param stk_code:
    :param date:
    :return:
    """

    """ --------------------------------- 打印小时线图片 ------------------------------------ """
    c.setFont("song", 10)
    c.drawString(20, letter[1] - 20, stk_code + ' ' + code2name(stk_code) + ' ' + '小时走势图')
    c.setLineWidth(0.5)
    c.line(10, h - 24, w - 10, h - 24)

    # 插入小时macd图
    try:
        image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'h_' + stk_code + '.png')
        c.drawImage(ImageReader(image_file), x=w * 0.05, y=h * 0.65, height=0.3 * h, width=0.45 * w,
                    preserveAspectRatio=True)
    except Exception as e:
        print('函数print_k_to_pdf：出错！\n' + str(e))

    # 插入小时指标图
    try:
        image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'h_idx_' + stk_code + '.png')
        c.drawImage(ImageReader(image_file), x=w * 0.5, y=h * 0.65, height=0.3 * h, width=0.45 * w,
                    preserveAspectRatio=True)
    except Exception as e:
        print('函数print_k_to_pdf：出错！\n' + str(e))

    """ --------------------------------- 打印日线图片 ------------------------------------ """
    c.setFont("song", 10)
    c.drawString(20, h * 0.65, stk_code + ' ' + code2name(stk_code) + ' ' + '日线走势图')
    c.setLineWidth(0.5)
    c.line(10, h * 0.65 - 4, w - 10, h * 0.65 - 4)

    # 插入日线macd图
    try:
        image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'd_' + stk_code + '.png')
        c.drawImage(ImageReader(image_file), x=w * 0.05, y=h * 0.35, height=0.3 * h, width=0.45 * w,
                    preserveAspectRatio=True)
    except Exception as e:
        print('函数print_k_to_pdf：出错！\n' + str(e))

    # 插入日线指标图
    try:
        image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'd_idx_' + stk_code + '.png')
        c.drawImage(ImageReader(image_file), x=w * 0.5, y=h * 0.35, height=0.3 * h, width=0.45 * w,
                    preserveAspectRatio=True)
    except Exception as e:
        print('函数print_k_to_pdf：出错！\n' + str(e))

    """ --------------------------------- 打印周月线图片 ------------------------------------ """

    c.setFont("song", 10)
    c.drawString(20, h * 0.35, stk_code + ' ' + code2name(stk_code) + ' ' + '周/月走势图')
    c.setLineWidth(0.5)
    c.line(10, h * 0.35 - 4, w - 10, h * 0.35 - 4)

    # 插入周线图
    try:
        image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'wm_' + stk_code + '.png')
        c.drawImage(ImageReader(image_file), x=w * 0.05, y=h * 0.05, height=0.3 * h, width=0.45 * w,
                    preserveAspectRatio=True)
    except Exception as e:
        print('函数print_k_to_pdf：出错！\n' + str(e))

    c.showPage()

    return c


class SeaSelectPdf:

    """
    海选功能中与生成pdf功能的类
    """

    def __init__(self):
        pass

    @staticmethod
    def add_tail_page(canvas_param, pagesize=letter):
        """
        函数功能：为pdf文档添加功能，分“主题”、“副标题”两部分
        :param canvas:
        :param pagesize: 页面大小，默认A4
        :param theme: 主题字符串
        :param subtitle: 副标题字符串
        :return:
        """
        PAGE_WIDTH = pagesize[0]
        PAGE_HEIGHT = pagesize[1]

        # 设置主标题字体并打印主标题
        canvas_param.setFont("song", 20)
        canvas_param.drawString(20, PAGE_HEIGHT * 0.75, '联系我们：')
        canvas_param.drawString(20, PAGE_HEIGHT * 0.7, '魔灯量化（微信公众号）')

        # 插入小时macd图
        image_file = PIL.Image.open(rootPath + 'Function\SeaSelect\Sub\modeng.jpg')
        canvas_param.drawImage(ImageReader(image_file), x=w * 0.3, y=h * 0.3, height=0.3 * h, width=0.4 * w,
                               preserveAspectRatio=True)

        canvas_param.showPage()

        return canvas_param

    @staticmethod
    def print_k_to_pdf(c, stk_code, date):
        """
        将一只股票的走势图打印到pdf中的一页
        :param c:
        :param stk_code:
        :param date:
        :return:
        """

        """ --------------------------------- 打印小时线图片 ------------------------------------ """
        c.setFont("song", 10)
        c.drawString(20, letter[1] - 20, stk_code + ' ' + code2name(stk_code) + ' ' + '小时走势图')
        c.setLineWidth(0.5)
        c.line(10, h - 24, w - 10, h - 24)

        # 插入小时macd图
        try:
            image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'h_' + stk_code + '.png')
            c.drawImage(ImageReader(image_file), x=w * 0.05, y=h * 0.65, height=0.3 * h, width=0.45 * w,
                        preserveAspectRatio=True)
        except Exception as e:
            print('函数print_k_to_pdf：出错！\n' + str(e))

        # 插入小时指标图
        try:
            image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'h_idx_' + stk_code + '.png')
            c.drawImage(ImageReader(image_file), x=w * 0.5, y=h * 0.65, height=0.3 * h, width=0.45 * w,
                        preserveAspectRatio=True)
        except Exception as e:
            print('函数print_k_to_pdf：出错！\n' + str(e))

        """ --------------------------------- 打印日线图片 ------------------------------------ """
        c.setFont("song", 10)
        c.drawString(20, h * 0.65, stk_code + ' ' + code2name(stk_code) + ' ' + '日线走势图')
        c.setLineWidth(0.5)
        c.line(10, h * 0.65 - 4, w - 10, h * 0.65 - 4)

        # 插入日线macd图
        try:
            image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'd_' + stk_code + '.png')
            c.drawImage(ImageReader(image_file), x=w * 0.05, y=h * 0.35, height=0.3 * h, width=0.45 * w,
                        preserveAspectRatio=True)
        except Exception as e:
            print('函数print_k_to_pdf：出错！\n' + str(e))

        # 插入日线指标图
        try:
            image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'd_idx_' + stk_code + '.png')
            c.drawImage(ImageReader(image_file), x=w * 0.5, y=h * 0.35, height=0.3 * h, width=0.45 * w,
                        preserveAspectRatio=True)
        except Exception as e:
            print('函数print_k_to_pdf：出错！\n' + str(e))

        """ --------------------------------- 打印周月线图片 ------------------------------------ """

        c.setFont("song", 10)
        c.drawString(20, h * 0.35, stk_code + ' ' + code2name(stk_code) + ' ' + '周/月走势图')
        c.setLineWidth(0.5)
        c.line(10, h * 0.35 - 4, w - 10, h * 0.35 - 4)

        # 插入周线图
        try:
            image_file = PIL.Image.open(sea_select_pic_dir + date + '/' + 'wm_' + stk_code + '.png')
            c.drawImage(ImageReader(image_file), x=w * 0.05, y=h * 0.05, height=0.3 * h, width=0.45 * w,
                        preserveAspectRatio=True)
        except Exception as e:
            print('函数print_k_to_pdf：出错！\n' + str(e))

        c.showPage()

        return c

    def gen_sea_select_pic(self, stk_list_ss):
        """
        打印图片
        :param stk_list_ss:
        :return:
        """
        for stk in stk_list_ss:

            # 将选定的股票的走势图打印到本地
            self.gen_stk_sea_select_pic_sub(stk.stk_code)

    @staticmethod
    def gen_stk_sea_select_pic_sub(stk_code):

        try:
            jq_login()

            # 保存路径
            save_dir = sea_select_pic_dir + get_current_date_str() + '/'

            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 准备 小时 和 日线 数据
            df_hour = gen_hour_macd_values(stk_code)
            df_day = get_k_data_JQ(stk_code, 800)

            # 定义图片名称
            file_name = stk_code + '.png'

            # 生成小时图片
            gen_hour_macd_pic_local(df_hour, stk_code, 'jq', '', save_dir + 'h_' + file_name)
            gen_hour_index_pic_local(df_hour[0], stk_code, save_dir + 'h_idx_' + file_name)
            gen_day_pic_local(df_day, stk_code, save_dir + 'd_' + file_name)
            gen_w_m_macd_pic_local(df_day, stk_code, save_dir + 'wm_' + file_name)
            gen_idx_pic_local(df_day, stk_code, save_dir + 'd_idx_' + file_name)

        except Exception as e:
            print('生成股票走势图失败！原因：\n' + str(e))
        finally:
            logout()

    def gen_pdf(self, stk_list_ss, pdf_save_dir):
        """
        生成相应pdf
        :return:
        """
        # 生成pdf
        c = canvas.Canvas(pdf_save_dir + U"魔灯海选" + get_current_date_str() + ".pdf", pagesize=letter)
        c = add_front(c, '魔灯每日股票海选结果' + get_current_date_str(), '本文档由免费开源的量化投资软件“魔灯”自动生成 末尾公众号内有软件介绍', pagesize=letter)
        for stk in stk_list_ss:
            c = print_k_to_pdf(c, stk.stk_code, get_current_date_str())
        c = self.add_tail_page(c)
        c.save()
