# encoding=utf-8

#coding=utf-8
import threading
from time import ctime, sleep


def music(func):
    for i in range(2):
        print("我在听歌： %s. %s" %(func, ctime()))
        sleep(1)


def move(func):
    for i in range(2):
        print("我在看电影： %s! %s" % (func, ctime()))
        sleep(5)

threads = []
t1 = threading.Thread(target=music, args=(u'爱情买卖',))
threads.append(t1)
t2 = threading.Thread(target=move, args=(u'阿凡达',))
threads.append(t2)

if __name__ == '__main__':
    for t in threads:
        t.setDaemon(True)
        t.start()

    print("所有任务结束！ %s" %ctime())