
import wx
from common import XAXIS, YAXIS, ZAXIS

class SpindlePanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.spindleOn = False
		self.spindleSpeed = 0

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		self.cbOnOff = wx.CheckBox(self, wx.ID_ANY, "Turn spindle On", pos=(50, 50))
		self.cbOnOff.Bind(wx.EVT_CHECKBOX,  self.onOnOff)
		self.cbOnOff.SetValue(False)

		self.slSpindleSpeed = wx.Slider(self, wx.ID_ANY,
			self.spindleSpeed, 0, 6000, size=(250, 400), pos=(50, 90),
			style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS)


	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onOnOff(self, _):
		self.spindleOn = self.cbOnOff.GetValue()
		if self.spindleOn:
			self.shapeoko.setSpindleSpeec(self.spindleSpeed)
			self.shapeoko.spindleOn()
			self.cbOnOff.SetLabel("Turn Spindle Off")
		else:
			self.shapeoko.spindleOff()
			self.cbOnOff.SetLabel("Turn Spindle On")



