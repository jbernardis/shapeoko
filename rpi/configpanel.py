import wx
from wx.lib import newevent

class ConfigPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.parentFrame = win
		self.images = images

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())
