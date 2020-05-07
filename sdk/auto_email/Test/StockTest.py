# enconding = utf-8


from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from reportlab.lib.pagesizes import letter


PAGE_HEIGHT = letter[1]
import sys
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet


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

import copy



# ==============================================
styles=getSampleStyleSheet()

HeaderStyle = styles["Heading1"]
ParaStyle = styles["Normal"]

# 定义中文字体
styles_chs = copy.deepcopy(styles['Normal'])
styles_chs.fontName = 'song'
styles_chs.fontSize = 20


# ==============================================


c = canvas.Canvas("test_pdfgen_links.pdf", pagesize=letter)


# Page 1
c.setFont("song", 10)

page_n = 1

