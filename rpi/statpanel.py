import wx
from wx.lib import newevent

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  

class StatPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images
		self.parserState = ""

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		fontText = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.dc = wx.ScreenDC()
		self.dc.SetFont(fontText)

		self.stMachineState = wx.StaticText(self, wx.ID_ANY, "Idle", pos=(300, 20))
		self.stMachineState.SetFont(fontText)

		self.stParserState = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 80))
		self.stParserState.SetFont(fontText)

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBrefresh, size=(120, 120), pos=(50, 20))
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)



	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		#self.shapeoko.registerNewStatus(self.statusUpdate)
		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		self.status = evt.status
		w,h = self.dc.GetTextExtent(self.status)
		self.stMachineState.SetSize((w, h))
		self.stMachineState.SetLabel(self.status)

	def onBRefresh(self, evt):
		self.shapeoko.getParserState()

	def refreshParserState(self, state):
		self.parserState = state
		w,h = self.dc.GetTextExtent(state)
		self.stParserState.SetSize((w, h))
		self.stParserState.SetLabel(state)

