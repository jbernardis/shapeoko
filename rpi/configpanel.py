import wx
from wx.lib import newevent

(ConfigEvent, EVT_CONFIG) = newevent.NewEvent()  

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

		self.shapeoko.registerConfigHandler(self.configHandler)
		self.Bind(EVT_CONFIG, self.showConfig)

	def configHandler(self, msg):  # thread context
		evt = ConfigEvent(msg=msg)
		wx.PostEvent(self, evt)

	def showConfig(self, evt):
		msg = evt.msg
		print("Config data rcvd: (%s)" % msg)

		cx, val = msg[1:].split("=", 1)

		try:
			icx = int(cx)
		except:
			icx = None
		if icx is not None:
			print("cfg index: %d  value: (%s)" % (int(cx), val))

	def switchToPage(self):
		try:
			self.shapeoko.getConfig()
		except:
			pass

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())
