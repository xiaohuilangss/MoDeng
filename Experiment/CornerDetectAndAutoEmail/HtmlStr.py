# encoding = utf-8

"""
该文本用于拆解HTML字符串

"""

# 综述当中要展示的内容
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

H_Head = \
"""

    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=GB2312">
            <title> Auto report when a corner pot is detected! </title>
        </head>
        
        <br><br><br><br>
        <hr />

"""


def genH_Intro(C_Instro):
    """
    前述字符串
    :param C_Instro:
    :return:
    """

    H_Intro = \
        """
                    <body>
                    <p> 当前处于 “拐点”的STK 有：</p>
        """ \
        + "<p>" + C_Instro + "</p>" + \
        """
                    <br><br><br><br></body>
        """

    return H_Intro


def gen_H_Unit(stk_code, stk_name, pic_dir):
    """
    单位模块字符串
    :param stk_code:        stk代码
    :param pic_AC_ID:       类似 "stk_ave.png"
    :param pic_M_ID:        类似 "stk_MACD.png"
    :return:
    """

    H_Unit = \
    """
                <HR style="FILTER: progid:DXImageTransform.Microsoft.Shadow(color:#987cb9,direction:145,strength:15)" width="100%" color=#987cb9 SIZE=5>
                <body>
                    <h1> """ + str(stk_code)+ ' ' + stk_name +""" </h1><br /><br />
    
                    <p> AVE/Close/MACD: </p>
                    <img src= "cid:""" + pic_dir.replace('.png', '') + '"' + """  alt="ave+close"/>
    
                </body>
    """

    return H_Unit



H_tail = "</html>"



def addInfoToMsg(msg, html_str, date, pic_dir):

    # 将html字符串添加到邮件msg中
    msg.attach(MIMEText(html_str, 'html', 'utf-8'))

    # 测试添加png类型的图片
    fp_ave = open(pic_dir, 'rb')
    msgImage_ave = MIMEImage(fp_ave.read())

    msgImage_ave.add_header('Content-ID', '<' + pic_dir.replace() + '>')
    msg.attach(msgImage_ave)
    fp_ave.close()




""" --------------------- 测试代码 ------------------------ """

"""
测试方式：
将字符串保存到文件中，并命名为html格式
"""
#
# html_str = H_Head + genH_Intro('300508')+\
#            gen_H_Unit(
#     '300508',
#     '东软载波',
#     '2019-02-15',
#     "stk_ave.png",
#     "stk_MACD.png")\
# + gen_H_Unit(
#     '300508',
#     '东软载波',
#     '2019-02-15',
#     "stk_ave.png",
#     "stk_MACD.png")
#
#
# f = open("C:/Users/Administrator/Desktop/html练习2.htm", 'w')
#
# f.write(html_str)
# f.close()

# end=0