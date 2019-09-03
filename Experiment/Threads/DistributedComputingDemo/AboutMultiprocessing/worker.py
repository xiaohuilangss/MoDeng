#coding:utf-8
import time
from multiprocessing.managers import BaseManager


# 创建类似的QueueManager:
class QueueManager(BaseManager):
    pass

# 实现第一步：使用QueueManager注册获取Queue的方法名称
QueueManager.register('get_task_queue')
QueueManager.register('get_result_queue')

# 实现第二步：连接到服务器:
server_addr = '127.0.0.1'
print('Connect to server %s...' % server_addr)

# 端口和验证口令注意保持与服务进程设置的完全一致:
m = QueueManager(address=(server_addr, 8001), authkey='lsf')

# 从网络连接:
m.connect()

# 实现第三步：获取Queue的对象:
task = m.get_task_queue()
result = m.get_result_queue()

# 实现第四步：从task队列取任务,并把结果写入result队列:
while not task.empty():
        image_url = task.get(True, timeout=5)
        print('run task download %s...' % image_url)
        time.sleep(1)
        result.put('%s--->success'% image_url)

# 处理结束:
print('worker exit.')