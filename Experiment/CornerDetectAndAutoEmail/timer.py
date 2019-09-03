# enconding = utf-8

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
sched.add_job(func=MACD_Report, trigger='cron', day_of_week='mon-sat', hour=5, minute=0)
sched.add_job(func=update_k, trigger='cron', day_of_week='mon-sat', hour=6, minute=30)
sched.start()