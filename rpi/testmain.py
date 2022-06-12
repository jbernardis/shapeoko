import wx

from shapeoko import Shapeoko
from images import Images
from dropanel import DROPanel
from statpanel import StatPanel
from jobpanel import JobPanel
from jogpanel import JogPanel 
from settings import Settings


class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))
		self.SetClientSize((800, 480))

		self.shapeoko = None
		self.settings = Settings()

		self.images = Images("images")

		self.lb = wx.Listbook(self, wx.ID_ANY, style=wx.BK_RIGHT)
		il = wx.ImageList(32, 32)

		il.Add(self.images.pngDropanel)
		il.Add(self.images.pngStatpanel)
		il.Add(self.images.pngJobpanel)
		il.Add(self.images.pngJogpanel)
		il.Add(self.images.pngExitpanel)
		self.lb.AssignImageList(il)

		self.DROPanel = DROPanel(self.lb, self)
		self.lb.AddPage(self.DROPanel, "DRO", imageId=0)

		self.StatPanel = StatPanel(self.lb, self)
		self.lb.AddPage(self.StatPanel, "Status", imageId=1)

		self.JobPanel = JobPanel(self.lb, self)
		self.lb.AddPage(self.JobPanel, "Job", imageId=2)

		self.JogPanel = JogPanel(self.lb, self)
		self.lb.AddPage(self.JogPanel, "Jog", imageId=3)




		self.ExitPanel = ExitPanel(self.lb, self)
		self.lb.AddPage(self.ExitPanel, "EXIT", imageId=4)

		wx.CallAfter(self.initialize)

	def initialize(self):
		try:
			self.shapeoko = Shapeoko(self.settings.ttyshapeoko, self.settings.ttypendant)
		except Exception as e:
			print("exception (%s)" % str(e))
			self.shapeoko = None

		self.DROPanel.initialize(self.shapeoko, self.settings)
		self.StatPanel.initialize(self.shapeoko, self.settings)
		self.JobPanel.initialize(self.shapeoko, self.settings)
		self.JogPanel.initialize(self.shapeoko, self.settings)


		self.ExitPanel.initialize(self)

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
		self.frame.Show()
		#self.frame.ShowFullScreen(True)
#		self.frame.Maximize(True)
#		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()
