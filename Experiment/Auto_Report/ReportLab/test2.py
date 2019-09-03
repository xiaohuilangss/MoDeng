# encoding = utf-8

from Auto_Report.ReportLab.SubFunction import *
import tushare as ts

sh_index = ts.get_hist_data('cyb')
sh_index['date'] = sh_index.index
sh_index = sh_index.reset_index(drop=True)

close = ExtractPointFromDf_DateX(sh_index,'date', 'close')
m5 = ExtractPointFromDf_DateX(sh_index,'date', 'm5')
m10 = ExtractPointFromDf_DateX(sh_index,'date', 'm10')
m20 = ExtractPointFromDf_DateX(sh_index,'date', 'm20')


end = 0