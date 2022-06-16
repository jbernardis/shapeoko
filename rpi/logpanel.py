import wx
from wx.lib import newevent

(AlarmEvent, EVT_ALARM) = newevent.NewEvent()  
(ErrorEvent, EVT_ERROR) = newevent.NewEvent()  


class LogPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.parentFrame = win
		self.images = images

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

		self.shapeoko.registerAlarmHandler(self.alarmHandler)
		self.Bind(EVT_ALARM, self.showAlarm)

		self.shapeoko.registerErrorHandler(self.errorHandler)
		self.Bind(EVT_ERROR, self.showError)

	def alarmHandler(self, msg):  # thread context
		evt = AlarmEvent(msg=msg)
		wx.PostEvent(self, evt)

	def showAlarm(self, evt):
		msg = evt.msg
		print("log showAlarm: (%s)" % msg)

	def errorHandler(self, status, msg):  # thread context
		evt = AlarmEvent(status=status, msg=msg)
		wx.PostEvent(self, evt)

	def showError(self, evt):
		status = evt.status
		msg = evt.msg
		print("log showError: (%s) (%s)" % (status, msg))

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())
