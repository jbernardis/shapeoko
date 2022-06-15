import wx

from shapeoko import Shapeoko
from images import Images
from dropanel import DROPanel
from statpanel import StatPanel
from jobpanel import JobPanel
from jogpanel import JogPanel 
from settings import Settings
from common import devMode


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

		self.lb = wx.Listbook(self, wx.ID_ANY, style=wx.BK_RIGHT)
		il = wx.ImageList(32, 32)

		il.Add(self.images.pngDropanel)
		il.Add(self.images.pngStatpanel)
		il.Add(self.images.pngJobpanel)
		il.Add(self.images.pngJogpanel)

		il.Add(self.images.pngExitpanel)

		self.lb.AssignImageList(il)

		self.DROPanel = DROPanel(self.lb, self)
		self.StatPanel = StatPanel(self.lb, self, self.images)
		self.JobPanel = JobPanel(self.lb, self, self.images)
		self.JogPanel = JogPanel(self.lb, self, self.images)

		self.ExitPanel = ExitPanel(self.lb, self)  #######REMOVE

		self.pages = [
			[ self.DROPanel, "DRO", 0 ],
			[ self.StatPanel, "Status", 1 ],
			[ self.JobPanel, "Job", 2 ],
			[ self.JogPanel, "Jog", 3 ]
		]

		self.pages.append([ self.ExitPanel, "EXIT", 4 ])  #######Remove

		for pg in self.pages:
			self.lb.AddPage(pg[0], pg[1], imageId=pg[2])

		self.lb.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.onPageChanged)

		self.timer = wx.Timer(self)

		wx.CallAfter(self.initialize)

	def onPageChanged(self, evt):
		page = evt.GetSelection()
		try:
			self.pages[page][0].switchToPage()
		except AttributeError:
			pass

	def initialize(self):
		try:
			self.shapeoko = Shapeoko(self.settings)
		except Exception as e:
			print("exception (%s)" % str(e))
			self.shapeoko = None
			#return

		self.DROPanel.initialize(self.shapeoko, self.settings)
		self.StatPanel.initialize(self.shapeoko, self.settings)
		self.JobPanel.initialize(self.shapeoko, self.settings)
		self.JogPanel.initialize(self.shapeoko, self.settings)

		self.timer.Start(1000)
		self.Bind(wx.EVT_TIMER, self.ticker)

		self.ExitPanel.initialize(self)  ######REMOVE

		if self.shapeoko is not None:
			self.shapeoko.go()
		
		self.initialized = True

	def registerTicker(self, cbTicker):
		self.registeredTickers.append(cbTicker)

	def ticker(self, evt):
		for cb in self.registeredTickers:
			cb()

	def onClose(self, _):
		self.settings.save()
		
		if self.shapeoko is not None:
			self.shapeoko.terminate()

		self.Destroy()

class ExitPanel(wx.Panel):
	def __init__(self, parent, win):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		self.b = wx.Button(self, wx.ID_ANY, "exit", pos=(50, 50), size=(120, 120))

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, win):
		self.Bind(wx.EVT_BUTTON, win.onClose, self.b)

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		if devMode:
			self.frame.Show()
		else:
			self.frame.ShowFullScreen(True)
		return True

app = App(False)
app.MainLoop()
