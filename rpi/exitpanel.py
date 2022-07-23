import wx

class ExitPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images
		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		fontText = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.dc = wx.ScreenDC()
		self.dc.SetFont(fontText)

		
		self.bExit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBexit, size=(120, 120), pos=(50, 280))
		self.Bind(wx.EVT_BUTTON, self.onBExit, self.bExit)

		self.bShutdown = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBshutdown, size=(120, 120), pos=(250, 280))
		self.Bind(wx.EVT_BUTTON, self.onBShutdown, self.bShutdown)

		self.bReboot = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBreboot, size=(120, 120), pos=(450, 280))
		self.Bind(wx.EVT_BUTTON, self.onBReboot, self.bReboot)

		self.enableButtons()

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def onBExit(self, _):
		self.parentFrame.requestClose()

	def onBShutdown(self, _):
		self.parentFrame.requestClose(shutdown=True)

	def onBReboot(self, _):
		self.parentFrame.requestClose(reboot=True)


