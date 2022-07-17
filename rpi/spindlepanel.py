
import wx
from common import XAXIS, YAXIS, ZAXIS

class SpindlePanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.spindleStat = False
		self.speed = 0

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		self.bOn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngHome,    size=(54, 54), pos=(50, 50))
		self.bOn.Bind(wx.EVT_BUTTON,  self.onOnButton)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onOnButton(self, _):
		if self.spindleStat:
			self.shapeoko.spindleOff()
			self.spindleStat = False
		else:
			self.shapeoko.spindleOn()
			self.spindleStat = True


