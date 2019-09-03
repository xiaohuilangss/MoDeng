
# !/usr/bin/env python3
# coding: utf-8
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

sender = '189916591@qq.com'
receiver = '1234567@qq.com'
subject = 'python email test'
smtpserver = 'smtp.qq.com'
username = '189916591@qq.com'
password = 'tetwlkdappggcaej'
msgRoot = MIMEMultipart('related')
msgRoot['Subject'] = 'mini message'
msgRoot['From'] = sender
msgRoot['To'] = receiver


msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>good!', 'html', 'utf-8')
# msgText = MIMEText('很好', 'plain', 'utf-8')

msgRoot.attach(msgText)


# buf = io.BytesIO()
# plt.plot()
# plt.savefig(buf,format='png')
# buf.seek(0)
# msgImage = MIMEImage(buf.read())

fp = open("C:/Users/paul/Desktop/6.png", 'rb')
msgImage = MIMEImage(fp.read())
fp.close()
msgImage.add_header('Content-ID', '<image1>')
msgRoot.attach(msgImage)

smtp = smtplib.SMTP()
smtp.connect(smtpserver)
smtp.login(username, password)
smtp.sendmail(sender, receiver, msgRoot.as_bytes())
smtp.quit()