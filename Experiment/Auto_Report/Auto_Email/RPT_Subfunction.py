# encoding = utf-8

"""
reportlab常用依赖
"""
import random

import pandas as pd
import numpy as np
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

from reportlab.lib.pagesizes import letter

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet

# 画图相关
from reportlab.graphics.shapes import Drawing, PolyLine, colors, Auto
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker


from reportlab.pdfbase.pdfmetrics import stringWidth

# styles=getSampleStyleSheet()
#
# HeaderStyle = styles["Heading1"]
# ParaStyle = styles["Normal"]
#
# # 定义中文字体
# styles_chs = copy.deepcopy(styles['Normal'])
# styles_chs.fontName = 'song'
# styles_chs.fontSize = 20


# 中文字体
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


pdfmetrics.registerFont(TTFont('song', 'SURSONG.TTF'))
pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))

from reportlab.lib import fonts
fonts.addMapping('song', 0, 0, 'song')
fonts.addMapping('song', 0, 1, 'song')
fonts.addMapping('song', 1, 0, 'hei')
fonts.addMapping('song', 1, 1, 'hei')



"""
# 本脚本是一些与reportlab包有关的子函数
# 同时也设置reportlab中常用的一些import，其他文件可以通过import该文件来方便地引入常用依赖
"""


def addFront(canvas_param, theme, subtitle, pagesize=letter):
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
    canvas_param.setFont("song", 10)
    canvas_param.drawString((PAGE_WIDTH-stringWidth(theme, fontName='song', fontSize=30))/2.0, PAGE_HEIGHT*0.15, subtitle)

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
    legend.x = pos_x
    legend.y = pos_y
    legend.colorNamePairs = Auto(obj=chart)
    draw_obj.add(legend)

