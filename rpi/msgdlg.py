import wx

class MessageDlg(wx.Dialog):
	def __init__(self, parent, caption, msg, timeout):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, caption, style=wx.CAPTION | wx.STAY_ON_TOP)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(111, 237, 134))

		self.timeout = timeout

		font = wx.Font(28, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.dc = wx.ScreenDC()
		self.dc.SetFont(font)

		msgString = "\n".join(msg)
		self.msgfld = wx.StaticText(self, wx.ID_ANY, msgString, pos=(20, 20))
		self.msgfld.SetFont(font)
		maxw = 0
		maxh = 0
		for ml in msg:
			w,h = self.dc.GetTextExtent(ml)
			if w > maxw:
				maxw = w
			if h > maxh:
				maxh = h
		w = maxw
		h = maxh * len(msg)
		self.msgfld.SetLabel(msgString)
		self.msgfld.SetSize((w, h))

		self.SetClientSize((w+40, h+40))
		wx.CallAfter(self.initialize)

	def initialize(self):
		self.msgfld.SetPosition((20, 20))
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onClose)
		self.timer.Start(1000 * self.timeout)

	def onClose(self, _):
		self.doDestroy()
		
	def doDestroy(self):
		self.Destroy()
