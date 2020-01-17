# encoding=utf-8
import wx


class ConfigDialog(wx.Frame):
	def __init__(self, parent, title):
		super(ConfigDialog, self).__init__(parent, title=title, size=(700, 500))

		# 绑定关闭函数
		self.Bind(wx.EVT_CLOSE, self.on_close, parent)

		panel = wx.Panel(self)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.my_grid4 = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
		
		# Grid
		self.my_grid4.CreateGrid(len(stk_info), 6)
		self.my_grid4.EnableEditing(False)
		self.my_grid4.EnableGridLines(True)
		self.my_grid4.EnableDragGridSize(False)
		self.my_grid4.SetMargins(0, 0)
		
		# Columns
		self.my_grid4.EnableDragColMove(False)
		self.my_grid4.EnableDragColSize(True)
		self.my_grid4.SetColLabelSize(30)
		self.my_grid4.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		
		self.my_grid4.SetColLabelValue(0, "参数名称")
		self.my_grid4.SetColLabelValue(1, "参数A")
		self.my_grid4.SetColLabelValue(2, "参数B")
		self.my_grid4.SetColLabelValue(3, "参数释义")

		# Rows
		self.my_grid4.EnableDragRowSize(True)
		self.my_grid4.SetRowLabelSize(80)
		self.my_grid4.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		# self.my_grid4.SetRowLabelValue()
		
		# Add name to Rows
		self.add_row_name([(x[0], x[1]) for x in stk_info])
		
		self.my_grid4.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
		self.my_grid4.DisableCellEditControl()
		
		# 设置行间隔
		# self.my_grid4.SetMargins(0, 2)
		
		hbox3.Add(self.my_grid4, 0, wx.ALL, 5)

		self.Centre()
		self.Show()
		self.Fit()

	def on_close(self, event):
		print('进入关闭响应函数！')
		global dengshen_on
		dengshen_on = False

		event.Skip()

	def on_key_typed(self, event):
		print(event.GetString())

	def OnMaxLen(self, event):
		print("Maximum length reached")