import wx
from wx.lib import newevent


from grbl import Grbl

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  
(PositionEvent, EVT_NEWPOSITION) = newevent.NewEvent()  


class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None, size=(800, 480), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour("white")

		self.shapeokoStatus = ""
		self.shapeokoMPos = [0.0, 0.0, 0.0]
		self.shapeokoWCO  = [0.0, 0.0, 0.0]
		self.displayPos = [None, None, None]
		self.showMPos = False

		self.grbl = None
		font = wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial Black")


		self.status = wx.StaticText(self, wx.ID_ANY, "IDLE", pos=(10, 1))
		self.status.SetFont(font)

		self.posX = self.addPositionLine("X", 160, font)
		self.posY = self.addPositionLine("Y", 320, font)
		self.posZ = self.addPositionLine("Z", 480, font)

		b = wx.Button(self, wx.ID_ANY, "exit", pos=(500, 480))
		self.Bind(wx.EVT_BUTTON, self.onClose, b)

		#wx.CallAfter(self.initialize)

	def initialize(self):
		self.grbl = Grbl("/dev/ttyACM0", "/dev/ttyUSB0")
		self.grbl.registerNewStatus(self.statusUpdate)
		self.grbl.registerNewPosition(self.positionChange)
		self.grbl.go()

		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.Bind(EVT_NEWPOSITION, self.setPositionEvent)


	def addPositionLine(self, axis, ycoord, font):
		lbl = wx.StaticText(self, wx.ID_ANY, "%s:" % axis, pos=(10, ycoord))
		lbl.SetFont(font)
		value = wx.StaticText(self, wx.ID_ANY, "0000.000", pos=(60, ycoord))
		value.SetFont(font)
		return value

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		print("new status = (%s)" % evt.status)
		self.shapeokoStatus = evt.status
		self.status.SetLabel(evt.status)

	def positionChange(self, pos, off): # thread context
		evt = PositionEvent(mpos=pos, wco=off)
		wx.PostEvent(self, evt)

	def setPositionEvent(self, evt):
		posChanged = False
		for i in range(3):
			if evt.mpos[i] != self.shapeokoMPos[i]:
				self.shapeokoMPos[i] = evt.mpos[i]
				posChanged = True
			if evt.wco[i] != self.shapeokoWCO[i]:
				self.shapeokoWCO[i] = evt.wco[i]
				posChanged = True
		if posChanged:
			print("new position: [%f %f %f] [%f %f %f]" % (evt.mpos[0], evt.mpos[1], evt.mpos[2], evt.wco[0], evt.wco[1], evt.wco[2]))
			if self.showMPos:
				nx, ny, nz = self.shapeokoMPos
			else:
				nx, ny, nz = [self.shapeokoMPos[i]-self.shapeokoWCO[i] for i in range(3)]

			for stpos, nv in [[self.posX, nx], [self.poxY, ny], [self.posZ, nz]]:
				nvl = "%7.3f" % nv
				stpos.SetLabel(nvl)

	def onClose(self, _):
		if self.grbl is not None:
			self.grbl.terminate()

		self.Destroy()

class App(wx.App):
	def OnInit(self):

		self.frame = MainFrame()
		self.frame.ShowFullScreen(True)
#		self.frame.Maximize(True)
#		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()
