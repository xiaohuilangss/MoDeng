# enconding = utf-8

from apscheduler.schedulers.blocking import BlockingScheduler

from Auto_Report.ReportLab.test1 import send_basic_email
from Config.GlobalSetting import conn_k
from Experiment.LoadHistoryData import update_K_data
from Test.MACD_Timer import macd_test_daily


def MACD_Report():
    macd_test_daily()

def update_k():
    update_K_data()
    conn_k.commit()
    send_basic_email()


# 下面这几行代码用于手动执行使用，使用定时器时记得将其屏蔽
macd_test_daily()
update_K_data()
conn_k.commit()
send_basic_email()

sched = BlockingScheduler()
sched.add_job(func=MACD_Report, trigger='cron', day_of_week='mon-sat', hour=5, minute=0)
sched.add_job(func=update_k, trigger='cron', day_of_week='mon-sat', hour=6, minute=30)
sched.start()