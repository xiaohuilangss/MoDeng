import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger


def day_limits():
        variable.value = 90
        print ('Day Variable: ',variable.value)

def night_limits():
        variable.value = 65
        print ('Night Variable: ', variable.value)


def thread_2(variable):
    while True:
        c_hour = int(datetime.now().strftime("%H"))
        c_min = int(datetime.now().strftime("%M"))
        c_sec = int(datetime.now().strftime("%S"))

        print ('%02d:%02d:%02d - Variable: %d ' % (c_hour,c_min,c_sec,variable.value))

        time.sleep(2)


if __name__ == "__main__":

    m = multiprocessing.Manager()
    variable = m.Value('i', 60)

    schedfortest = BlockingScheduler()

    trigger_test = OrTrigger([
        CronTrigger(minute='*/1')
    ])

    schedfortest.add_job(callbacktotal,
                          trigger_test,
                          minute='*/2',
                          max_instances=10)

    schedfortest.start()





    scheduler = AsyncIOScheduler()
    scheduler.add_job(day_limits, 'cron', hour=7,misfire_grace_time=3600,timezone='GB')
    scheduler.add_job(night_limits, 'cron', hour=19, minute=32,misfire_grace_time=3600,timezone='GB')
    scheduler.start()

    scheduler.print_jobs()

    executor = ProcessPoolExecutor(1)
    loop = asyncio.get_event_loop()
    baa = asyncio.async(loop.run_in_executor(executor, thread_2, variable))  # Need to pass variable explicitly

    try:
        loop.run_forever()

    except (KeyboardInterrupt, Exception):
        loop.stop()
        scheduler.shutdown()