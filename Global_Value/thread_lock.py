# encoding=utf-8

"""

"""
import threading

# 操作记录锁
opt_record_lock = threading.Lock()

# 操作记录变量写入锁
opt_lock = threading.Lock()
