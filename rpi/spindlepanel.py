
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
		self.reportedSpindleSpeed = 0

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		self.bOnOff = wx.BitmapButton(self, wx.ID_ANY, images.pngPower, pos=(35, 30), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBOnOff, self.bOnOff)

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, images.pngRefresh, pos=(115, 30), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBRefresh, self.bRefresh)

		self.slSpindleSpeed = wx.Slider(self, wx.ID_ANY,
			self.spindleSpeed, 0, self.maxSpindleSpeed, size=(150, 300), pos=(30, 90),
			style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS | wx.SL_INVERSE)
		self.slSpindleSpeed.SetFont(font)

		self.Bind(wx.EVT_SLIDER, self.onSlSpindleSpeed, self.slSpindleSpeed)

		ybase = 30
		self.bSpindleSpeedUp100 = wx.BitmapButton(self, wx.ID_ANY, images.pngUp3, pos=(210, ybase), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBSpindleSpeedUp100, self.bSpindleSpeedUp100)

		self.bSpindleSpeedUp10 = wx.BitmapButton(self, wx.ID_ANY, images.pngUp2, pos=(210, ybase+60), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBSpindleSpeedUp10, self.bSpindleSpeedUp10)

		self.bSpindleSpeedUp1 = wx.BitmapButton(self, wx.ID_ANY, images.pngUp1, pos=(210, ybase+60*2), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBSpindleSpeedUp1, self.bSpindleSpeedUp1)

		self.bSpindleSpeedDown1 = wx.BitmapButton(self, wx.ID_ANY, images.pngDown1, pos=(210, ybase+60*3), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBSpindleSpeedDown1, self.bSpindleSpeedDown1)

		self.bSpindleSpeedDown10 = wx.BitmapButton(self, wx.ID_ANY, images.pngDown2, pos=(210, ybase+60*4), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBSpindleSpeedDown10, self.bSpindleSpeedDown10)

		self.bSpindleSpeedDown100 = wx.BitmapButton(self, wx.ID_ANY, images.pngDown3, pos=(210, ybase+60*5), size=(54, 54))
		self.Bind(wx.EVT_BUTTON,  self.onBSpindleSpeedDown100, self.bSpindleSpeedDown100)

		text = "Spindle is OFF"
		w,h = dc.GetTextExtent(text)
		self.stSpindleState = wx.StaticText(self, wx.ID_ANY, text, pos=(80, 410), size=(w, h+10))
		self.stSpindleState.SetFont(font)

		# adjustSpindleSpeed(-10, -1, 0, 1, 10)

		self.bFeedUp10 = wx.Button(self, wx.ID_ANY, "+10%", pos=(410, ybase), size=(54, 54))
		self.bFeedUp10.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, 10))

		self.bFeedUp1 = wx.Button(self, wx.ID_ANY, "+1%", pos=(410, ybase+60), size=(54, 54))
		self.bFeedUp1.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, 1))

		self.bFeed100 = wx.Button(self, wx.ID_ANY, "100%", pos=(410, ybase+60*2), size=(54, 54))
		self.bFeed100.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, 0))

		self.bFeedDown1 = wx.Button(self, wx.ID_ANY, "-1%", pos=(410, ybase+60*3), size=(54, 54))
		self.bFeedDown1.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, -1))

		self.bFeedDown10 = wx.Button(self, wx.ID_ANY, "-10%", pos=(410, ybase+60*4), size=(54, 54))
		self.bFeedDown1.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, -10))

		# adjustRapidRate(100, 50, 25)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		self.shapeoko.registerSpeedHandler(self.updateSpeeds)

	def updateSpeeds(self, feed, spindle):
		if spindle is not None:
			self.reportedSpindleSpeed = spindle

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onBOnOff(self, _):
		if self.spindleOn:
			self.shapeoko.spindleOff()
			self.stSpindleState.SetLabel("Spindle is OFF")
			self.spindleOn = False
		else:
			self.shapeoko.setSpindleSpeed(self.spindleSpeed)
			self.shapeoko.spindleOn()
			self.stSpindleState.SetLabel("Spindle is ON")
			self.spindleOn = True

	def onBSpindleSpeedUp1(self, _):
		self.setSpindleSpeed(1)

	def onBSpindleSpeedUp10(self, _):
		self.setSpindleSpeed(10)

	def onBSpindleSpeedSpindleSpeedUp100(self, _):
		self.setSpindleSpeed(100)

	def onBSpindleSpeedDown1(self, _):
		self.setSpindleSpeed(-1)

	def onBSpindleSpeedDown10(self, _):
		self.setSpindleSpeed(-10)

	def onBSpindleSpeedDown100(self, _):
		self.setSpindleSpeed(-100)

	def setSpindleSpeed(self, inc):
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

	def onBRefresh(self, _):
		self.updateFromShapeoko()

	def updateFromShapeoko(self):
		self.spindleOn = self.reportedSpindleSpeed != 0
		self.spindleSpeed = self.reportedSpindleSpeed
		self.slSpindleSpeed.SetValue(self.spindleSpeed)
		self.stSpindleState.SetLabel("Spindle is ON" if self.spindleOn else "Spindle is OFF")

	def onFeedButton(self, inc):
		self.shapeoko.adjustFeedRate(inc)

