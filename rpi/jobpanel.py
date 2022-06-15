import wx
from wx.lib import newevent

import glob
import os
import time
import queue
from gparser import Scanner

(StatusEvent, EVT_NEWSTATUS) = newevent.NewEvent()  

ACTION_LOAD = 0
ACTION_DELETE = 1

class JobPanel(wx.Panel):
	def __init__(self, parent, win, images):		
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))

		self.parentFrame = win
		self.images = images

		self.Bind(wx.EVT_SIZE, self.OnPanelSize)

		fontText = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.dc = wx.ScreenDC()
		self.dc.SetFont(fontText)

		self.currentFile = None
		self.fullFileName = None

		self.playing = False
		self.paused = False
		self.status = ""
		self.filePosition = 0

		self.bFiles = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBfiles, size=(120, 120), pos=(50, 20))
		self.Bind(wx.EVT_BUTTON, self.onBFiles, self.bFiles)

		self.stMachineState = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 20))
		self.stMachineState.SetFont(fontText)
		self.stFileName = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 80))
		self.stFileName.SetFont(fontText)
		self.stFileSize = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 120))
		self.stFileSize.SetFont(fontText)
		self.stFileLines = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 160))
		self.stFileLines.SetFont(fontText)
		self.stFileDate = wx.StaticText(self, wx.ID_ANY, "", pos=(300, 200))
		self.stFileDate.SetFont(fontText)

		self.bCheckSize = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBchecksize, size=(120, 120), pos=(50, 160))
		self.Bind(wx.EVT_BUTTON, self.onBCheckSize, self.bCheckSize)

		self.bPlay = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBplay, size=(120, 120), pos=(50, 300))
		self.Bind(wx.EVT_BUTTON, self.onBPlay, self.bPlay)

		self.bPause = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBpause, size=(120, 120), pos=(200, 300))
		self.Bind(wx.EVT_BUTTON, self.onBPause, self.bPause)

		self.bReset = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBreset, size=(120, 120), pos=(350, 300))
		self.Bind(wx.EVT_BUTTON, self.onBReset, self.bReset)

		self.enableBasedOnFile()

	def initialize(self, shapeoko, settings):
		self.shapeoko = shapeoko
		self.settings = settings

		self.currentFile = None
		self.displayCurrentFileInfo()

		self.parentFrame.registerTicker(self.ticker)
		self.shapeoko.registerNewStatus(self.statusUpdate)
		self.Bind(EVT_NEWSTATUS, self.setStatusEvent)

	def statusUpdate(self, newStatus): # Thread context
		evt = StatusEvent(status=newStatus)
		wx.PostEvent(self, evt)

	def setStatusEvent(self, evt):
		self.status = evt.status
		w,h = self.dc.GetTextExtent(self.status)
		self.stMachineState.SetSize((w, h))
		self.stMachineState.SetLabel(self.status)

		if self.status.lower() == "idle" and self.playing:
			self.finishRun()

	def ticker(self):
		if self.playing:
			np = self.shapeoko.getPosition()
			if np != self.filePosition:
				self.filePosition = np
				txt = "%d / %d lines" % (np, self.fileLines)
				w,h = self.dc.GetTextExtent(txt)
				self.stFileLines.SetLabel(txt)
				self.stFileLines.SetSize((w, h))

	def enableBasedOnFile(self):
		self.bCheckSize.Enable(self.currentFile is not None and not self.playing and self.status.lower() == "idle")
		self.bPlay.Enable(self.currentFile is not None and not self.playing and self.status.lower() == "idle")
		self.bPause.Enable(self.currentFile is not None and self.playing)
		self.bReset.Enable(self.currentFile is not None and self.playing)

	def onBFiles(self, evt):
		dlg = FilesDlg(self, self.settings.datadir)
		dlg.Center()
		rc = dlg.ShowModal()

		if rc == wx.ID_OK:
			flist, action = dlg.getResults()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		if action == ACTION_LOAD:
			self.currentFile = flist[0]
			self.fullFileName = os.path.join(self.settings.datadir, self.currentFile)
			with open(self.fullFileName, 'r') as fp:
				for count, line in enumerate(fp):
					pass
			self.fileLines = count + 1
			self.displayCurrentFileInfo()
		
		elif action == ACTION_DELETE:
			for f in flist:
				if f == self.currentFile:
					self.currentFile = None
					self.fullFileName = None
					self.displayCurrentFileInfo()

				fqn = os.path.join(self.settings.datadir, f)
				os.unlink(fqn)

		self.enableBasedOnFile()

	def onBCheckSize(self, evt):
		scanq = queue.Queue()
		sc = Scanner(scanq, self.fullFileName)

		data = scanq.get()
		minx = 1000
		miny = 1000
		maxx = -1000
		maxy = -1000
		while data is not None:
			if data[0] in ["X", "x"]:
				x = float(data[1:])
				if x < minx:
					minx = x
				if x > maxx:
					maxx = x
			elif data[0] in ["Y", "y"]:
				y = float(data[1:])
				if y < miny:
					miny = y
				if y > maxy:
					maxy = y

			data = scanq.get()

		lines = []
		for x, y in [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]:
			lines.append("G0X%.3fY%.3f" % (x, y))

		self.shapeoko.sendGcodeLines(lines)

	def onBPlay(self, evt):
		self.playing = True
		self.filePosition = 0
		self.enableBasedOnFile()
		self.shapeoko.sendGCodeFile(self.fullFileName)

	def finishRun(self):
		self.paused = False
		self.playing = False
		self.filePosition = 0
		self.enableBasedOnFile()

		txt = "%d lines" % self.fileLines
		w,h = self.dc.GetTextExtent(txt)
		self.stFileLines.SetLabel(txt)
		self.stFileLines.SetSize((w, h))

	def onBPause(self, evt):
		if self.paused:
			self.shapeoko.resume()
			self.paused = False
		else:
			self.shapeoko.holdFeed()
			self.paused = True

	def onBReset(self, evt):
		self.shapeoko.softReset()
		self.finishRun()

	def OnPanelSize(self, evt):
		self.SetPosition((0,0))
		self.SetSize(evt.GetSize())

	def displayCurrentFileInfo(self):
		txt = "<no file chosen>" if self.currentFile is None else self.currentFile
		w,h = self.dc.GetTextExtent(txt)
		self.stFileName.SetLabel(txt)
		self.stFileName.SetSize((w, h))

		if self.currentFile is not None:
			fi = os.stat(self.fullFileName)

		txt = " " if self.currentFile is None else "%d bytes" % fi.st_size
		w,h = self.dc.GetTextExtent(txt)
		self.stFileSize.SetLabel(txt)
		self.stFileSize.SetSize((w, h))

		txt = " " if self.currentFile is None else "%d lines" % self.fileLines
		w,h = self.dc.GetTextExtent(txt)
		self.stFileLines.SetLabel(txt)
		self.stFileLines.SetSize((w, h))

		txt = " " if self.currentFile is None else time.strftime("%d %b %Y %H:%M:%S", time.localtime(fi.st_mtime))
		w,h = self.dc.GetTextExtent(txt)
		self.stFileDate.SetLabel(txt)
		self.stFileDate.SetSize((w, h))

