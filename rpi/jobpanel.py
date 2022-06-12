import wx
import glob
import os

ACTION_LOAD = 0
ACTION_DELETE = 1

class JobPanel(wx.Panel):
	def __init__(self, parent, win):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		font = wx.Font(72, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Monospace")
		fontButton = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Monospace")
		fontText = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Monospace")
		self.dc = wx.ScreenDC()
		self.dc.SetFont(fontText)

		self.currentFile = None


		self.bFiles = wx.Button(self, wx.ID_ANY, "Files", size=(120, 120), pos=(50, 20))
		self.bFiles.SetFont(fontButton)
		self.Bind(wx.EVT_BUTTON, self.onBFiles, self.bFiles)

		st = wx.StaticText(self, wx.ID_ANY, "Current file:", pos=(200, 30))
		st.SetFont(fontText)

		self.stFileName = wx.StaticText(self, wx.ID_ANY, "", pos=(240, 80))
		self.stFileName.SetFont(fontText)

		self.bCheckSize = wx.Button(self, wx.ID_ANY, "Check\nSize", size=(120, 120), pos=(50, 160))
		self.bCheckSize.SetFont(fontButton)
		self.Bind(wx.EVT_BUTTON, self.onBCheckSize, self.bCheckSize)

		self.bPlay = wx.Button(self, wx.ID_ANY, "Play", size=(120, 120), pos=(50, 300))
		self.bPlay.SetFont(fontButton)
		self.Bind(wx.EVT_BUTTON, self.onBPlay, self.bPlay)

		self.bPause = wx.Button(self, wx.ID_ANY, "Pause", size=(120, 120), pos=(200, 300))
		self.bPause.SetFont(fontButton)
		self.Bind(wx.EVT_BUTTON, self.onBPause, self.bPause)

		self.enableBasedOnFile()

	def enableBasedOnFile(self):
		self.bCheckSize.Enable(self.currentFile is not None)
		self.bPlay.Enable(self.currentFile is not None)
		self.bPause.Enable(self.currentFile is not None)

	def onBFiles(self, evt):
		dlg = FilesDlg(self, self.settings.datadir)
		rc = dlg.ShowModal()

		if rc == wx.ID_OK:
			flist, action = dlg.getResults()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		if action == ACTION_LOAD:
			self.currentFile = flist[0]
			self.displayCurrentFileName()
			self.fullFileName = os.path.join(self.settings.datadir, flist[0])
			print(self.fullFileName)
		elif action == ACTION_DELETE:
			for f in flist:
				if f == self.currentFile:
					self.currentFile = None
					self.displayCurrentFileName()

				fqn = os.path.join(self.settings.datadir, f)
				os.unlink(fqn)

	def onBCheckSize(self, evt):
		print("check size")

	def onBPlay(self, evt):
		print("play")

	def onBPause(self, evt):
		print("pause")

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

		self.currentFile = None
		self.displayCurrentFileName()

	def displayCurrentFileName(self):
		if self.currentFile is None:
			txt = "<none>"
		else:
			txt = self.currentFile

		w,h = self.dc.GetTextExtent(txt)
		self.stFileName.SetLabel(txt)
		self.stFileName.SetSize((w, h))

class FilesDlg(wx.Dialog):
	def __init__(self, parent, datadir):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Monospace")

		self.parent = parent
		self.datadir = datadir
		self.loadFileNames()

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(10)

		self.lbFiles = wx.CheckListBox(self, wx.ID_ANY, size=(400, 220), choices=self.flist)
		self.lbFiles.SetFont(font)
		self.Bind(wx.EVT_LISTBOX, self.onLbFilesList, self.lbFiles)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onLbFiles, self.lbFiles)
		self.lbFiles.SetSelection(wx.NOT_FOUND)
		vsz.Add(self.lbFiles, 0, wx.LEFT + wx.RIGHT, 20)

		vsz.AddSpacer(10)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(20)

		self.bLoad = wx.Button(self, wx.ID_ANY, "Load", size=(60, 60))
		self.bLoad.Enable(False)
		bsz.Add(self.bLoad)
		self.Bind(wx.EVT_BUTTON, self.onBLoad, self.bLoad)

		bsz.AddSpacer(10)

		self.bDelete = wx.Button(self, wx.ID_ANY, "Delete", size=(60, 60))
		self.bDelete.Enable(False)
		bsz.Add(self.bDelete)
		self.Bind(wx.EVT_BUTTON, self.onBDelete, self.bDelete)

		bsz.AddSpacer(10)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=(60, 60))
		bsz.Add(self.bRefresh)
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)

		bsz.AddSpacer(10)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(60, 60))
		bsz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.onBCancel, self.bCancel)

		bsz.AddSpacer(20)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(vsz)
		hsz.AddSpacer(10)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def loadFileNames(self):
		self.flist = []
		for ext in [ "nc", "gcode" ]:
			fspec = os.path.join(self.datadir, "*.%s" % ext)
			self.flist.extend([os.path.basename(f) for f in glob.glob(fspec)])

	def onBRefresh(self, _):
		self.loadFileNames()
		self.lbFiles.SetItems(self.flist)
		self.lbFiles.Refresh()

	def onLbFilesList(self, evt):
		self.lbFiles.SetSelection(wx.NOT_FOUND)

	def onLbFiles(self, evt):
		ci = self.lbFiles.GetCheckedItems()
		self.lbFiles.SetSelection(wx.NOT_FOUND)
		self.bDelete.Enable(len(ci) > 0)
		self.bLoad.Enable(len(ci) == 1)

	def onBLoad(self, _):
		self.action = ACTION_LOAD
		self.EndModal(wx.ID_OK)

	def onBDelete(self, _):
		self.action = ACTION_DELETE
		self.EndModal(wx.ID_OK)
		
	def onBCancel(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)

	def getResults(self):
		fnames = [self.flist[x] for x in self.lbFiles.GetCheckedItems()]
		return fnames, self.action
