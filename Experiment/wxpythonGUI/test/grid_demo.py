import wx.grid as grid
import os
import wx


class healthStatus(wx.Frame):
    organs = ["heart", "lungs", "brain", "liver"]
    health_icons = []
    (row, progress) = (0, 0)

    def __init__(self, parent, id, title):
        # initialise the frame container
        wx.Frame.__init__(self, parent, id, title)
        # main gui sizer, shall be the sizer for the window
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.health_grid = grid.Grid(self)
        self.health_grid.CreateGrid(len(self.organs), 2)
        self.health_grid.SetColLabelValue(0, "Organ")
        self.health_grid.SetColLabelValue(1, "Status")
        self.health_grid.SetRowLabelSize(0)

        try:
            # self.health_icons.append(self.getFilePath("images" + os.sep + "img3.png"))
            # self.health_icons.append(self.getFilePath("images" + os.sep + "img2.png"))
            # self.health_icons.append(self.getFilePath("images" + os.sep + "img1.png"))

            self.health_icons.append("./img3.png")
            self.health_icons.append("./img2.png")
            self.health_icons.append("./img1.png")

        except Exception as e:
            wx.MessageBox("Cannot load icons. \n Please ensure the images directory has not been moved\n\n"
                          + e.message, "Cannot Load Icons", wx.ICON_ERROR)

        index = 0
        for organ in self.organs:
            self.addItem(index, organ)
            index += 1
        self.main_sizer.Add(self.health_grid, 0, wx.ALL, 5)

        self.testing_button = wx.Button(self, wx.ID_ANY, "Testing")
        self.testing_button.Bind(wx.EVT_BUTTON, self.onProgress)
        self.main_sizer.Add(self.testing_button, 0, wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.Fit()

    def addItem(self, index, organ):
        self.health_grid.SetCellValue(index, 0, organ)
        self.health_grid.SetCellRenderer(index, 1, BitmapRenderer(self.health_icons[0]))

    def updateProgress(self, index, progress):
        self.health_grid.SetCellRenderer(index, 0, BitmapRenderer(self.health_icons[progress]))
        self.health_grid.Refresh()

    def getFilePath(self, directory):
        curr = os.getcwd() + os.sep
        parent = "listctrlproblem" + os.sep
        parent_offset = len(parent)

        if curr.index(parent) + parent_offset != len(curr + os.sep):
            curr = curr[:curr.index(parent) + parent_offset]
            print(curr)
        return curr + os.sep + directory

    def onProgress(self, evt):
        if self.health_grid.GetNumberRows() > 1:
            if self.progress + 1 < len(self.health_icons):
                self.progress += 1
            elif self.row < self.health_grid.GetNumberRows() + 1:
                self.progress = 0
                self.row += 1

        self.updateProgress(self.row, self.progress)


class BitmapRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self, image):
        self.image = image
        wx.grid.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, is_selected):
        bmp = wx.Bitmap(self.image)
        dc.DrawBitmap(bmp, rect.X, rect.Y)

    def Clone(self):
        return self.__class__()


app = wx.App(False)
frame = healthStatus(None, -1, "Organ Status")
frame.Show(1)
app.MainLoop()