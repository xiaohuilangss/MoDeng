# encoding=utf-8
import pickle
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from CornerDetectAndAutoEmail.AveMaxMinDetect.Global import h_l_pot_info_url
from CornerDetectAndAutoEmail.AveMaxMinDetect.MaxMin import judgeAndSendMsg, updatePotInfo
from SDK.MyTimeOPT import get_current_datetime_str


def time_now():
    print(str(get_current_datetime_str()))

trigger = OrTrigger([
    CronTrigger(hour='11', minute='1-59/3')
])

sched = BlockingScheduler()
sched.add_job(time_now,
              trigger,
              day_of_week='mon-fri',
              max_instances=10)

sched.start()