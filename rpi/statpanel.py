import wx
from wx.lib import newevent
from common import StateColors, devMode

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  
(ParserStateEvent, EVT_NEWPARSERSTATE) = newevent.NewEvent()  

class StatPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images
		self.status = ""
		self.parserState = ""

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		fontText = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.dc = wx.ScreenDC()
		self.dc.SetFont(fontText)

		self.stMachineState = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 20))
		self.stMachineState.SetFont(fontText)

		self.stParserState1 = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 80))
		self.stParserState1.SetFont(fontText)
		self.stParserState2 = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 120))
		self.stParserState2.SetFont(fontText)

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBrefresh, size=(120, 120), pos=(50, 20))
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)

		self.bClearAlarm = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBclearalarm, size=(120, 120), pos=(50, 160))
		self.Bind(wx.EVT_BUTTON, self.onBClearAlarm, self.bClearAlarm)
		
		self.bReset = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBreset, size=(120, 120), pos=(50, 300))
		self.Bind(wx.EVT_BUTTON, self.onBReset, self.bReset)

		self.enableBasedOnStatus()

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		if devMode:
			if shapeoko is None:
				return

		self.shapeoko.registerNewStatus(self.statusUpdate)
		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.shapeoko.registerNewParserState(self.parserStateUpdate)
		self.Bind(EVT_NEWPARSERSTATE, self.setParserStateEvent)

	def enableBasedOnStatus(self):
		self.bClearAlarm.Enable(self.status == "Alarm")

	def switchToPage(self):
		print("trying to refresh parser state")
		try:
			self.shapeoko.getParserState()
		except Exception as e:
			print("Exception (%s)" % str(e))

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		self.status = evt.status
		w,h = self.dc.GetTextExtent(self.status)
		self.stMachineState.SetLabel(self.status)
		self.stMachineState.SetSize((w, h))
		try:
			cx = StateColors[evt.status.lower()]
		except:
			cx = [0, 0, 0]
		self.stMachineState.SetForegroundColour(wx.Colour(cx))

		self.enableBasedOnStatus()

	def parserStateUpdate(self, newState): # Thread context
		evt = ParserStateEvent(state=newState)
		wx.PostEvent(self, evt)

	def setParserStateEvent(self, evt):
		self.refreshParserState(evt.state)

	def onBRefresh(self, evt):
		self.shapeoko.getParserState()

	def onBClearAlarm(self, evt):
		self.shapeoko.clearAlarm()

	def onBReset(self, evt):
		self.shapeoko.softReset()

	def refreshParserState(self, state):
		self.parserState = state

		s = state.split()
		s1 = " ".join(s[:6])
		s2 = " ".join(s[6:])

		w,h = self.dc.GetTextExtent(s1)
		self.stParserState1.SetLabel(s1)
		self.stParserState1.SetSize((w, h))

		w,h = self.dc.GetTextExtent(s2)
		self.stParserState2.SetLabel(s2)
		self.stParserState2.SetSize((w, h))

