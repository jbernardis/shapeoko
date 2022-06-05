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
		self.showMPos = False

		self.grbl = None

		sizer = wx.BoxSizer(wx.VERTICAL)
		self.stStatus = wx.StaticText(self, wx.ID_ANY, "IDLE")

		hsizer, self.posX = self.addPositionLine("X")
		sizer.Add(hsizer)
		hsizer, self.posY = self.addPositionLine("Y")
		sizer.Add(hsizer)
		hsizer, self.posZ = self.addPositionLine("Z")
		sizer.Add(hsizer)

		sizer.AddSpacer(10)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit()

		#wx.CallAfter(self.initialize)

	def initialize(self):
		self.grbl = Grbl("/dev/ttyACM0", "/dev/ttyUSB0")
		self.grbl.registerNewStatus(self.statusUpdate)
		self.grbl.registerNewPosition(self.positionChange)
		self.grbl.go()

		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.Bind(EVT_NEWPOSITION, self.setPositionEvent)


	def addPositionLine(self, axis):
		sz = wx.BoxSizer(wx.HORIZONTAL)
		lbl = wx.StaticText(self, wx.ID_ANY, "%s:" % axis)
		sz.Add(lbl)
		value = wx.StaticText(self, wx.ID_ANY, "                    ")
		sz.Add(value)
		return sz, value

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		print("new status = (%s)" % evt.status)
		self.displayStatus(evt.status)

	def displayStatus(self, status):
		self.shapeokoStatus = status
		self.stStatus.SetLabel(status)

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

	def onClose(self, _):
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
