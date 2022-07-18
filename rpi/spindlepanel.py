
import wx
from common import XAXIS, YAXIS, ZAXIS

class SpindlePanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.spindleOn = False
		self.spindleSpeed = 0
		self.maxSpindleSpeed = 6000

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		self.bOnOff = wx.BitmapButton(self, wx.ID_ANY, images.pngOff, pos=(75, 30), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBOnOff, self.bOnOff)

		self.slSpindleSpeed = wx.Slider(self, wx.ID_ANY,
			self.spindleSpeed, 0, self.maxSpindleSpeed, size=(150, 300), pos=(30, 90),
			style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS | wx.SL_INVERSE)
		self.slSpindleSpeed.SetFont(font)

		self.Bind(wx.EVT_SLIDER, self.onSlSpindleSpeed, self.slSpindleSpeed)

		ybase = 30
		self.bUp100 = wx.BitmapButton(self, wx.ID_ANY, images.pngUp3, pos=(210, ybase), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBUp100, self.bUp100)

		self.bUp10 = wx.BitmapButton(self, wx.ID_ANY, images.pngUp2, pos=(210, ybase+60), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBUp10, self.bUp10)

		self.bUp1 = wx.BitmapButton(self, wx.ID_ANY, images.pngUp1, pos=(210, ybase+60*2), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBUp1, self.bUp1)

		self.bDown1 = wx.BitmapButton(self, wx.ID_ANY, images.pngDown1, pos=(210, ybase+60*3), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBDown1, self.bDown1)

		self.bDown10 = wx.BitmapButton(self, wx.ID_ANY, images.pngDown2, pos=(210, ybase+60*4), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBDown10, self.bDown10)

		self.bDown100 = wx.BitmapButton(self, wx.ID_ANY, images.pngDown3, pos=(210, ybase+60*5), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBDown100, self.bDown100)

		text = "Spindle is OFF"
		w,h = dc.GetTextExtent(text)
		self.stSpindleState = wx.StaticText(self, wx.ID_ANY, text, pos=(80, 410), size=(w, h+10))
		self.stSpindleState.SetFont(font)


	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onBOnOff(self, _):
		if self.spindleOn:
			self.shapeoko.spindleOff()
			self.bOnOff.SetBitmap(self.images.pngOn)
			self.stSpindleState.SetLabel("Spindle is OFF")
			self.spindleOn = False
		else:
			self.shapeoko.setSpindleSpeed(self.spindleSpeed)
			self.shapeoko.spindleOn()
			self.bOnOff.SetBitmap(self.images.pngOff)
			self.stSpindleState.SetLabel("Spindle is ON")
			self.spindleOn = True

	def onBUp1(self, _):
		self.adjustSpindleSpeed(1)

	def onBUp10(self, _):
		self.adjustSpindleSpeed(10)

	def onBUp100(self, _):
		self.adjustSpindleSpeed(100)

	def onBDown1(self, _):
		self.adjustSpindleSpeed(-1)

	def onBDown10(self, _):
		self.adjustSpindleSpeed(-10)

	def onBDown100(self, _):
		self.adjustSpindleSpeed(-100)

	def adjustSpindleSpeed(self, inc):
		if self.spindleSpeed + inc > self.maxSpindleSpeed:
			self.spindleSpeed = self.maxSpindleSpeed
		elif self.spindleSpeed + inc < 0:
			self.spindleSpeed = 0
		else:
			self.spindleSpeed += inc

		self.slSpindleSpeed.SetValue(self.spindleSpeed)
		if self.spindleOn:
			self.shapeoko.setSpindleSpeed(self.spindleSpeed)

	def onSlSpindleSpeed(self, evt):
		self.spindleSpeed = self.slSpindleSpeed.GetValue()
		if self.spindleOn:
			self.shapeoko.setSpindleSpeed(self.spindleSpeed)

