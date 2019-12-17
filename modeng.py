# encoding=utf-8

if __name__ == '__main__':

	# try:

	""" =========================== 将当前路径及工程的跟目录添加到路径中，必须在文件头部，否则易出错 ============================ """

	import sys
	import os

	curPath = os.path.abspath(os.path.dirname(__file__))
	if "MoDeng" in curPath:
		rootPath = curPath[:curPath.find("MoDeng\\") + len("MoDeng\\")]  # 获取myProject，也就是项目的根路径
	elif "MoDeng-master" in curPath:
		rootPath = curPath[:curPath.find("MoDeng-master\\") + len("MoDeng-master\\")]  # 获取myProject，也就是项目的根路径
	else:
		input('没有找到项目的根目录！请检查项目根文件夹的名字！')
		exit(1)

	sys.path.append('..')
	sys.path.append(rootPath)

	import multiprocessing as mp

	from Function.GUI.GUI_main.Sub import run_myframe_in_process
	from Function.GUI.GUI_main.Thread_Sub import data_process_callback
	from Config.AutoGenerateConfigFile import checkConfigFile

	# 检查配置文件
	checkConfigFile()

	# 定义管道
	pipe_master, pipe_proc = mp.Pipe()

	# 启动主进程
	process = mp.Process(target=run_myframe_in_process, args=(pipe_master, True))
	process.start()

	# 启动处理循环
	data_process_callback(pipe_proc, debug=False)

	# except Exception as e:
		# print('出错！错误：\n' + str(e) + '\n')

		# a = input('请关闭！')
