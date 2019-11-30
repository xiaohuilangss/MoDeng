# encoding=utf-8

import multiprocessing

import time


def foo(sk):
	while True:
	    sk.send('hello dad')
	    print('子：' + sk.recv())


if __name__ == '__main__':
    conn1, conn2 = multiprocessing.Pipe()                       # 开辟两个口，都是能进能出，括号中如果False即单向通信
    p = multiprocessing.Process(target=foo, args=(conn1,))      # 子进程使用sock口，调用foo函数
    p.start()
    
    while True:
	    print('主：' + conn1.recv())                # 主进程使用conn口接收
	    conn1.send('hi son')                                        # 主进程使用conn口发送
	    
	    time.sleep(2)