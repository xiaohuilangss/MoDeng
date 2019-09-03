# encoding=utf-8
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd

""" 测试向任务中传入参数 """
test = pd.DataFrame({'test': [1, 2, 3, 4]})

def job1(a, b, c):
    print("job1:", str(a), b, c)


def job2(a, b, c):
    print("job2:", a, b, c)


sched = BlockingScheduler()
sched.add_job(func=job1, trigger='cron', day_of_week='mon-sat', minute='*/1', args=[test, "t", "f"])
# sched.add_job(func=job2, trigger='cron', day_of_week='mon-sat', hour=6, minute=30)
sched.start()
