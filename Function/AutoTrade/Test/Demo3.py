# encoding=utf-8
import pywinauto
import time


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

    def __close_popup_window(self):
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

    def __close_popup_windows(self):
        """
        关闭多个弹出窗口
        :return:
        """
        while self.__close_popup_window():
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
        self.__close_popup_windows()

    def max_window(self):
        """
        最大化窗口
        """
        if self.__main_window.GetShowState() != 3:

            self.__main_window.Maximize()
        self.__main_window.SetFocus()

    def min_window(self):
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

    def get_money(self):
        """
        获取可用资金
        """
        return float(str(self.__dialog_window.Static19.WindowText()))

    @staticmethod
    def __clean_clipboard_data(data, cols=11):
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

    def __copy_to_clipboard(self):
        """
        拷贝持仓信息至剪贴板
        :return:
        """
        self.__dialog_window.CVirtualGridCtrl.RightClick(coords=(30, 30))

        self.__main_window.TypeKeys('C')

    def __get_cleaned_data(self):
        """
        读取ListView中的信息
        :return: 清洗后的数据
        """
        self.__copy_to_clipboard()

        data = pywinauto.clipboard.GetData()
        return self.__clean_clipboard_data(data)

    def __select_window(self, choice):
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

    def __get_info(self, choice):
        """
        获取股票信息
        """
        self.__select_window(choice=choice)
        return self.__get_cleaned_data()

    def get_position(self):
        """
        获取持仓
        :return:
        """
        return self.__get_info(choice='W')

    @staticmethod
    def get_deal(code, pre_position, cur_position):
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
        info = self.__get_info(choice='R')
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
            self.__close_popup_windows()

    def withdraw_buy(self):
        """
        撤买
        :return:
        """
        self.__select_window(choice='R')
        self.__dialog_window.Button8.Click()
        self.__close_popup_windows()

    def withdraw_sell(self):
        """
        撤卖
        :return:
        """
        self.__select_window(choice='R')
        self.__dialog_window.Button9.Click()
        self.__close_popup_windows()

    def withdraw_all(self):
        """
        全撤
        :return:
        """
        self.__select_window(choice='R')
        self.__dialog_window.Button7.Click()
        self.__close_popup_windows()


if __name__ == '__main__':
    opt = OperationThs()
    r = opt.get_position()

    end = 0