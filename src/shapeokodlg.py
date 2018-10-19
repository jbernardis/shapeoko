import wx

from propertiesgrid import PropertiesGrid

class ShapeokoDlg(wx.Dialog):
	def __init__(self, parent, cnc, images):
		self.parent = parent
		self.cnc = cnc
		self.images = images
		
		wx.Dialog.__init__(self, None, wx.ID_ANY, "Shapeoko Properties")
		sz = wx.BoxSizer(wx.VERTICAL)
				
		self.pGrid = PropertiesGrid(self, self.images, size=(400, 250))
		sz.Add(self.pGrid, 1, wx.EXPAND)
		sz.AddSpacer(20)
		
		self.pGrid.setProperties(self.cnc)
		
		b = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.onBOK, b)
		sz.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(sz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		
	def setModified(self, flag=True):
		self.parent.setModified(flag)

	def onBOK(self, evt):
		self.EndModal(wx.ID_OK)