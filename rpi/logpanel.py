import wx
from wx.lib import newevent

from common import AlarmText, ErrorText

(AlarmEvent, EVT_ALARM) = newevent.NewEvent()  
(ErrorEvent, EVT_ERROR) = newevent.NewEvent()  
(MessageEvent, EVT_MESSAGE) = newevent.NewEvent()  


class LogPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.parentFrame = win
		self.images = images
		self.verboseOutput = True
		self.showStatusOutput = False

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		self.teLog = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.HSCROLL, size=(400, 400), pos=(0, 0))
		font = wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.teLog.SetFont(font)

		self.cbVerbose = wx.CheckBox(self, wx.ID_ANY, "Verbose", pos=(40, 420), size=(120, 21))
		self.cbVerbose.SetFont(font)
		self.cbVerbose.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.onCbVerbose, self.cbVerbose)

		self.cbStatus = wx.CheckBox(self, wx.ID_ANY, "Status", pos=(200, 420), size=(120, 21))
		self.cbStatus.SetFont(font)
		self.Bind(wx.EVT_CHECKBOX, self.onCbStatus, self.cbStatus)

		self.bClear = wx.BitmapButton(self, wx.ID_ANY, images.pngBclearlog, size=(100, 60), pos=(500, 410))
		self.Bind(wx.EVT_BUTTON, self.onBClear, self.bClear)

	def onCbVerbose(self, _):
		self.verboseOutput = self.cbVerbose.GetValue()

	def onCbStatus(self, _):
		self.showStatusOutput = self.cbStatus.GetValue()

	def onBClear(self, _):
		self.teLog.Clear()

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

		h, v = self.GetClientSize()
		self.teLog.SetSize((h, v-80))

		self.shapeoko.registerAlarmHandler(self.alarmHandler)
		self.Bind(EVT_ALARM, self.showAlarm)

		self.shapeoko.registerErrorHandler(self.errorHandler)
		self.Bind(EVT_ERROR, self.showError)

		self.shapeoko.registerMessageHandler(self.messageHandler)
		self.Bind(EVT_MESSAGE, self.showMessage)

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

		self.teLog.AppendText("ALARM (%s)\n" % txt)

	def errorHandler(self, status, msg):  # thread context
		evt = ErrorEvent(status=status, msg=msg)
		wx.PostEvent(self, evt)

	def showError(self, evt):
		status = evt.status
		msg = evt.msg
		try:
			ex = int(status.split(":")[1])
			txt = ErrorText[ex]
		except:
			txt = "Unknown Error: %s" % status

		self.teLog.AppendText("ERROR (%s) (%s)\n" % (txt, msg))

	def messageHandler(self, msg, verbose=False, status=False):  # thread context
		if verbose and not self.verboseOutput:
			return

		if status and not self.showStatusOutput:
			return

		evt = MessageEvent(msg=msg)
		wx.PostEvent(self, evt)

	def showMessage(self, evt):
		self.teLog.AppendText(evt.msg + "\n")

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())
