import wx
from pylab import *

bookdata = {
    1 : ("钢铁是怎样炼成的练成的", "2017-05-31"),
    2 : ("秦腔", "2017-04-12"), 
    3 : ("西游记", "1987-08-12")
}




class LibrarySys(wx.Frame):
    def __init__(self, parent, title):
        '''初始化系统总体布局，包括各种控件'''

        #生成一个宽为400，高为600的frame框
        wx.Frame.__init__(self, parent, title=title, size=(400, 400))  

        #生成一个列表
        self.list = wx.ListCtrl(self, -1, style = wx.LC_REPORT)
        self.list.InsertColumn(0, "ID")
        self.list.InsertColumn(1, "书名")
        self.list.InsertColumn(2, "添加日期")

        items = bookdata.items()                                                #将字典数据转化为序列
        for key, data in items:

            #插入一个item，参数1为在什么地方插入，参数二为这个item的文本内容，刚开始item默认仅有一列
            index = self.list.InsertItem(self.list.GetItemCount(), str(key))
            self.list.SetItem(index, 1, pic_id)                                #添加一列，并设置文本为data[0]
            self.list.SetItem(index, 2, data[1])                                #再添加一列，设置文本为data[1]

        self.list.SetColumnWidth(0, 60)                                         #设置每一列的宽度
        self.list.SetColumnWidth(1,230)
        self.list.SetColumnWidth(2, 90)

        self.Show()


# 类似于c中的main函数，但被其他模块导入时，__name__值不是"__main__"
if __name__ == "__main__":
    app = wx.App()

    from PIL import Image
    from io import BytesIO

    fig, ax = plt.subplots(ncols=1, nrows=4)
    output = BytesIO()  # BytesIO实现了在内存中读写byte
    buf_save = BytesIO()
    fig.savefig(output, dpi=800)
    output.seek(0)
    img = wx.Image(output, wx.BITMAP_TYPE_PNG)
    pic_id = wx.Bitmap(img)
    buf_save.close()
    output.close()










    frame = LibrarySys(None, "library-system")
    app.MainLoop()




    end = 0
