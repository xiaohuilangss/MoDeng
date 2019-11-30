# encoding = utf-8
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from Experiment.Auto_Report.ReportLab.SubFunction import rpl_stk_page, rpl_stk_hour_page
from SDK.MyTimeOPT import get_current_date_str
if __name__ == '__main__':
 
	from DataSource.auth_info import *
	
	c = canvas.Canvas(U"SingleStock" + get_current_date_str() + ".pdf", pagesize=letter)
	c = rpl_stk_hour_page(c, '300508')
	
	c.save()
