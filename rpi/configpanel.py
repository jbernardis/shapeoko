import wx
from wx.lib import newevent

from common import Settings

(ConfigEvent, EVT_CONFIG) = newevent.NewEvent()  

class ConfigPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.parentFrame = win
		self.images = images

		fontText = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.dc = wx.ScreenDC()
		self.dc.SetFont(fontText)

		self.stVersion = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 20))
		self.stVersion.SetFont(fontText)

		self.lcConfig = ConfigListCtrl(self)
		self.lcConfig.SetPosition(0, 60)

		self.values = {}
		for k in Settings.keys():
			self.values[k] = None

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings
		
		h, v = self.GetClientSize()
		self.lcConfig.SetSize((h, v))
		self.lcConfig.SetPosition((0, 0))

		self.lcConfig.setValues(self.values)

		self.shapeoko.registerConfigHandler(self.configHandler)
		self.Bind(EVT_CONFIG, self.showConfig)

	def configHandler(self, msg):  # thread context
		evt = ConfigEvent(msg=msg)
		wx.PostEvent(self, evt)

	def showConfig(self, evt):
		msg = evt.msg

		if msg.startswith("Grbl"):
			l = msg.split()
			versionString = "%s %s" % (l[0], l[1])
			self.stVersion.SetLabel(versionString)
		else:
			cx, val = msg[1:].split("=", 1)
			try:
				icx = int(cx)
			except:
				icx = None
			if icx is not None and icx in Settings.keys():
				self.values[icx] = val
				self.lcConfig.refreshItem(icx)

	def switchToPage(self):
		try:
			self.shapeoko.getConfig()
		except:
			pass

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

class ConfigListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(700, 280),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.parent = parent
		
		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.SetFont(font)

		self.cfgKeys = sorted(Settings.keys())
		
		self.InsertColumn(0, "Parameter")
		self.InsertColumn(1, "Value")
		self.InsertColumn(2, "Units")
		self.InsertColumn(3, "Description")
		self.SetColumnWidth(0, 140)
		self.SetColumnWidth(1, 140)
		self.SetColumnWidth(2, 140)
		self.SetColumnWidth(3, 280)
		
		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

	def refreshItem(self, cx):
		try:
			kx = self.cfgKeys.index(cx)
		except ValueError:
			return

		self.RefreshItem(kx)
		
	def setValues(self, vl):
		self.values = vl
		self.SetItemCount(len(self.values))	
		
	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)
			
	def OnGetItemText(self, item, col):
		k = self.cfgKeys[item]

		if col == 0:
			return "%-3d" % k
		elif col == 1:
			if self.values[k] is None:
				return "???"
			else:
				return "%s" % str(self.values[k])
		elif col == 2:
			return Settings[k]["units"]
		elif col == 3:
			return Settings[k]["setting"]

		return "??"

	def OnGetItemAttr(self, item):		
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
