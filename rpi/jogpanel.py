
import wx
from common import devMode

class JogPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		basex = 50
		basey = 20

		bdim = 50

		colx = basex + 4*bdim
		rowy = basey + 4*bdim

		self.bY4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupgreen,    size=(36, 36), pos=(colx,  basey))
		self.bY3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupblue,     size=(36, 36), pos=(colx,  basey+bdim))
		self.bY2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupred,      size=(36, 36), pos=(colx,  basey+bdim*2))
		self.bY1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogupyellow,   size=(36, 36), pos=(colx,  basey+bdim*3))
		self.bY4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y4"))
		self.bY3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y3"))
		self.bY2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y2"))
		self.bY1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y1"))

		self.bYm1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnyellow,   size=(36, 36), pos=(colx, basey+bdim*5))
		self.bYm2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnred,      size=(36, 36), pos=(colx, basey+bdim*6))
		self.bYm3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdnblue,     size=(36, 36), pos=(colx, basey+bdim*7))
		self.bYm4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogdngreen,    size=(36, 36), pos=(colx, basey+bdim*8))
		self.bYm1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y-1"))
		self.bYm2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y-2"))
		self.bYm3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y-3"))
		self.bYm4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "Y-4"))

		self.bXm4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfgreen,    size=(36, 36), pos=(basex,  rowy))
		self.bXm3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfblue,     size=(36, 36), pos=(basex+bdim,  rowy))
		self.bXm2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfred,      size=(36, 36), pos=(basex+bdim*2,  rowy))
		self.bXm1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJoglfyellow,   size=(36, 36), pos=(basex+bdim*3,  rowy))
		self.bXm4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X-4"))
		self.bXm3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X-3"))
		self.bXm2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X-2"))
		self.bXm1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X-1"))

		self.bX1 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtyellow,   size=(36, 36), pos=(basex+bdim*5, rowy))
		self.bX2 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtred,      size=(36, 36), pos=(basex+bdim*6, rowy))
		self.bX3 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtblue,     size=(36, 36), pos=(basex+bdim*7, rowy))
		self.bX4 = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJogrtgreen,    size=(36, 36), pos=(basex+bdim*8, rowy))
		self.bX1.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X1"))
		self.bX2.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X2"))
		self.bX3.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X3"))
		self.bX4.Bind(wx.EVT_BUTTON,  lambda event: self.onJogButton(event, "X4"))

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onJogButton(self, evt, button):
		print("on button (%s)" % button)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		if devMode:
			if shapeoko is None:
				return
