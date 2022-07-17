
import wx
from common import XAXIS, YAXIS, ZAXIS

class JogPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		basex = 50
		basey = 20

		bdim = 50

		colx = basex + 4*bdim
		rowy = basey + 4*bdim

		self.bHome = wx.BitmapButton(self, wx.ID_ANY, self.images.pngHome,    size=(54, 54), pos=(basex,  basey))
		self.bHome.Bind(wx.EVT_BUTTON,  self.onHomeButton)

		self.bY4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupgreen,    size=(40, 40), pos=(colx,  basey))
		self.bY3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupblue,     size=(40, 40), pos=(colx,  basey+bdim))
		self.bY2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupred,      size=(40, 40), pos=(colx,  basey+bdim*2))
		self.bY1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupyellow,   size=(40, 40), pos=(colx,  basey+bdim*3))
		self.bY4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 4"))
		self.bY3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 3"))
		self.bY2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 2"))
		self.bY1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "JOG Y 1"))

		self.bYm1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnyellow,   size=(40, 40), pos=(colx, basey+bdim*5))
		self.bYm2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnred,      size=(40, 40), pos=(colx, basey+bdim*6))
		self.bYm3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnblue,     size=(40, 40), pos=(colx, basey+bdim*7))
		self.bYm4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdngreen,    size=(40, 40), pos=(colx, basey+bdim*8))
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

		zbasex = int(basex+7*bdim+bdim/2)
		zbasey = int(basey+5.5*bdim)

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

		self.bResetX = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisx, size=(54, 54), pos=(basex+10*bdim, basey+50))
		self.bResetY = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisy, size=(54, 54), pos=(basex+10*bdim, basey+50+70))
		self.bResetZ = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisz, size=(54, 54), pos=(basex+10*bdim, basey+50+70*2))
		self.bResetX.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, XAXIS))
		self.bResetY.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, YAXIS))
		self.bResetZ.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, ZAXIS))


		self.bGoToX =  wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisx,  size=(54, 54), pos=(basex+12*bdim, basey+50))
		self.bGoToY =  wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisy,  size=(54, 54), pos=(basex+12*bdim, basey+50+70))
		self.bGoToZ =  wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisz,  size=(54, 54), pos=(basex+12*bdim, basey+50+70*3))
		self.bGoToXY = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisxy, size=(66, 54), pos=(basex+12*bdim-6, basey+50+70*2))
		self.bGoToX.Bind(wx.EVT_BUTTON,  lambda event: self.onGoToButton(event, XAXIS))
		self.bGoToY.Bind(wx.EVT_BUTTON,  lambda event: self.onGoToButton(event, YAXIS))
		self.bGoToZ.Bind(wx.EVT_BUTTON,  lambda event: self.onGoToButton(event, ZAXIS))
		self.bGoToXY.Bind(wx.EVT_BUTTON,  self.onGoToXYButton)

		txt = "RESET    GO TO"
		w,h = dc.GetTextExtent(txt)
		hdr = wx.StaticText(self, wx.ID_ANY, txt, pos=(basex+10*bdim, basey), size=(w, h))
		hdr.SetFont(font)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		self.shapeoko.registerStatusHandler(self.statusUpdate)

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onHomeButton(self, evt):
		if self.status.lower() == "alarm":
			self.shapeoko.clearAlarm()
		self.shapeoko.gotoHome()

	def onJogButton(self, evt, command):
		self.shapeoko.jog(command)

	def onResetButton(self, evt, axis):
		if axis == XAXIS:
			self.shapeoko.resetAxis(x=0)
		elif axis == YAXIS:
			self.shapeoko.resetAxis(y=0)
		elif axis == ZAXIS:
			self.shapeoko.resetAxis(z=0)

	def onGoToButton(self, evt, axis):
		if axis == XAXIS:
			self.shapeoko.goto(x=0)
		elif axis == YAXIS:
			self.shapeoko.goto(y=0)
		elif axis == ZAXIS:
			self.shapeoko.goto(z=0)

	def onGoToXYButton(self, evt):
		self.shapeoko.goto(x=0, y=0)

	def statusUpdate(self, ns):  #thread context
		self.status = ns
