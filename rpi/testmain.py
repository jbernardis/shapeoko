import wx
from wx.lib import newevent


from shapeoko import Shapeoko
from common import XAXIS, YAXIS, ZAXIS, AxisList

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  
(PositionEvent, EVT_NEWPOSITION) = newevent.NewEvent()  



class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None, size=(800, 480), title="")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour("white")

		self.shapeokoStatus = ""
		self.shapeokoMPos = { XAXIS: 0.0, YAXIS: 0.0, ZAXIS: 0.0 }
		self.shapeokoWCO  = { XAXIS: 0.0, YAXIS: 0.0, ZAXIS: 0.0 }
		self.displayPos = { XAXIS: None, YAXIS: None, ZAXIS: None }
		self.showMPos = False

		self.shapeoko = None
		font = wx.Font(72, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Monospace")
		dc = wx.ScreenDC()
		dc.SetFont(font)

		w,h = dc.GetTextExtent("XXXXXXXX")
		self.status = wx.StaticText(self, wx.ID_ANY, "IDLE", pos=(10, 1), size=(w, h))
		self.status.SetFont(font)

		self.stAxisNames = {}
		self.stAxisValues = {}

		self.addPositionLine(XAXIS, 120, font, dc)
		self.addPositionLine(YAXIS, 240, font, dc)
		self.addPositionLine(ZAXIS, 360, font, dc)

		b = wx.Button(self, wx.ID_ANY, "exit", pos=(500, 360))
		self.Bind(wx.EVT_BUTTON, self.onClose, b)

		wx.CallAfter(self.initialize)

	def initialize(self):
		self.shapeoko = Shapeoko("/dev/ttyACM0", "/dev/ttyUSB0")
		self.shapeoko.registerNewStatus(self.statusUpdate)
		self.shapeoko.registerNewPosition(self.positionChange)
		self.shapeoko.go()

		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.Bind(EVT_NEWPOSITION, self.setPositionEvent)

	def addPositionLine(self, axis, ycoord, font, dc):
		labelAxis ="%s:" % axis
		lblw,lblh = dc.GetTextExtent(labelAxis)
		lbl = wx.StaticText(self, wx.ID_ANY, labelAxis, pos=(10, ycoord), size=(lblw, lblh))
		lbl.SetFont(font)
		self.stAxisNames[axis] = lbl

		valueAxis = "   0.00"
		w,h = dc.GetTextExtent(valueAxis)
		value = wx.StaticText(self, wx.ID_ANY, valueAxis, pos=(lblw+20, ycoord), size=(w, h))
		value.SetFont(font)
		self.stAxisValues[axis] = value

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
		for a in AxisList:
			if evt.mpos[a] != self.shapeokoMPos[a]:
				self.shapeokoMPos[a] = evt.mpos[a]
				posChanged = True
			if evt.wco[a] != self.shapeokoWCO[a]:
				self.shapeokoWCO[a] = evt.wco[a]
				posChanged = True

		if posChanged:
			print("new position: [%f %f %f] [%f %f %f]" % (evt.mpos[XAXIS], evt.mpos[YAXIS], evt.mpos[ZAXIS], evt.wco[XAXIS], evt.wco[YAXIS], evt.wco[ZAXIS]))
			for a in AxisList:
				if self.showMPos:
					newValue = self.shapeokoPos[a]
				else:
					newValue = self.shapeokoMPos[a]-self.shapeokoWCO[a]

				self.stAxisValues[a].SetLabel("%7.3f" % newValue)

	def onClose(self, _):
		if self.shapeoko is not None:
			self.shapeoko.terminate()

		self.Destroy()

class App(wx.App):
	def OnInit(self):

		self.frame = MainFrame()
		#self.frame.Show()
		self.frame.ShowFullScreen(True)
#		self.frame.Maximize(True)
#		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()
