# encoding = utf-8

from reportlab.pdfgen import canvas
from Auto_Report.ReportLab.SubFunction import *

c = canvas.Canvas("day报告1.pdf", pagesize=letter)


# 下载数据
quarter_gdp = ts.get_gdp_quarter()
gdp_pot = ExtractPointFromDf_DateX(df_origin=quarter_gdp,date_col='quarter',y_col='gdp',quarter=True)

gdp_drawing = genLPDrawing([tuple(gdp_pot)],['gdp'],quarter=True)

renderPDF.draw(drawing=gdp_drawing, canvas=c, x=10, y=letter[1] * 0.6)

c.showPage()
c.save()






