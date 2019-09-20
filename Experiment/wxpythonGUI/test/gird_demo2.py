import wx
import wx.grid

from PIL import Image
from io import BytesIO
from pylab import *

from SDK.Gen_Stk_Pic_Sub import set_background_color
from SDK.MyTimeOPT import get_current_datetime_str

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


class MyApp(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, -1, title="wx.Grid - Bitmap example")
        self.grid = wx.grid.Grid(self.frame)

        nrow, ncol = 1, 3
        self.grid.CreateGrid(nrow, ncol)

        self.timer = wx.Timer(self)  							# 创建定时器
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)  	# 绑定一个定时器事件
        self.timer.Start(1000)  								# 设定时间间隔

        self.frame.Show(True)

        return True

    # 定义定时器
    def on_timer(self, event):
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 4))

        plt.title('图' + get_current_datetime_str())
        output = BytesIO()  # BytesIO实现了在内存中读写byte

        fig.canvas.print_png(output)
        # fig.savefig(output, dpi=100)
        output.seek(0)
        img = wx.Image(output, wx.BITMAP_TYPE_ANY)

        output.close()
        # plt.close()

        imageRenderer = MyImageRenderer(wx.Bitmap(img))
        self.grid.SetCellRenderer(0, 1, imageRenderer)
        self.grid.SetColSize(1, img.GetWidth() + 2)
        self.grid.SetRowSize(0, img.GetHeight() + 2)

        self.frame.Refresh()


class MyImageRenderer(wx.grid.GridCellRenderer):
    def __init__(self, img):
        wx.grid.GridCellRenderer.__init__(self)
        self.img = img

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        image = wx.MemoryDC()
        image.SelectObject(self.img)
        # dc.SetBackgroundMode(wx.SOLID)
        if isSelected:
            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangle(rect)
        width, height = self.img.GetWidth(), self.img.GetHeight()
        if width > rect.width - 2:
            width = rect.width - 2
        if height > rect.height - 2:
            height = rect.height - 2
        dc.Blit(rect.x + 1, rect.y + 1, width, height, image, 0, 0, wx.COPY, True)


app = MyApp(0)
app.MainLoop()
