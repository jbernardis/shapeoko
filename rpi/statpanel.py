import wx
from wx.lib import newevent

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

		self.bClearAlarm = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBrefresh, size=(120, 120), pos=(50, 140))
		self.Bind(wx.EVT_BUTTON, self.onBClearAlarm, self.bClearAlarm)

		self.bCheck = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBrefresh, size=(120, 120), pos=(50, 260))
		self.Bind(wx.EVT_BUTTON, self.onBCheck, self.bCheck)

		self.enableBasedOnStatus()

	def enableBasedOnStatus(self):
		self.bClearAlarm.Enable(self.status == "Alarm")


	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		self.shapeoko.registerNewStatus(self.statusUpdate)
		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.shapeoko.registerNewParserState(self.parserStateUpdate)
		self.Bind(EVT_NEWPARSERSTATE, self.setParserStateEvent)

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		self.status = evt.status
		w,h = self.dc.GetTextExtent(self.status)
		self.stMachineState.SetLabel(self.status)
		self.stMachineState.SetSize((w, h))
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

	def onBCheck(self, evt):
		self.shapeoko.checkMode()

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

