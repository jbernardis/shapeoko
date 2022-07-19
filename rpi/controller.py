import os
import wx
from wx.lib import newevent
import sys

ShutDownFlag = False

DEPLOYED = False

from shapeoko import Shapeoko
from images import Images
from dropanel import DROPanel
from statpanel import StatPanel
from jobpanel import JobPanel
from jogpanel import JogPanel 
from overridepanel import OverridePanel
from configpanel import ConfigPanel
from logpanel import LogPanel
from settings import Settings
from msgdlg import MessageDlg

(CloseRequest, EVT_CLOSEREQUEST) = newevent.NewEvent()
(FeedbackMsg, EVT_FEEDBACK) = newevent.NewEvent()

class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))
		self.SetClientSize((800, 480))

		self.initialized = False
		self.shapeoko = None
		self.settings = Settings()

		self.images = Images("images")
		self.registeredTickers = []
		self.registeredLogs = []

		self.lb = wx.Listbook(self, wx.ID_ANY, style=wx.BK_RIGHT)
		il = wx.ImageList(32, 32)

		il.Add(self.images.pngDropanel)
		il.Add(self.images.pngStatpanel)
		il.Add(self.images.pngJobpanel)
		il.Add(self.images.pngJogpanel)
		il.Add(self.images.pngOverridepanel)
		il.Add(self.images.pngCfgpanel)
		il.Add(self.images.pngLogpanel)

		il.Add(self.images.pngExitpanel)

		self.lb.AssignImageList(il)

		self.DROPanel = DROPanel(self.lb, self)
		self.StatPanel = StatPanel(self.lb, self, self.images)
		self.JobPanel = JobPanel(self.lb, self, self.images)
		self.JogPanel = JogPanel(self.lb, self, self.images)
		self.OverridePanel = OverridePanel(self.lb, self, self.images)
		self.CfgPanel = ConfigPanel(self.lb, self, self.images)
		self.LogPanel = LogPanel(self.lb, self, self.images)

		if not DEPLOYED:
			self.ExitPanel = ExitPanel(self.lb, self)

		self.pages = [
			[ self.DROPanel, "DRO", 0 ],
			[ self.StatPanel, "Status", 1 ],
			[ self.JobPanel, "Job", 2 ],
			[ self.JogPanel, "Jog", 3 ],
			[ self.OverridePanel, "Override", 4 ],
			[ self.CfgPanel, "Config", 5 ],
			[ self.LogPanel, "Log", 6 ]
		]

		if not DEPLOYED:
			self.pages.append([ self.ExitPanel, "EXIT", 7 ]) 

		for pg in self.pages:
			self.lb.AddPage(pg[0], pg[1], imageId=pg[2])

		self.lb.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.onPageChanged)

		self.Bind(EVT_CLOSEREQUEST, self.onCloseRequest)
		self.Bind(EVT_FEEDBACK, self.onFeedback)

		self.timer = wx.Timer(self)

		wx.CallAfter(self.initialize)

	def onPageChanged(self, evt):
		page = evt.GetSelection()
		try:
			self.pages[page][0].switchToPage()
		except AttributeError:
			pass

	def isDeployed(self):
		return DEPLOYED

	def initialize(self):
		try:
			self.shapeoko = Shapeoko(self, self.settings)
		except Exception as e:
			print("exception (%s)" % str(e))
			self.shapeoko = None
			return

		for pg in self.pages:
			try:
				pg[0].initialize(self.shapeoko, self.settings)
			except AttributeError:
				pass

		self.Bind(wx.EVT_TIMER, self.ticker)
		self.timer.Start(1000)

		if self.shapeoko is not None:
			self.shapeoko.go()
		
		self.initialized = True

	def showFeedback(self, msg):  # thread context
		evt = FeedbackMsg(msg=msg)
		wx.PostEvent(self, evt)

	def onFeedback(self, evt):
		dlg = MessageDlg(None, "Feedback", [evt.msg], 5)
		dlg.CenterOnParent()
		dlg.Show()

	def registerTicker(self, cbTicker):
		self.registeredTickers.append(cbTicker)

	def ticker(self, evt):
		for cb in self.registeredTickers:
			cb()

	def registerLogHandler(self, cbLog):
		self.registeredLogs.append(cbLog)

	def log(self, msg):
		for cb in self.registeredLogs:
			cb(msg)

	def getJobInfo(self):
		return self.JobPanel.getJobInfo()

	def requestClose(self, shutdown=False):
		evt = CloseRequest(shutdown=shutdown)
		wx.PostEvent(self, evt)

	def onCloseRequest(self, evt):
		global ShutDownFlag
		try:
			ShutDownFlag = evt.shutdown
			
		except:
			ShutDownFlag = False

		self.doClose()

	def onClose(self, evt):
		self.doClose()

	def doClose(self):
		self.settings.save()
		
		if self.shapeoko is not None:
			self.shapeoko.terminate()

		self.Destroy()

class ExitPanel(wx.Panel):
	def __init__(self, parent, win):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.win = win
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		self.b = wx.Button(self, wx.ID_ANY, "exit", pos=(50, 50), size=(120, 120))
		self.Bind(wx.EVT_BUTTON, win.onClose, self.b)

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.ShowFullScreen(True)
		return True

if DEPLOYED:
	ofp = open("shapeoko.out", "w")
	efp = open("shapeoko.err", "w")
	sys.stdout = ofp
	sys.stderr = efp

app = App(False)
app.MainLoop()

if ShutDownFlag:
	os.system("sudo poweroff")
