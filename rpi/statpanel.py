import wx
from wx.lib import newevent
from common import StateColors, AlarmText

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  
(ParserStateEvent, EVT_NEWPARSERSTATE) = newevent.NewEvent()  
(AlarmEvent, EVT_ALARM) = newevent.NewEvent()  

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

		self.stAlarmText = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 200))
		self.stAlarmText.SetFont(fontText)
		self.stAlarmText.SetForegroundColour(wx.Colour(StateColors["alarm"]))

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBrefresh, size=(120, 120), pos=(50, 20))
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)

		self.bClearAlarm = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBclearalarm, size=(120, 120), pos=(50, 160))
		self.bClearAlarm.SetBitmapDisabled(self.images.pngBclearalarmdis)
		self.Bind(wx.EVT_BUTTON, self.onBClearAlarm, self.bClearAlarm)
		
		self.bReset = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBreset, size=(120, 120), pos=(50, 300))
		self.Bind(wx.EVT_BUTTON, self.onBReset, self.bReset)

		self.enableButtons()

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

		self.shapeoko.registerStatusHandler(self.statusUpdate)
		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)

		self.shapeoko.registerParserStateHandler(self.parserStateUpdate)
		self.Bind(EVT_NEWPARSERSTATE, self.setParserStateEvent)

		self.shapeoko.registerAlarmHandler(self.alarmHandler)
		self.Bind(EVT_ALARM, self.showAlarm)

	def enableButtons(self):
		self.bClearAlarm.Enable(self.status == "Alarm")

	def switchToPage(self):
		try:
			self.shapeoko.getParserState()
		except:
			pass

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

		if evt.status.lower() != "alarm":
			self.showAlarmText("")

		self.enableButtons()

	def parserStateUpdate(self, newState): # Thread context
		evt = ParserStateEvent(state=newState)
		wx.PostEvent(self, evt)

	def setParserStateEvent(self, evt):
		self.refreshParserState(evt.state)

	def alarmHandler(self, msg):  # thread context
		evt = AlarmEvent(msg=msg)
		wx.PostEvent(self, evt)

	def showAlarm(self, evt):
		msg = evt.msg
		try:
			ax = int(msg.split(":")[1])
			txt = AlarmText[ax]
		except:
			txt = "Unknown Alarm: %s" % msg
		self.showAlarmText(txt)

	def showAlarmText(self, txt):
		w,h = self.dc.GetTextExtent(txt)
		self.stAlarmText.SetLabel(txt)
		self.stAlarmText.SetSize((w, h))

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

