# -*- encoding: utf8 -*-
# version 1.11

import tkinter.messagebox,os
from tkinter import *
from tkinter.ttk import *
from tkinter import Menu
import datetime
import threading
import pickle
import time
import tushare as ts
import pywinauto
import pywinauto.clipboard
import pywinauto.application
NUM_OF_STOCKS = 5  # 自定义股票数量
is_start = False
is_monitor = True
set_stocks_info = []
actual_stocks_info = []
consignation_info = []
is_ordered = [1] * NUM_OF_STOCKS  # 1：未下单  0：已下单
is_dealt = [0] * NUM_OF_STOCKS  # 0: 未成交   负整数：卖出数量， 正整数：买入数量
stock_codes = [''] * NUM_OF_STOCKS

class OperationThs:
    def __init__(self):
        try:
            self.__app = pywinauto.application.Application()
            self.__app.connect(title='网上股票交易系统5.0')
            top_hwnd = pywinauto.findwindows.find_window(title='网上股票交易系统5.0')
            dialog_hwnd = pywinauto.findwindows.find_windows(top_level_only=False, class_name='#32770', parent=top_hwnd)[0]
            # wanted_hwnds = pywinauto.findwindows.find_windows(top_level_only=False, parent=dialog_hwnd)
            # print('wanted_hwnds length', len(wanted_hwnds))
            # if len(wanted_hwnds) not in (99,97,96,98,100,101):
            #     tkinter.messagebox.showerror('错误', '无法获得“同花顺双向委托界面”的窗口句柄,请将同花顺交易系统切换到“双向委托界面”！')
            #     exit()
            self.__main_window = self.__app.window_(handle=top_hwnd)
            self.__dialog_window = self.__app.window_(handle=dialog_hwnd)
        except:
            pass

    def __buy(self, code, quantity):
        """买函数
        :param code: 代码， 字符串
        :param quantity: 数量， 字符串
        """
        self.__dialog_window.Edit1.SetFocus()
        time.sleep(0.2)
        self.__dialog_window.Edit1.SetEditText(code)
        time.sleep(0.2)
        if quantity != '0':
            self.__dialog_window.Edit3.SetEditText(quantity)
            time.sleep(0.2)
        self.__dialog_window.Button1.Click()
        time.sleep(0.2)

    def __sell(self, code, quantity):
        """
        卖函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        self.__dialog_window.Edit4.SetFocus()
        time.sleep(0.2)
        self.__dialog_window.Edit4.SetEditText(code)
        time.sleep(0.2)
        if quantity != '0':
            self.__dialog_window.Edit6.SetEditText(quantity)
            time.sleep(0.2)
        self.__dialog_window.Button2.Click()
        time.sleep(0.2)

    def __closePopupWindow(self):
        """
        关闭一个弹窗。
        :return: 如果有弹出式对话框，返回True，否则返回False
        """
        popup_hwnd = self.__main_window.PopupWindow()
        if popup_hwnd:
            popup_window = self.__app.window_(handle=popup_hwnd)
            popup_window.SetFocus()
            popup_window.Button.Click()
            return True
        return False

    def __closePopupWindows(self):
        """
        关闭多个弹出窗口
        :return:
        """
        while self.__closePopupWindow():
            time.sleep(0.5)

    def order(self, code, direction, quantity):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向， 字符串
        :param quantity: 买卖数量， 字符串
        """
        if direction == 'B':
            self.__buy(code, quantity)
        if direction == 'S':
            self.__sell(code, quantity)
        self.__closePopupWindows()

    def maxWindow(self):
        """
        最大化窗口
        """
        if self.__main_window.GetShowState() != 3:

            self.__main_window.Maximize()
        self.__main_window.SetFocus()

    def minWindow(self):
        """
        最小化窗体
        """
        if self.__main_window.GetShowState() != 2:
            self.__main_window.Minimize()

    def refresh(self, t=0.5):
        """
        点击刷新按钮
        :param t:刷新后的等待时间
        """
        self.__dialog_window.Button5.Click()
        time.sleep(t)

    def getMoney(self):
        """
        获取可用资金
        """
        return float(str(self.__dialog_window.Static19.WindowText()))

    @staticmethod
    def __cleanClipboardData(data, cols=11):
        """
        清洗剪贴板数据
        :param data: 数据
        :param cols: 列数
        :return: 清洗后的数据，返回列表
        """
        lst = data.strip().split()[:-1]
        matrix = []
        for i in range(0, len(lst) // cols):
            matrix.append(lst[i * cols:(i + 1) * cols])
        return matrix[1:]

    def __copyToClipboard(self):
        """
        拷贝持仓信息至剪贴板
        :return:
        """
        self.__dialog_window.CVirtualGridCtrl.RightClick(coords=(30, 30))
        self.__main_window.TypeKeys('C')

    def __getCleanedData(self):
        """
        读取ListView中的信息
        :return: 清洗后的数据
        """
        self.__copyToClipboard()
        data = pywinauto.clipboard.GetData()
        return self.__cleanClipboardData(data)

    def __selectWindow(self, choice):
        """
        选择tab窗口信息
        :param choice: 选择个标签页。持仓，撤单，委托，成交
        :return:
        """
        rect = self.__dialog_window.CCustomTabCtrl.ClientRect()
        x = rect.width() // 8
        y = rect.height() // 2
        if choice == 'W':
            x = x
        elif choice == 'E':
            x *= 3
        elif choice == 'R':
            x *= 5
        elif choice == 'A':
            x *= 7
        self.__dialog_window.CCustomTabCtrl.ClickInput(coords=(x, y))
        time.sleep(0.5)

    def __getInfo(self, choice):
        """
        获取股票信息
        """
        self.__selectWindow(choice=choice)
        return self.__getCleanedData()

    def getPosition(self):
        """
        获取持仓
        :return:
        """
        return self.__getInfo(choice='W')

    @staticmethod
    def getDeal(code, pre_position, cur_position):
        """
        获取成交数量
        :param code: 需检查的股票代码， 字符串
        :param pre_position: 下单前的持仓
        :param cur_position: 下单后的持仓
        :return: 0-未成交， 正整数是买入的数量， 负整数是卖出的数量
        """
        if pre_position == cur_position:
            return 0
        pre_len = len(pre_position)
        cur_len = len(cur_position)
        if pre_len == cur_len:
            for row in range(cur_len):
                if cur_position[row][0] == code:
                    return int(float(cur_position[row][1]) - float(pre_position[row][1]))
        if cur_len > pre_len:
            return int(float(cur_position[-1][1]))

    def withdraw(self, code, direction):
        """
        指定撤单
        :param code: 股票代码
        :param direction: 方向 B， S
        :return:
        """
        row_pos = []
        info = self.__getInfo(choice='R')
        if direction == 'B':
            direction = '买入'
        elif direction == 'S':
            direction = '卖出'
        if info:
            for index, element in enumerate(info):
                if element[0] == code:
                    if element[1] == direction:
                        row_pos.append(index)
        if row_pos:
            for row in row_pos:
                self.__dialog_window.CVirtualGridCtrl.ClickInput(coords=(7, 28 + 16 * row))
            self.__dialog_window.Button12.Click()
            self.__closePopupWindows()

    def withdrawBuy(self):
        """
        撤买
        :return:
        """
        self.__selectWindow(choice='R')
        self.__dialog_window.Button8.Click()
        self.__closePopupWindows()

    def withdrawSell(self):
        """
        撤卖
        :return:
        """
        self.__selectWindow(choice='R')
        self.__dialog_window.Button9.Click()
        self.__closePopupWindows()

    def withdrawAll(self):
        """
        全撤
        :return:
        """
        self.__selectWindow(choice='R')
        self.__dialog_window.Button7.Click()
        self.__closePopupWindows()



def monitor():
    """
    实时监控函数
    """
    global actual_stocks_info, consignation_info, is_ordered, is_dealt, set_stocks_info
    count = 1
    pre_position = []
    try:
        operation = OperationThs()
        operation.maxWindow()
        pre_position = operation.getPosition()
        # print(pre_position)
        while is_monitor:
            if is_start:
                actual_stocks_info = getStockData()
                for row, (actual_code, actual_name, actual_price) in enumerate(actual_stocks_info):
                    if actual_code and is_start and is_ordered[row] == 1 and actual_price > 0 \
                            and set_stocks_info[row][1] and set_stocks_info[row][2] > 0 \
                            and set_stocks_info[row][3] and set_stocks_info[row][4] \
                            and datetime.datetime.now().time() > set_stocks_info[row][5]:
                        if (set_stocks_info[row][1] == '>' and actual_price > set_stocks_info[row][2]) or \
                                (set_stocks_info[row][1] == '<' and float(actual_price) < set_stocks_info[row][2]):
                            operation.maxWindow()
                            operation.order(actual_code, set_stocks_info[row][3], set_stocks_info[row][4])
                            dt = datetime.datetime.now()
                            is_ordered[row] = 0
                            operation.refresh()
                            cur_position = operation.getPosition()
                            is_dealt[row] = operation.getDeal(actual_code, pre_position, cur_position)
                            consignation_info.append(
                                (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                                 actual_name, set_stocks_info[row][3],
                                 actual_price, set_stocks_info[row][4], '已委托', is_dealt[row]))
                            pre_position = cur_position
            if count % 200 == 0:
                operation.refresh()
            time.sleep(3)
            count += 1

    except:
        tkinter.messagebox.showerror('错误', '请先打开“同花顺双向委托界面”后在打开自动交易系统！')
        sys.exit()

class StockGui:
    global is_monitor
    def __init__(self):
        self.window = Tk()
        self.window.title("自动化交易系统－同花顺")
        # 左上角图标
        self.window.iconbitmap('e:\ico.ico')
        self.window.resizable(0, 0)
        frame1 = Frame(self.window)
        frame1.pack(padx=10, pady=10)
        Label(frame1, text="股票代码", width=8, justify=CENTER).grid(
            row=1, column=1, padx=5, pady=5)
        Label(frame1, text="股票名称", width=8, justify=CENTER).grid(
            row=1, column=2, padx=5, pady=5)
        Label(frame1, text="实时价格", width=8, justify=CENTER).grid(
            row=1, column=3, padx=5, pady=5)
        Label(frame1, text="关系", width=4, justify=CENTER).grid(
            row=1, column=4, padx=5, pady=5)
        Label(frame1, text="设定价格", width=8, justify=CENTER).grid(
            row=1, column=5, padx=5, pady=5)
        Label(frame1, text="方向", width=4, justify=CENTER).grid(
            row=1, column=6, padx=5, pady=5)
        Label(frame1, text="数量", width=8, justify=CENTER).grid(
            row=1, column=7, padx=5, pady=5)
        Label(frame1, text="时间可选", width=8, justify=CENTER).grid(
            row=1, column=8, padx=5, pady=5)
        Label(frame1, text="委托", width=6, justify=CENTER).grid(
            row=1, column=9, padx=5, pady=5)
        Label(frame1, text="成交", width=6, justify=CENTER).grid(
            row=1, column=10, padx=5, pady=5)
        self.rows = NUM_OF_STOCKS
        self.cols = 10
        self.variable = []
        for row in range(self.rows):
            self.variable.append([])
            for col in range(self.cols):
                self.variable[row].append(StringVar())
        for row in range(self.rows):
            Entry(frame1, textvariable=self.variable[row][0],
                  width=8).grid(row=row + 2, column=1, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][1], state=DISABLED,
                  width=8).grid(row=row + 2, column=2, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][2], state=DISABLED, justify=RIGHT,
                  width=8).grid(row=row + 2, column=3, padx=5, pady=5)
            Combobox(frame1, values=('<', '>'), textvariable=self.variable[row][3],
                     width=2).grid(row=row + 2, column=4, padx=5, pady=5)
            Spinbox(frame1, from_=0, to=999, textvariable=self.variable[row][4], justify=RIGHT,
                    increment=0.01, width=6).grid(row=row + 2, column=5, padx=5, pady=5)
            Combobox(frame1, values=('B', 'S'), textvariable=self.variable[row][5],
                     width=2).grid(row=row + 2, column=6, padx=5, pady=5)
            Spinbox(frame1, from_=0, to=10000, textvariable=self.variable[row][6], justify=RIGHT,
                    increment=100, width=6).grid(row=row + 2, column=7, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][7],
                  width=8).grid(row=row + 2, column=8, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][8], state=DISABLED, justify=CENTER,
                  width=6).grid(row=row + 2, column=9, padx=5, pady=5)
            Entry(frame1, textvariable=self.variable[row][9], state=DISABLED, justify=RIGHT,
                  width=6).grid(row=row + 2, column=10, padx=5, pady=5)

        frame3 = Frame(self.window)
        frame3.pack(padx=10, pady=10)
         # 创建菜单功能
        self.menuBar = Menu(self.window)
        self.window.config(menu=self.menuBar)
        # tearoff=0 代表将菜单项最上面的一条虚线去掉，默认是存在的
        self.fileMenu = Menu(self.menuBar,tearoff=0)
        # 创建一个名为“帮助”的菜单项
        self.menuBar.add_cascade(label="帮助",menu=self.fileMenu)
        # 在“帮助”项下添加一个名为“关于”的选项
        self.fileMenu.add_command(label="关于",command =self.about)
        # 增加一条横线
        self.fileMenu.add_separator()
        # 在“帮助”项下添加一个名为“退出”的选项,并绑定执行函数
        self.fileMenu.add_command(label="退出",command=self.close)
        # 增加第二个导航栏
        # self.helpMenu = Menu(self.menuBar,tearoff=0)
        # self.menuBar.add_cascade(label="Help", menu=self.helpMenu)
        # self.helpMenu.add_command(label="About")
        self.start_bt = Button(frame3, text="开始", command=self.start)
        self.start_bt.pack(side=LEFT)
        self.set_bt = Button(frame3, text='重置买卖', command=self.setFlags)
        self.set_bt.pack(side=LEFT)
        Button(frame3, text="历史记录", command=self.displayHisRecords).pack(side=LEFT)
        Button(frame3, text='保存', command=self.save).pack(side=LEFT)
        self.load_bt = Button(frame3, text='载入', command=self.load)
        self.load_bt.pack(side=LEFT)
        self.window.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.window.after(100, self.updateControls)
        self.window.mainloop()

    def displayHisRecords(self):
        """
        显示历史信息
        """
        global consignation_info
        tp = Toplevel()
        tp.title('历史记录')
        tp.iconbitmap('e:\ico.ico')
        tp.resizable(0, 1)
        scrollbar = Scrollbar(tp)
        scrollbar.pack(side=RIGHT, fill=Y)
        col_name = ['日期', '时间', '证券代码', '证券名称', '方向', '价格', '数量', '委托', '成交']
        tree = Treeview(
            tp, show='headings', columns=col_name, height=30, yscrollcommand=scrollbar.set)
        tree.pack(expand=1, fill=Y)
        scrollbar.config(command=tree.yview)
        for name in col_name:
            tree.heading(name, text=name)
            tree.column(name, width=70, anchor=CENTER)

        for msg in consignation_info:
            tree.insert('', 0, values=msg)
    def save(self):
        """
        保存设置
        """
        global set_stocks_info, consignation_info
        self.getItems()
        with open('stockInfo.dat', 'wb') as fp:
            pickle.dump(set_stocks_info, fp)
            pickle.dump(consignation_info, fp)
    def load(self):
        """
        载入设置
        """
        global set_stocks_info, consignation_info
        try:
            with open('stockInfo.dat', 'rb') as fp:
                set_stocks_info = pickle.load(fp)
                consignation_info = pickle.load(fp)
            for row in range(self.rows):
                for col in range(self.cols):
                    if col == 0:
                        self.variable[row][col].set(set_stocks_info[row][0])
                    elif col == 3:
                        self.variable[row][col].set(set_stocks_info[row][1])
                    elif col == 4:
                        self.variable[row][col].set(set_stocks_info[row][2])
                    elif col == 5:
                        self.variable[row][col].set(set_stocks_info[row][3])
                    elif col == 6:
                        self.variable[row][col].set(set_stocks_info[row][4])
                    elif col == 7:
                        temp = set_stocks_info[row][5].strftime('%X')
                        if temp == '01:00:00':
                            self.variable[row][col].set('')
                        else:
                            self.variable[row][col].set(temp)
        except Exception :
            tkinter.messagebox.showerror('错误', "没有找到配置保存文件，请先进行股票买卖配置信息保存！")
    def setFlags(self):
        """
        重置买卖标志
        """
        global is_start, is_ordered
        if is_start is False:
            is_ordered = [1] * NUM_OF_STOCKS
            tkinter.messagebox.showinfo('重置成功', "重置成功！")
    def updateControls(self):
        """
        实时股票名称、价格、状态信息
        """
        global actual_stocks_info, is_start
        if is_start:
            for row, (actual_code, actual_name, actual_price) in enumerate(actual_stocks_info):
                if actual_code:
                    self.variable[row][1].set(actual_name)
                    self.variable[row][2].set(str(actual_price))
                    if is_ordered[row] == 1:
                        self.variable[row][8].set('监控中')
                    elif is_ordered[row] == 0:
                        self.variable[row][8].set('已委托')
                    self.variable[row][9].set(str(is_dealt[row]))
                else:
                    self.variable[row][1].set('')
                    self.variable[row][2].set('')
                    self.variable[row][8].set('')
                    self.variable[row][9].set('')
        self.window.after(3000, self.updateControls)
    @staticmethod
    def __pickCodeFromItems(items_info):
        """
        提取股票代码
        :param items_info: UI下各项输入信息
        :return:股票代码列表
        """
        stock_codes = []
        for item in items_info:
            stock_codes.append(item[0])
        return stock_codes

    def start(self):
        """
        启动停止
        """
        global is_start, stock_codes, set_stocks_info
        if is_start is False:
            is_start = True
        else:
            is_start = False

        if is_start:
            self.getItems()
            stock_codes = self.__pickCodeFromItems(set_stocks_info)
            self.start_bt['text'] = '停止'
            self.set_bt['state'] = DISABLED
            self.load_bt['state'] = DISABLED
            tkinter.messagebox.showinfo('成功','启动成功！')
        else:
            self.start_bt['text'] = '开始'
            self.set_bt['state'] = NORMAL
            self.load_bt['state'] = NORMAL
    def about(self):
        tkinter.messagebox.showinfo("关于",'\r此系统仅适应于同花顺网上交易5.0，使用时请先登陆同花顺网上交易系统并切换到“同花顺双向委托界面”。\r 版本号：v 1.0.0 \r 作者：水域\r 发布日期：2017.01.11')
    def close(self):
        """
        关闭程序时，停止monitor线程
        """
        global is_monitor
        is_monitor = False
        self.window.quit()

    def getItems(self):
        """
        获取UI上用户输入的各项数据，
        """
        global set_stocks_info
        set_stocks_info = []
        # 获取买卖价格数量输入项等
        for row in range(self.rows):
            set_stocks_info.append([])
            for col in range(self.cols):
                temp = self.variable[row][col].get().strip()
                if col == 0:
                    if len(temp) == 6 and temp.isdigit():  # 判断股票代码是否为6位数
                        set_stocks_info[row].append(temp)
                    else:
                        set_stocks_info[row].append('')
                elif col == 3:
                    if temp in ('>', '<'):
                        set_stocks_info[row].append(temp)
                    else:
                        set_stocks_info[row].append('')
                elif col == 4:
                    try:
                        price = float(temp)
                        if price > 0:
                            set_stocks_info[row].append(price)  # 把价格转为数字
                        else:
                            set_stocks_info[row].append(0)
                    except ValueError:
                        set_stocks_info[row].append(0)
                elif col == 5:
                    if temp in ('B', 'S'):
                        set_stocks_info[row].append(temp)
                    else:
                        set_stocks_info[row].append('')
                elif col == 6:
                    if temp.isdigit() and int(temp) >= 0:
                        set_stocks_info[row].append(str(int(temp) // 100 * 100))
                    else:
                        set_stocks_info[row].append('')
                elif col == 7:
                    try:
                        set_stocks_info[row].append(datetime.datetime.strptime(temp, '%H:%M:%S').time())
                    except ValueError:
                        set_stocks_info[row].append(datetime.datetime.strptime('1:00:00', '%H:%M:%S').time())

if __name__ == '__main__':

    opt = OperationThs()
    print(str(opt.getMoney()))

    # StockGui()
    # t1 = threading.Thread(target=StockGui)
    # t1.start()
    # t2 = threading.Thread(target=monitor)
    # t2.start()