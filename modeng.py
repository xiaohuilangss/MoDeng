# encoding=utf-8
import multiprocessing as mp

from Function.GUI.GUI_main.Sub import run_myframe_in_process
from Function.GUI.GUI_main.Thread_Sub import data_process_callback

if __name__ == '__main__':
	
	# 定义管道
	pipe_master, pipe_proc = mp.Pipe()
	
	# 启动主进程
	process = mp.Process(target=run_myframe_in_process, args=(pipe_master, False))
	process.start()
	
	# 启动处理循环
	data_process_callback(pipe_proc, debug=False)
