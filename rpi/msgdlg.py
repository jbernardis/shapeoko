import wx

class MessageDlg(wx.Dialog):
	def __init__(self, parent, caption, msg):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, caption, style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(111, 237, 134))
		self.Bind(wx.EVT_ACTIVATE, self.activate)

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

		print(self.msgfld.GetSize())

		self.SetClientSize((w+40, h+40))


	def activate(self, evt):
		print("in activate")
		self.msgfld.SetPosition((20, 20))
		evt.Skip()

	def onClose(self, _):
		self.doDestroy()
		
	def doDestroy(self):
		self.Destroy()
