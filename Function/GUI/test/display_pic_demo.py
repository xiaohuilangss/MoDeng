#!/usr/bin/env python
"""Hello, wxPython! program."""
import wx

from pylab import *

from SDK.Gen_Stk_Pic_Sub import set_background_color

from PIL import Image
from io import BytesIO
from pylab import *


class Frame(wx.Frame):
    """Frame class that displays an image."""

    def __init__(self, image, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title='Hello, wxPython!'):
        """Create a Frame instance and display image."""

        temp = image.ConvertToBitmap()
        size = temp.GetWidth(), temp.GetHeight()
        wx.Frame.__init__(self, parent, id, title, pos, size)
        self.bmp = wx.StaticBitmap(parent=self, bitmap=temp)


class App(wx.App):
    """Application class."""

    def OnInit(self):
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 4))
        set_background_color('b_r')
        plt.title('图')
        output = BytesIO()  # BytesIO实现了在内存中读写byte

        fig.canvas.print_png(output)
        img = wx.Image(output, wx.BITMAP_TYPE_PNG)

        output.close()
        plt.close()

        self.frame = Frame(img)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


def main():
    app = App()
    app.MainLoop()


if __name__ == '__main__':
    main()