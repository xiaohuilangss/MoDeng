# encoding = utf-8
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from Experiment.Auto_Report.ReportLab.SubFunction import RPL_Bk_Page
from SDK.MyTimeOPT import get_current_date_str

c = canvas.Canvas(U"SingleStock" + get_current_date_str() + ".pdf", pagesize=letter)
c = RPL_Bk_Page(c, '300508')

c.save()
