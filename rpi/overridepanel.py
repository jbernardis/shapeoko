import wx
from wx.lib import newevent

from common import XAXIS, YAXIS, ZAXIS

(RateEvent, EVT_RATE) = newevent.NewEvent()

class OverridePanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.spindleOn = False
		self.spindleSpeed = 0
		self.maxSpindleSpeed = 6000
		self.reportedSpindleSpeed = 0

		self.feedrate = 100
		self.rapidrate = 100
		self.spindlerate = 100

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)
		ratew,rateh = dc.GetTextExtent("100%")

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
		self.stSpindleState.SetSize((w, h+10))

		header = "---------Overrides---------"
		w,h = dc.GetTextExtent(header)
		self.stHeader = wx.StaticText(self, wx.ID_ANY, header, pos=(360, 10), size=(w, h))
		self.stHeader.SetFont(font)

		# adjustFeedRate(-10, -1, 0, 1, 10)
		xcol = 360
		ybase = 40
		yrates = ybase+60*5
		self.bFeedUp10 = wx.Button(self, wx.ID_ANY, "+10%", pos=(xcol, ybase), size=(54, 54))
		self.bFeedUp10.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, 10))

		self.bFeedUp1 = wx.Button(self, wx.ID_ANY, "+1%", pos=(xcol, ybase+60), size=(54, 54))
		self.bFeedUp1.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, 1))

		self.bFeed100 = wx.Button(self, wx.ID_ANY, "100%", pos=(xcol, ybase+60*2), size=(54, 54))
		self.bFeed100.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, 0))

		self.bFeedDown1 = wx.Button(self, wx.ID_ANY, "-1%", pos=(xcol, ybase+60*3), size=(54, 54))
		self.bFeedDown1.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, -1))

		self.bFeedDown10 = wx.Button(self, wx.ID_ANY, "-10%", pos=(xcol, ybase+60*4), size=(54, 54))
		self.bFeedDown10.Bind(wx.EVT_BUTTON,  lambda event: self.onFeedButton(event, -10))

		self.stFeedRate = wx.StaticText(self, wx.ID_ANY, "100%", pos=(xcol, yrates))
		self.stFeedRate.SetFont(font)
		self.stFeedRate.SetSize((ratew, rateh))

		# adjustRapidRate(100, 50, 25)
		xcol = 460
		ybase = 100
		self.bRapid100 = wx.Button(self, wx.ID_ANY, "100%", pos=(xcol, ybase), size=(54, 54))
		self.bRapid100.Bind(wx.EVT_BUTTON,  lambda event: self.onRapidButton(event, 100))

		self.bRapid50 = wx.Button(self, wx.ID_ANY, "50%", pos=(xcol, ybase+60), size=(54, 54))
		self.bRapid50.Bind(wx.EVT_BUTTON,  lambda event: self.onRapidButton(event, 50))

		self.bRapid25 = wx.Button(self, wx.ID_ANY, "25%", pos=(xcol, ybase+60*2), size=(54, 54))
		self.bRapid25.Bind(wx.EVT_BUTTON,  lambda event: self.onRapidButton(event, 25))

		self.stRapidRate = wx.StaticText(self, wx.ID_ANY, "100%", pos=(xcol, yrates))
		self.stRapidRate.SetFont(font)
		self.stRapidRate.SetSize((ratew, rateh))

		# adjustSpindleSpeed(-10, -1, 0, 1, 10)
		xcol = 560
		ybase = 40
		self.bSpindleUp10 = wx.Button(self, wx.ID_ANY, "+10%", pos=(xcol, ybase), size=(54, 54))
		self.bSpindleUp10.Bind(wx.EVT_BUTTON,  lambda event: self.onSpindleButton(event, 10))

		self.bSpindleUp1 = wx.Button(self, wx.ID_ANY, "+1%", pos=(xcol, ybase+60), size=(54, 54))
		self.bSpindleUp1.Bind(wx.EVT_BUTTON,  lambda event: self.onSpindleButton(event, 1))

		self.bSpindle100 = wx.Button(self, wx.ID_ANY, "100%", pos=(xcol, ybase+60*2), size=(54, 54))
		self.bSpindle100.Bind(wx.EVT_BUTTON,  lambda event: self.onSpindleButton(event, 0))

		self.bSpindleDown1 = wx.Button(self, wx.ID_ANY, "-1%", pos=(xcol, ybase+60*3), size=(54, 54))
		self.bSpindleDown1.Bind(wx.EVT_BUTTON,  lambda event: self.onSpindleButton(event, -1))

		self.bSpindleDown10 = wx.Button(self, wx.ID_ANY, "-10%", pos=(xcol, ybase+60*4), size=(54, 54))
		self.bSpindleDown10.Bind(wx.EVT_BUTTON,  lambda event: self.onSpindleButton(event, -10))

		self.stSpindleRate = wx.StaticText(self, wx.ID_ANY, "100%", pos=(xcol, yrates))
		self.stSpindleRate.SetFont(font)
		self.stSpindleRate.SetSize((ratew, rateh))

		colLabel = "Feed      Rapid    Spindle"
		w,h = dc.GetTextExtent(colLabel)
		self.stColLabel = wx.StaticText(self, wx.ID_ANY, colLabel, pos=(360, yrates+30), size=(w, h))
		self.stColLabel.SetFont(font)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		self.shapeoko.registerSpeedHandler(self.updateSpeeds)
		self.shapeoko.registerOverrideHandler(self.updateOverrides)
		self.Bind(EVT_RATE, self.rateEvent)

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

	def onBSpindleSpeedUp100(self, _):
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

	def onFeedButton(self, _, inc):
		self.shapeoko.adjustFeedRate(inc)

	def onRapidButton(self, _, inc):
		self.shapeoko.adjustRapidRate(inc)

	def onSpindleButton(self, _, inc):
		self.shapeoko.adjustSpindleSpeed(inc)

	def updateOverrides(self, feed, rapid, spindle): # thread context
		print("Overrides: Feed(%s)  Rapid(%s)  Spindle(%s)" % (feed, rapid, spindle))
		evt = RateEvent(feed=feed, rapid=rapid, spindle=spindle)
		wx.PostEvent(self, evt)

	def rateEvent(self, evt):
		print("got the rate event")
		if evt.feed is not None:
			self.feedrate = evt.feed
			self.stFeedRate.SetLabel("%d%%" % self.feedrate)
		if evt.rapid is not None:
			self.rapidrate = evt.rapid
			self.stRapidRate.SetLabel("%d%%" % self.rapidrate)
		if evt.spindle is not None:
			self.spindlerate = evt.spindle
			self.stSpindleRate.SetLabel("%d%%" % self.spindlerate)
