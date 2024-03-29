
import wx
from wx.lib import newevent

from common import XAXIS, YAXIS, ZAXIS
(ProbeEvent, EVT_PROBE) = newevent.NewEvent()  


class JogPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images
		self.status = ""
		self.frame = win

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		basex = 50
		basey = 10

		bdim = 45

		colx = basex + 4*bdim
		rowy = basey + 4*bdim

		self.bHome = wx.BitmapButton(self, wx.ID_ANY, self.images.pngHome,    size=(54, 54), pos=(basex,  basey))
		self.bHome.Bind(wx.EVT_BUTTON,  self.onHomeButton)

		self.bProbe = wx.BitmapButton(self, wx.ID_ANY, self.images.pngProbe,    size=(54, 54), pos=(basex+bdim+20,  basey))
		self.bProbe.Bind(wx.EVT_BUTTON,  self.onProbeButton)

		yoff = 15
		self.bY4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupgreen,    size=(40, 40), pos=(colx,  basey+yoff))
		self.bY3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupblue,     size=(40, 40), pos=(colx,  basey+yoff+bdim))
		self.bY2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupred,      size=(40, 40), pos=(colx,  basey+yoff+bdim*2))
		self.bY1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupyellow,   size=(40, 40), pos=(colx,  basey+yoff+bdim*3))
		self.bY4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 4"))
		self.bY3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 3"))
		self.bY2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 2"))
		self.bY1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 1"))

		yoff = -15
		self.bYm1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnyellow,   size=(40, 40), pos=(colx, basey+yoff+bdim*5))
		self.bYm2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnred,      size=(40, 40), pos=(colx, basey+yoff+bdim*6))
		self.bYm3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnblue,     size=(40, 40), pos=(colx, basey+yoff+bdim*7))
		self.bYm4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdngreen,    size=(40, 40), pos=(colx, basey+yoff+bdim*8))
		self.bYm1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y -1"))
		self.bYm2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y -2"))
		self.bYm3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y -3"))
		self.bYm4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y -4"))

		self.bXm4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfgreen,    size=(40, 40), pos=(basex,  rowy))
		self.bXm3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfblue,     size=(40, 40), pos=(basex+bdim,  rowy))
		self.bXm2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfred,      size=(40, 40), pos=(basex+bdim*2,  rowy))
		self.bXm1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfyellow,   size=(40, 40), pos=(basex+bdim*3,  rowy))
		self.bXm4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X -4"))
		self.bXm3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X -3"))
		self.bXm2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X -2"))
		self.bXm1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X -1"))

		self.bX1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtyellow,   size=(40, 40), pos=(basex+bdim*5, rowy))
		self.bX2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtred,      size=(40, 40), pos=(basex+bdim*6, rowy))
		self.bX3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtblue,     size=(40, 40), pos=(basex+bdim*7, rowy))
		self.bX4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtgreen,    size=(40, 40), pos=(basex+bdim*8, rowy))
		self.bX1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X 1"))
		self.bX2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X 2"))
		self.bX3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X 3"))
		self.bX4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG X 4"))

		self.bXY1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfupgreen, size=(40, 40), pos=(basex+bdim*2, basey+bdim*2))
		self.bXY1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG XY -4 4"))
		self.bXY2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtupgreen, size=(40, 40), pos=(basex+bdim*6, basey+bdim*2))
		self.bXY2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG XY 4 4"))
		self.bXY3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfdngreen, size=(40, 40), pos=(basex+bdim*2, basey+bdim*6))
		self.bXY3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG XY -4 -4"))
		self.bXY4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtdngreen, size=(40, 40), pos=(basex+bdim*6, basey+bdim*6))
		self.bXY4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG XY 4 -4"))

		zbasex = int(basex+9*bdim+bdim/2)
		zbasey = int(basey+5*bdim)

		self.bZm1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnyellow, size=(40, 40), pos=(zbasex, zbasey+bdim/2))
		self.bZm2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnred,    size=(40, 40), pos=(zbasex, zbasey+bdim+bdim/2))
		self.bZm3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnblue,   size=(40, 40), pos=(zbasex, zbasey+bdim*2+bdim/2))
		self.bZm1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Z -1"))
		self.bZm2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Z -2"))
		self.bZm3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Z -3"))

		self.bZ3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupblue,   size=(40, 40), pos=(zbasex+bdim, zbasey))
		self.bZ2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupred,    size=(40, 40), pos=(zbasex+bdim, zbasey+bdim))
		self.bZ1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupyellow, size=(40, 40), pos=(zbasex+bdim, zbasey+bdim*2))
		self.bZ3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Z 3"))
		self.bZ2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Z 2"))
		self.bZ1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Z 1"))

		self.bStopJog = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogstop, size=(54, 54), pos=(basex+7*bdim, basey))
		self.bStopJog.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG STOP"))

		self.bResetX = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisx, size=(54, 54), pos=(basex+12*bdim, basey+50))
		self.bResetY = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisy, size=(54, 54), pos=(basex+12*bdim, basey+50+70))
		self.bResetZ = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisz, size=(54, 54), pos=(basex+12*bdim, basey+50+70*2))
		self.bResetX.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, XAXIS))
		self.bResetY.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, YAXIS))
		self.bResetZ.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, ZAXIS))


		self.bGoToX =  wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisx,  size=(54, 54), pos=(basex+14*bdim, basey+50))
		self.bGoToY =  wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisy,  size=(54, 54), pos=(basex+14*bdim, basey+50+70))
		self.bGoToZ =  wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisz,  size=(54, 54), pos=(basex+14*bdim, basey+50+70*3))
		self.bGoToXY = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisxy, size=(66, 54), pos=(basex+14*bdim-6, basey+50+70*2))
		self.bGoToX.Bind(wx.EVT_BUTTON,  lambda event: self.onGoToButton(event, XAXIS))
		self.bGoToY.Bind(wx.EVT_BUTTON,  lambda event: self.onGoToButton(event, YAXIS))
		self.bGoToZ.Bind(wx.EVT_BUTTON,  lambda event: self.onGoToButton(event, ZAXIS))
		self.bGoToXY.Bind(wx.EVT_BUTTON,  self.onGoToXYButton)

		txt = "RESET    GO TO"
		w,h = dc.GetTextExtent(txt)
		hdr = wx.StaticText(self, wx.ID_ANY, txt, pos=(basex+12*bdim, basey), size=(w, h))
		hdr.SetFont(font)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		self.shapeoko.registerStatusHandler(self.statusUpdate)
		self.shapeoko.registerProbeHandler(self.probeReport)
		self.Bind(EVT_PROBE, self.probeEvent)

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onHomeButton(self, evt):
		if self.status == "alarm":
			self.shapeoko.clearAlarm()
		elif self.status == "idle":
			self.shapeoko.gotoHome()
		else:
			self.frame.log("\"Home\" command illegal while in '%s' state" % self.status)

	def onProbeButton(self, evt):
		if self.status == "idle":
			self.shapeoko.probe()
		else:
			self.frame.log("\"Probe\" command illegal while in '%s' state" % self.status)

	def onJogButton(self, evt, command):
		if self.status in ["idle", "jog"]:
			self.shapeoko.jog(command)
		else:
			self.frame.log("\"Jog\" command illegal while in '%s' state" % self.status)

	def onResetButton(self, evt, axis):
		if self.status == "idle":
			if axis == XAXIS:
				self.shapeoko.resetAxis(x=0)
			elif axis == YAXIS:
				self.shapeoko.resetAxis(y=0)
			elif axis == ZAXIS:
				self.shapeoko.resetAxis(z=0)
		else:
			self.frame.log("\"Reset Axis\" command illegal while in '%s' state" % self.status)

	def onGoToButton(self, evt, axis):
		if self.status == "idle":
			if axis == XAXIS:
				self.shapeoko.goto(x=0)
			elif axis == YAXIS:
				self.shapeoko.goto(y=0)
			elif axis == ZAXIS:
				self.shapeoko.goto(z=0)
		else:
			self.frame.log("\"Go To\" command illegal while in '%s' state" % self.status)

	def onGoToXYButton(self, evt):
		if self.status == "idle":
			self.shapeoko.goto(x=0, y=0)
		else:
			self.frame.log("\"Go To\" command illegal while in '%s' state" % self.status)

	def statusUpdate(self, ns):  #thread context
		self.status = ns.lower()

	def probeReport(self, msg): # thread context
		evt = ProbeEvent(msg=msg)
		wx.PostEvent(self, evt)

	def probeEvent(self, evt):
		self.shapeoko.resetAxis(z=self.settings.probeheight)

