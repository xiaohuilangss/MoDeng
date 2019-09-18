# encoding=utf-8

import wx
import sys
import glob

from PIL import Image
from io import BytesIO
from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False


MAIN_PANEL = wx.NewId()


class CommunicationApp(wx.App):
    """This is the class for the communication tool application.
    """

    def __init__(self, config=None, redirect=False):
        """ Instantiates an application."""

        wx.App.__init__(self, redirect=redirect)
        self.cfg = config
        self.mainframe = CommunicationFrame(config=config, redirect=redirect)
        self.mainframe.Show()

        def OnInit(self):
            # self.SetTopWindow(self.mainframe)
            return True


class CommunicationFrame(wx.Frame):
    """Frame of the Communication Application.
    """

    def __init__(self, config, redirect=False):
        """Initialize the frame.
        """

        wx.Frame.__init__(self, parent=None,
                          title="CMC Communication Tool",
                          style=wx.DEFAULT_FRAME_STYLE)
        # self.imgs = glob.glob('./img/img*.png')
        self.panel = CommuniationPanel(parent=self,
                                       pid=MAIN_PANEL, config=config)

        # Gridbagsizer.
        nrows, ncols = 3, 3
        # self.Scrollbar = wx.ScrollBar(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SB_VERTICAL)
        self.grid = wx.GridSizer(rows=nrows, cols=ncols, vgap=0, hgap=0)

        # self.grid.Add(self.Scrollbar, 0, wx.EXPAND)

        # Add images to the grid.
        for r in range(nrows):
            for c in range(ncols):
                _n = ncols * r + c

                fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 4))
                plt.title('图' + str(_n))
                output = BytesIO()  # BytesIO实现了在内存中读写byte
                buf_save = BytesIO()
                fig.savefig(output, dpi=100)
                output.seek(0)
                _tmp = wx.Image(output, wx.BITMAP_TYPE_ANY)
                # pic_id = wx.Bitmap(img)
                buf_save.close()
                output.close()

                # _tmp = wx.Image(self.imgs[_n], wx.BITMAP_TYPE_ANY)
                _temp = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                wx.BitmapFromImage(_tmp))
                self.grid.Add(_temp, 0, wx.EXPAND)
                # self.grid.Fit(self)

                self.panel.SetSizer(self.grid)


class CommuniationPanel(wx.Panel):
    """Panel of the Communication application frame.
    """

    def __init__(self, parent, pid, config):
        """ Initialize the panel. """

        wx.Panel.__init__(self, parent=parent, id=pid)

        # CALLBACK BINDINGS
        # Bind keyboard events.

        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

    def on_key_up(self, evt):
        """Handles Key UP events.
        """
        code = evt.GetKeyCode()
        print(code, wx.WXK_ESCAPE)

        if code == wx.WXK_ESCAPE:
            sys.exit(0)


def main():
    app = CommunicationApp()
    app.MainLoop()


if __name__ == '__main__':
    main()