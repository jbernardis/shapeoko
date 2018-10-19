import wx
import os
import time

from model import Model

BTNDIM = (48, 48)

def timeStamp():
	return time.asctime()

class RenderDlg(wx.Dialog):
	def __init__(self, parent, objList, cnc, toolList, images, settings):
		self.parent = parent
		self.objList = objList
		self.cnc = cnc
		self.toolList = toolList
		self.images = images
		self.settings = settings
		
		self.rendering = None
		self.savedRendering = False
		
		wx.Dialog.__init__(self, None, wx.ID_ANY, "Render")
		sz = wx.BoxSizer(wx.VERTICAL)
				
		box = wx.StaticBox(self, wx.ID_ANY, " Options ")
		bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		
		self.cbComment = wx.CheckBox(self, wx.ID_ANY, " Add Comments to G Code ")
		self.cbComment.SetValue(True)
		bsizer.Add(self.cbComment)
		bsizer.AddSpacer(5)
		
		self.cbAddSpeed = wx.CheckBox(self, wx.ID_ANY, " Add Speeds to G Code ")
		self.cbAddSpeed.SetValue(True)
		bsizer.Add(self.cbAddSpeed)
		bsizer.AddSpacer(5)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Decimal Places:"), 0, wx.ALIGN_CENTER_VERTICAL)
		
		sc = wx.SpinCtrl(self, wx.ID_ANY, size=(60, -1))
		sc.SetRange(2, 7)
		sc.SetValue(4)
		hsz.Add(sc, 0, wx.ALIGN_CENTER_VERTICAL)
		self.scPlaces = sc
		bsizer.Add(hsz)
		
		sz.Add(bsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sz.AddSpacer(10)
				
		box = wx.StaticBox(self, wx.ID_ANY, " Offsets ")
		bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "X:"), 0, wx.ALIGN_CENTER_VERTICAL)
		
		sc = wx.SpinCtrl(self, wx.ID_ANY, size=(60, -1))
		sc.SetRange(-1000, 1000)
		sc.SetValue(0)
		hsz.Add(sc, 0, wx.ALIGN_CENTER_VERTICAL)
		self.scOffX = sc
		hsz.AddSpacer(10)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Y:"), 0, wx.ALIGN_CENTER_VERTICAL)
		
		sc = wx.SpinCtrl(self, wx.ID_ANY, size=(60, -1))
		sc.SetRange(-1000, 1000)
		sc.SetValue(0)
		hsz.Add(sc, 0, wx.ALIGN_CENTER_VERTICAL)
		self.scOffY = sc
		hsz.AddSpacer(10)
		
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Z:"), 0, wx.ALIGN_CENTER_VERTICAL)
		
		sc = wx.SpinCtrl(self, wx.ID_ANY, size=(60, -1))
		sc.SetRange(-10, 10)
		sc.SetValue(0)
		hsz.Add(sc, 0, wx.ALIGN_CENTER_VERTICAL)
		self.scOffZ = sc
		bsizer.Add(hsz)
		
		sz.Add(bsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		sz.AddSpacer(10)

		box = wx.StaticBox(self, wx.ID_ANY, " Selected Tool ")
		bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

		self.chTool = wx.Choice(self, wx.ID_ANY, size=[200, -1], choices=[t["name"] for t in self.toolList])
		self.chTool.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.onToolChoice, self.chTool)
		bsizer.Add(self.chTool, 0,  wx.ALL, 5)
		sz.Add(bsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		sz.AddSpacer(10)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		
		b = wx.BitmapButton(self, wx.ID_ANY, self.images.pngRender, size=BTNDIM)
		b.SetToolTip("Render G Code")
		self.Bind(wx.EVT_BUTTON, self.onBRender, b)
		bsz.Add(b)
		bsz.AddSpacer(10)
		
		cb = wx.CheckBox(self, wx.ID_ANY, "Add preamble")
		cb.SetToolTip("Add G Code preamble")
		cb.SetValue(True)
		bsz.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL)
		bsz.AddSpacer(20)
		self.cbPreamble = cb
		
		b = wx.BitmapButton(self, wx.ID_ANY, self.images.pngSaveas, size=BTNDIM)
		b.SetToolTip("Save G Code")
		self.Bind(wx.EVT_BUTTON, self.onBSaveAs, b)
		b.Enable(False)
		self.bSaveAs = b
		bsz.Add(b)
		bsz.AddSpacer(10)
		
		cb = wx.CheckBox(self, wx.ID_ANY, "Append")
		cb.SetToolTip("Append G Code to an existing file")
		cb.SetValue(False)
		cb.Enable(False)
		bsz.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL)
		bsz.AddSpacer(20)
		self.cbAppend = cb
				
		b = wx.BitmapButton(self, wx.ID_ANY, self.images.pngExit, size=BTNDIM)
		b.SetToolTip("Exit Dialog")
		self.Bind(wx.EVT_BUTTON, self.onBExit, b)
		bsz.Add(b)
		
		sz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(sz)
		hsz.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(10)
		sz.Add(wx.StaticText(self, wx.ID_ANY, "Rendering Log"))
		self.tcLog = wx.TextCtrl(self, wx.ID_ANY, "", size=(600, 300), style=wx.TE_READONLY+wx.TE_MULTILINE)
		sz.Add(self.tcLog)
		sz.AddSpacer(10)
		
		hsz.Add(sz, 0, wx.EXPAND)
		hsz.AddSpacer(10)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def onToolChoice(self, evt):
		s = self.chTool.GetSelection()
		if s == wx.NOT_FOUND:
			return

		tool = self.toolList[s]
		self.cnc.setTool(tool)

	def onBRender(self, evt):
		self.tcLog.Clear()
		self.renderInfo("Rendering started at %s" % timeStamp())
		cmt = self.cbComment.GetValue()
		spd = self.cbAddSpeed.GetValue()
		places = self.scPlaces.GetValue()
		addPreamble = self.cbPreamble.GetValue()
				
		self.cnc.setOptions(commentCode=cmt, addSpeed=spd, decimalPlaces = places)
		
		ox = self.scOffX.GetValue()
		oy = self.scOffY.GetValue()
		oz = self.scOffZ.GetValue()
		self.cnc.setOffset(ox, oy, oz)
		m = Model()
		for o in self.objList:
			m.addObject(o)
		self.rendering = m.render(self.cnc, self, addPreamble)
		self.renderInfo("%d lines of G Code generated" % len(self.rendering))
		self.savedRendering = False
		self.bSaveAs.Enable(True)
		self.cbAppend.Enable(True)
		self.renderInfo("Rendering completed at %s" % timeStamp())
			
	def onBSaveAs(self, evt):
		append = self.cbAppend.GetValue()

		skey = "gcodedir"
		sdir = self.settings.setting(skey)
		style = wx.FD_SAVE
		openMode = "a"
		text = "appended"
		if not append:
			style += wx.FD_OVERWRITE_PROMPT
			openMode = "w"
			text = "saved"

		with wx.FileDialog(self, "Save G Code file", wildcard="NC files (*.nc)|*.nc",
					defaultDir=sdir,
					style=style) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			pathname = fileDialog.GetPath()
			ndir = os.path.dirname(pathname)
			
			if ndir != sdir:
				self.settings.setSetting(skey, ndir)
				
			try:
				with open(pathname, openMode) as file:
					for l in self.rendering:
						file.write(l+"\n")
					self.renderInfo("G Code %s to file '%s'." % (text, pathname))
				self.savedRendering = True
			except IOError:
				self.renderError("Cannot save current data in file '%s'." % pathname)
			
	def onBExit(self, evt):
		if self.rendering is not None and not self.savedRendering:
			dlg = wx.MessageDialog(self, 'Are you sure you want to exit without saving?',
								   'Discard Rendering?',
								   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
			rc = dlg.ShowModal()
			dlg.Destroy()
	
			if rc == wx.ID_NO:
				return

		self.EndModal(wx.ID_OK)

	def renderInfo(self, text):
		self.tcLog.AppendText(text+"\n")

	def renderError(self, text):
		self.tcLog.AppendText("ERROR: %s\n" % text)

	def renderWarning(self, text):
		self.tcLog.AppendText("WARNING: %s\n" % text)

		
