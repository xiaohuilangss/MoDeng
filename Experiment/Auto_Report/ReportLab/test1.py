# encoding = utf-8
from Auto_Report.Auto_Email.Email_SendPdf import loadPickle, sendMail
from SDK.MyTimeOPT import get_current_date_str
import os

# 更新K数据


# ======================================== 创建画布信息 ====================================
from reportlab.pdfgen import canvas

from Auto_Report.ReportLab.SubFunction import *

def send_basic_email():

    width = letter[0]
    height = letter[1]

    c = canvas.Canvas(U"A股日报" + get_current_date_str() + ".pdf", pagesize=letter)
    c.setFont("song", 10)
    page_n = 1


    # ========================================= 进行画图 ========================================

    # 增加封面
    c = addFront(canvas_param=c, theme='中国A股日度数据展示', subtitle='')

    # ========================================= 开始画大盘图 =====================================
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('大盘', "P" + str(page_n), closed=1,level=0)
    page_n += 1

    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('上证指数', "P" + str(page_n), closed=1,level=1)

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '上证指数')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)
    c = RPL_Bk_Page(c,'sh')
    page_n += 1


    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('深证指数', "P" + str(page_n), closed=1,level=1)

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '深证指数')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)
    c = RPL_Bk_Page(c,'sz')
    page_n += 1

    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('创业板', "P" + str(page_n), closed=1,level=1)

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '创业板')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)
    c = RPL_Bk_Page(c,'cyb')
    page_n += 1

    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('上证50', "P" + str(page_n), closed=1,level=1)

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '上证50')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)
    c = RPL_Bk_Page(c,'sz50')
    page_n += 1

    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('沪深300', "P" + str(page_n), closed=1,level=1)

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '沪深300')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)
    c = RPL_Bk_Page(c,'hs300')
    page_n += 1

    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('中小板', "P" + str(page_n), closed=1,level=1)

    c.setFont("song", 10)
    c.drawString(10, letter[1] - 20, '中小板')
    c.setLineWidth(3)
    c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)
    c = RPL_Bk_Page(c,'zxb')
    page_n += 1



    # ========================================= 画行业图 =====================================

    # 建一级目录
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('行业走势', "P" + str(page_n), closed=1,level=0)
    page_n += 1

    date_start = add_date_str(get_current_date_str(),-1080)
    date_end = get_current_date_str()

    industry_data_list = cal_industry_index(date_start,date_end)

    for ids in industry_data_list:
        c_name = ids['c_name']

        c_data = ids['c_data']
        if len(c_data) > 0:

            # 添加书签
            c.bookmarkPage("P" + str(page_n))
            c.addOutlineEntry(c_name, "P" + str(page_n), closed=1,level=1)
            page_n += 1

            c.setFont("song", 10)
            c.drawString(10, letter[1] - 20, c_name)
            c.setLineWidth(3)
            c.line(10, letter[1] - 24, letter[0] - 10, letter[1] - 24)


            # 准备画图数据
            c_data['date'] = c_data.index
            ids = ExtractPointFromDf_DateX(c_data, 'date', 'industry_index')

            data = [tuple(ids)]
            data_name = [c_name]

            drawing_ave = genLPDrawing(data=data, data_note=data_name, height=letter[1] * 0.3)
            renderPDF.draw(drawing=drawing_ave, canvas=c, x=10, y=letter[1] * 0.6)

            c.showPage()

        else:
            print('行业'+c_name+' 没有数据，无法打印走势图！')


    # ========================================= 画宏观经济图 =====================================

    # 建一级目录
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('宏观数据', "P" + str(page_n), closed=1, level=0)
    page_n += 1

    # 货币供应
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('货币供应', "P" + str(page_n), closed=1, level=1)
    page_n += 1

    c = addMoneySupplyPage(c)

    # 存款准备金基率
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('准备金基率', "P" + str(page_n), closed=1, level=1)
    page_n += 1

    c = addReserveBaseRatePage(c)

    # gdp
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('季度GDP', "P" + str(page_n), closed=1, level=1)
    page_n += 1

    c = addQuarterGDPPage(c)

    # 三大产业对GDP的拉动
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('三大产业对GDP的拉动', "P" + str(page_n), closed=1,level=1)
    page_n += 1

    c = addDemandsForGDPPage(c)

    # CPI
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('月度CPI', "P" + str(page_n), closed=1, level=1)
    page_n += 1
    c = addCPIPage(c,50)

    # PPI
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('月度PPI', "P" + str(page_n), closed=1, level=1)
    page_n += 1
    c = addPPIPage(c,50)

    # 建一级目录
    # c.bookmarkPage("P" + str(page_n))
    # c.addOutlineEntry('银行拆借利率', "P" + str(page_n), closed=1,level=0)
    # page_n += 1

    # shibor拆放利率
    # c.bookmarkPage("P" + str(page_n))
    # c.addOutlineEntry('Shibor拆放利率', "P" + str(page_n), closed=1, level=1)
    # page_n += 1
    #
    # c = addShiborPage(c)

    # 贷款利率
    # c.bookmarkPage("P" + str(page_n))
    # c.addOutlineEntry('银行贷款利率', "P" + str(page_n), closed=1, level=1)
    # page_n += 1
    #
    # c = addLprPage(c)
    #


    # 建一级目录
    c.bookmarkPage("P" + str(page_n))
    c.addOutlineEntry('尾注', "P" + str(page_n), closed=1, level=0)
    page_n += 1

    c = addTailPage(c)

    c.save()


    # ================================ 发送邮件 =====================================

    senderInfo = loadPickle(os.path.basename('.'), "senderInfo.txt")
    sender = senderInfo.split("?")[0]               # 发件人邮箱
    password = senderInfo.split("?")[1]             # 发件人邮箱密码
    # recipient = senderInfo.split("?")[2]            # 收件人邮箱
    # recipient = [recipient[2:-2]]                   # 将string格式的"['收件人邮箱']"转换成['收件人邮箱']


    # recipient = ['1234567@qq.com',
    #              '3303366489@qq.com',
    #              '2314923644@qq.com',
    #              '3122140480@qq.com',
    #              '1959148913@qq.com',
    #              '2384205754@qq.com',
    #              '2959544903@qq.com',
    #              '1156668277@qq.com',
    #              '2624822992@qq.com',
    #              '1170200744@qq.com',
    #              '313201657@qq.com',
    #              '2897475285@qq.com']

    recipient = ['189916591@qq.com']
    sendMail("A股日报" + get_current_date_str(), recipient, '', U"A股日报" + get_current_date_str() + ".pdf")






