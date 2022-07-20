import wx
from wx.lib import newevent

from common import XAXIS, YAXIS, ZAXIS, AxisList, StateColors

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  
(PositionEvent, EVT_NEWPOSITION) = newevent.NewEvent()  

class DROPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.images = images

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)
		self.shapeokoStatus = ""
		self.shapeokoMPos = { XAXIS: 0.0, YAXIS: 0.0, ZAXIS: 0.0 }
		self.shapeokoWCO  = { XAXIS: 0.0, YAXIS: 0.0, ZAXIS: 0.0 }
		self.displayPos = { XAXIS: None, YAXIS: None, ZAXIS: None }
		self.showMPos = False

		font = wx.Font(56, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		fontCoords = wx.Font(56, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		fontButton = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
		dc = wx.ScreenDC()
		dc.SetFont(font)

		w,h = dc.GetTextExtent("XXXXXXXX")
		self.status = wx.StaticText(self, wx.ID_ANY, "", pos=(10, 1), size=(w, h))
		self.status.SetFont(font)

		self.bCoord = wx.Button(self, wx.ID_ANY, "Work", pos=(550, 30), size=(160, 60))
		self.bCoord.SetFont(fontButton)
		self.Bind(wx.EVT_BUTTON, self.onBCoord, self.bCoord)

		self.stAxisNames = {}
		self.stAxisValues = {}

		lblw, lblh = dc.GetTextExtent("X:")
		valw, valh = dc.GetTextExtent("-0000.000")
		lblPosX = 10
		valPosX = lblPosX + lblw + 20

		self.addPositionLine(XAXIS, lblPosX, valPosX, 100, lblw, valw, valh, font, fontCoords)
		self.addPositionLine(YAXIS, lblPosX, valPosX, 200, lblw, valw, valh, font, fontCoords)
		self.addPositionLine(ZAXIS, lblPosX, valPosX, 300, lblw, valw, valh, font, fontCoords)

		basex = 550 + 50
		basey = 180

		bdim = 45
		self.bResetX = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisx, size=(54, 54), pos=(basex, basey))
		self.bResetY = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisy, size=(54, 54), pos=(basex, basey+70))
		self.bResetZ = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAxisz, size=(54, 54), pos=(basex, basey+70*2))
		self.bResetX.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, XAXIS))
		self.bResetY.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, YAXIS))
		self.bResetZ.Bind(wx.EVT_BUTTON,  lambda event: self.onResetButton(event, ZAXIS))

		txt = "RESET"
		dc.SetFont(fontButton)
		w,h = dc.GetTextExtent(txt)
		hdr = wx.StaticText(self, wx.ID_ANY, txt, pos=(basex-int(w/4), basey-h-10), size=(w, h))
		hdr.SetFont(fontButton)


	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		self.displayPosition()

		self.shapeoko.registerStatusHandler(self.statusUpdate)
		self.shapeoko.registerPositionHandler(self.positionChange)

		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)
		self.Bind(EVT_NEWPOSITION, self.setPositionEvent)

	def addPositionLine(self, axis, lblXCoord, valXCoord, yCoord, lblWidth, valWidth, ht, fontText, fontCoords):
		labelAxis ="%s:" % axis
		lbl = wx.StaticText(self, wx.ID_ANY, labelAxis, pos=(lblXCoord, yCoord), size=(lblWidth, ht))
		lbl.SetFont(fontText)
		self.stAxisNames[axis] = lbl

		valueAxis = "      0.000"
		value = wx.StaticText(self, wx.ID_ANY, valueAxis, pos=(valXCoord, yCoord), size=(valWidth, ht))
		value.SetFont(fontCoords)
		value.SetForegroundColour((0,0,0)) # set text color
		value.SetBackgroundColour((255,255,255)) # set text back color
		self.stAxisValues[axis] = value

	def onBCoord(self, evt):
		self.showMPos = not self.showMPos
		if self.showMPos:
			self.bCoord.SetLabel("Machine")
		else:
			self.bCoord.SetLabel("Work")
		self.displayPosition()

	def onResetButton(self, evt, axis):
		if axis == XAXIS:
			self.shapeoko.resetAxis(x=0)
		elif axis == YAXIS:
			self.shapeoko.resetAxis(y=0)
		elif axis == ZAXIS:
			self.shapeoko.resetAxis(z=0)

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		self.shapeokoStatus = evt.status
		self.status.SetLabel(evt.status)
		try:
			cx = StateColors[evt.status.lower()]
		except:
			cx = [0, 0, 0]
		self.status.SetForegroundColour(wx.Colour(cx))
		
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
			self.displayPosition()

	def displayPosition(self):
		for a in AxisList:
			if self.showMPos:
				newValue = self.shapeokoMPos[a]
			else:
				newValue = self.shapeokoMPos[a]-self.shapeokoWCO[a]

			self.stAxisValues[a].SetLabel("%9.3f" % newValue)
