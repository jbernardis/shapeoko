import wx

class StatPanel(wx.Panel):
	def __init__(self, parent, win):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