class FilesDlg(wx.Dialog):
	def __init__(self, parent, datadir):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "", size=(500, 440), style=wx.CENTER | wx.CAPTION)
		self.Bind(wx.EVT_CLOSE, self.onClose)

		font = wx.Font(28, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

		self.action = None
		self.parent = parent
		self.datadir = datadir
		images = self.parent.images
		self.loadFileNames()

		self.lbFiles = wx.CheckListBox(self, wx.ID_ANY, size=(400, 220), pos=(50, 30), choices=self.flist)
		self.lbFiles.SetFont(font)
		self.Bind(wx.EVT_LISTBOX, self.onLbFilesClick, self.lbFiles)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.onLbFilesDClick, self.lbFiles)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onLbFiles, self.lbFiles)
		self.lbFiles.SetSelection(wx.NOT_FOUND)

		self.bLoad = wx.BitmapButton(self, wx.ID_ANY, images.pngBload, size=(100, 60), pos=(20, 270))
		self.bLoad.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBLoad, self.bLoad)

		self.bDelete = wx.BitmapButton(self, wx.ID_ANY, images.pngBdelete, size=(100, 60), pos=(130, 270))
		self.bDelete.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBDelete, self.bDelete)

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, images.pngBrefresh, size=(100, 60), pos=(240, 270))
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)

		self.bCancel = wx.BitmapButton(self, wx.ID_ANY, images.pngBcancel, size=(100, 60), pos=(350, 270))
		self.Bind(wx.EVT_BUTTON, self.onBCancel, self.bCancel)

	def loadFileNames(self):
		fl = []
		for ext in [ "nc", "gcode" ]:
			fspec = os.path.join(self.datadir, "*.%s" % ext)
			fl.extend([os.path.basename(f) for f in glob.glob(fspec)])

		self.flist = ["  %s" % f for f in sorted(fl)]

	def onBRefresh(self, _):
		self.loadFileNames()
		self.lbFiles.SetItems(self.flist)
		self.lbFiles.Refresh()

	def onLbFilesDClick(self, evt):
		ix = evt.GetSelection()
		if ix == wx.NOT_FOUND:
			return

		self.lbFiles.Check(ix, not self.lbFiles.IsChecked(ix))
		self.lbFiles.SetSelection(wx.NOT_FOUND)
		self.countCheckedItems()

	def onLbFilesClick(self, evt):
		evt.Skip()

	def onLbFiles(self, evt):
		self.lbFiles.SetSelection(wx.NOT_FOUND)
		self.countCheckedItems()

	def countCheckedItems(self):
		ci = self.lbFiles.GetCheckedItems()
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
		if self.action is None:
			fnames = []
		else:
			fnames = [self.flist[x].strip() for x in self.lbFiles.GetCheckedItems()]
		return fnames, self.action
