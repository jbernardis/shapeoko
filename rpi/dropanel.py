import wx
from wx.lib import newevent

from common import XAXIS, YAXIS, ZAXIS, AxisList

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  
(PositionEvent, EVT_NEWPOSITION) = newevent.NewEvent()  

class DROPanel(wx.Panel):
	def __init__(self, parent, win):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)
		self.shapeokoStatus = ""
		self.shapeokoMPos = { XAXIS: 0.0, YAXIS: 0.0, ZAXIS: 0.0 }
		self.shapeokoWCO  = { XAXIS: 0.0, YAXIS: 0.0, ZAXIS: 0.0 }
		self.displayPos = { XAXIS: None, YAXIS: None, ZAXIS: None }
		self.showMPos = False

		font = wx.Font(72, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Monospace")
		dc = wx.ScreenDC()
		dc.SetFont(font)

		w,h = dc.GetTextExtent("XXXXXXXX")
		self.status = wx.StaticText(self, wx.ID_ANY, "IDLE", pos=(10, 1), size=(w, h))
		self.status.SetFont(font)

		self.stAxisNames = {}
		self.stAxisValues = {}

		lblw, lblh = dc.GetTextExtent("X:")
		valw, valh = dc.GetTextExtent("-0000.000")
		lblPosX = 10;
		valPosX = lblPosX + lblw + 20;

		self.addPositionLine(XAXIS, lblPosX, valPosX, 120, lblw, valw, valh, font)
		self.addPositionLine(YAXIS, lblPosX, valPosX, 240, lblw, valw, valh, font)
		self.addPositionLine(ZAXIS, lblPosX, valPosX, 360, lblw, valw, valh, font)

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		if shapeoko is None:
			return

		self.shapeoko.registerNewStatus(self.statusUpdate)
		self.shapeoko.registerNewPosition(self.positionChange)
		self.shapeoko.go()

		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.Bind(EVT_NEWPOSITION, self.setPositionEvent)

	def addPositionLine(self, axis, lblXCoord, valXCoord, yCoord, lblWidth, valWidth, ht, font):
		labelAxis ="%s:" % axis
		lbl = wx.StaticText(self, wx.ID_ANY, labelAxis, pos=(lblXCoord, yCoord), size=(lblWidth, ht))
		lbl.SetFont(font)
		self.stAxisNames[axis] = lbl

		valueAxis = "      0.000"
		value = wx.StaticText(self, wx.ID_ANY, valueAxis, pos=(valXCoord, yCoord), size=(valWidth, ht))
		value.SetFont(font)
		value.SetForegroundColour((0,0,0)) # set text color
		value.SetBackgroundColour((255,255,255)) # set text back color
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
