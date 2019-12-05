# encoding=utf-8

import time
from multiprocessing import Process, Queue, Pool, Manager, Pipe


def producer(pipe):
	while True:
		
		pipe.send("a1")
		pipe.send("a2")
		pipe.send("a3")
		pipe.send("a4")
		pipe.send("a5")
		
		print('发送了a\n')
		
		if pipe.recv() == 'c':
			time.sleep(30)
			print('收到c\n')
			

def consumer(pipe):
	while True:
		pipe.send("b")
		print('发送了b\n')
		data = pipe.recv()
		
		if 'a' in data:
			# time.sleep(3)
			print('收到' + str(data))
			
		
if __name__ == "__main__":
	
	# Pipe实现两进程间通信
	s_pipe, r_pipe = Pipe()
	pool = Pool()
	pool.apply_async(producer, args=(s_pipe,))
	pool.apply_async(consumer, args=(r_pipe,))
	pool.close()
	pool.join()
