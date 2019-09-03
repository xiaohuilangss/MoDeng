# encoding = utf-8

import tornado
from apscheduler.schedulers.tornado import TornadoScheduler
sched = TornadoScheduler()

""" 测试向任务中传入参数 """
test = 'hello'

def job1(a, b, c):
    print("job1:", a,b,c)


def job2(a, b, c):
    print("job2:", a,b,c)


sched.add_job(job1, 'interval', seconds=1, args=["e", "t", "f"])
sched.add_job(job2, 'interval', seconds=1, kwargs={"a": test, "b": "b", "c": "c"})
sched.start()

tornado.ioloop.IOLoop.instance().start()
