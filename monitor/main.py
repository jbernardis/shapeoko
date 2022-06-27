#!/usr/bin/env python3

import wx
import os

from controller import Controller
from images import Images
from settings import Settings
from viewcanvas import ViewCanvas
from cnc import CNC
from filelist import FileList

BUTTONSIZE = (64, 64)

TYPE_ACTIVEJOB = 1
TYPE_SHAPEOKOFILE = 2
TYPE_LOCALFILE = 3

class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None)
		self.SetTitle("Shapeoko File Manager")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))
		self.SetClientSize((800, 480))

		self.settings = Settings()
		self.images = Images("images")

		self.showGrid = True
		self.showZGrid = False
		self.fileName = None
		self.position = 0
		self.fileLines = 0
		self.fileType = None
		self.controller = None
		self.following = False
		self.status = ""

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "File:", size=(100, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(font)
		hsz.AddSpacer(30)
		hsz.Add(st)
		hsz.AddSpacer(10)
		self.stFileInfo = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.stFileInfo.SetFont(font)
		hsz.Add(self.stFileInfo)

		vsz.Add(hsz)
		vsz.AddSpacer(5)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Status:", size=(100, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(font)
		hsz.AddSpacer(30)
		hsz.Add(st)
		hsz.AddSpacer(10)
		self.stStatus = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.stStatus.SetFont(font)
		hsz.Add(self.stStatus)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.gl = ViewCanvas(self, buildarea=(200, 200))
		hsz.Add(self.gl)

		hsz.AddSpacer(20)
		vsz.Add(hsz)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.cbShowGrid = wx.CheckBox(self, wx.ID_ANY, "Draw Axes")
		self.cbShowGrid.SetValue(self.showGrid)
		self.gl.setDrawGrid(self.showGrid)
		self.Bind(wx.EVT_CHECKBOX, self.onShowGrid, self.cbShowGrid)		
		hsz.Add(self.cbShowGrid)

		hsz.AddSpacer(20)

		self.cbShowZGrid = wx.CheckBox(self, wx.ID_ANY, "Draw Z Axis")
		self.cbShowZGrid.SetValue(self.showZGrid)
		self.gl.setDrawZGrid(self.showZGrid)
		self.Bind(wx.EVT_CHECKBOX, self.onShowZGrid, self.cbShowZGrid)		
		hsz.Add(self.cbShowZGrid)
		self.cbShowZGrid.Enable(self.showGrid)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bRetrieveJob = wx.BitmapButton(self, wx.ID_ANY, self.images.pngJob, size=(BUTTONSIZE))
		self.Bind(wx.EVT_BUTTON, self.onBRetrieveJob, self.bRetrieveJob)
		self.bRetrieveJob.SetToolTip("Retrieve current job from the shapeoko")
		btnsz.Add(self.bRetrieveJob)

		btnsz.AddSpacer(20)

		self.bFollow = wx.BitmapButton(self, wx.ID_ANY, self.images.pngFollow, size=(BUTTONSIZE))
		self.Bind(wx.EVT_BUTTON, self.onBFollow, self.bFollow)
		self.bFollow.SetToolTip("Follow/Unfollow the current job as it runs")
		btnsz.Add(self.bFollow)

		btnsz.AddSpacer(50)

		self.bLocalFile = wx.BitmapButton(self, wx.ID_ANY, self.images.pngLocalfile, size=(BUTTONSIZE))
		self.Bind(wx.EVT_BUTTON, self.onBLocalFile, self.bLocalFile)
		self.bLocalFile.SetToolTip("Load a local file for viewing only")
		btnsz.Add(self.bLocalFile)

		btnsz.AddSpacer(20)

		self.bShapeokoFile = wx.BitmapButton(self, wx.ID_ANY, self.images.pngShapeokofile, size=(BUTTONSIZE))
		self.Bind(wx.EVT_BUTTON, self.onBShapeokoFile, self.bShapeokoFile)
		self.bShapeokoFile.SetToolTip("Select and download a shapeoko file for viewing only")
		btnsz.Add(self.bShapeokoFile)

		vsz.Add(btnsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
	
		self.initialized = False

		self.timer = wx.Timer(self)

		wx.CallAfter(self.initialize)

	def initialize(self):
		self.gl.setDrawGrid(self.showGrid)
		self.gl.setDrawZGrid(self.showZGrid)

		self.controller = Controller(self.settings.ipaddr, self.settings.port, self.settings.user, self.settings.password)
		self.position = 0
		
		self.Bind(wx.EVT_TIMER, self.ticker)

		self.enableButtons()

		self.initialized = True

	def ticker(self, _):
		if self.following:
			try:
				rc, json = self.controller.getJobInfo()
			except Exception as e:
				self.msgDlg("Unable to retrieve Job information: %s" % str(e), "Exception")
				return

			if rc >= 400:
				self.msgDlg("HTTP Error retrieving job information: %d" % rc, "HTTP Error")
				return

			if self.position != json["position"]:
				self.position = json["position"]
				self.gl.setPosition(self.position)
				self.showStatus()

	def onShowGrid(self, _):
		self.showGrid = self.cbShowGrid.GetValue()
		self.gl.setDrawGrid(self.showGrid)
		self.cbShowZGrid.Enable(self.showGrid)
		
	def onShowZGrid(self, _):
		self.showZGrid = self.cbShowZGrid.GetValue()
		self.gl.setDrawZGrid(self.showZGrid)

	def onBRetrieveJob(self, _):
		self.fileType = None
		self.fileName = None
		self.position = 0
		try:
			rc, json = self.controller.getJobInfo()
		except Exception as e:
			self.msgDlg("Unable to retrieve Job information: %s" % str(e), "Exception")
			self.showStatus()
			return

		if rc >= 400:
			self.msgDlg("HTTP Error retrieving job information: %d" % rc, "HTTP Error")
			self.showStatus()
			return

		self.fileName = json["file"]
		if self.fileName == "":
			self.fileName = None
			self.gc = None
			self.msgDlg("No file has been selected on shapeoko", "No file selected")
			self.showStatus()
			return
		else:
			try:
				gc = self.controller.getRemoteFile(self.fileName)
			except Exception as e:
				self.msgDlg("Exception trying to retrieve G Code for file %s: %s" % (self.fileName, str(e)))
				self.fileName = None
				self.showStatus()
				return

		if gc is None:
			self.fileName = None
			dlg = self.msgDlg("Selected file does not exist on shapeoko", "File doesn't exist")
			self.showStatus()
			return

		self.fileType = TYPE_ACTIVEJOB
		self.fileLines = json["lines"]
		self.loadGCode(gc)
		self.enableButtons()
		self.showFileInformation()
		self.showStatus()

	def showFileInformation(self):
		if self.fileType == TYPE_ACTIVEJOB:
			ft = " (Current Job)"
		elif self.fileType == TYPE_LOCALFILE:
			ft = " (Local File)"
		elif self.fileType == TYPE_SHAPEOKOFILE:
			ft = " (Shapeoko File)"
		else:
			ft = ""

		if self.fileName is None:
			self.stFileInfo.SetLabel("")
		else:
			self.stFileInfo.SetLabel("%s%s" % (self.fileName, ft))

	def showStatus(self):
		if self.fileName is None:
			self.stStatus.SetLabel("")
		elif self.following:
			self.stStatus.SetLabel("Following (line %d/%d)" % (self.position, self.fileLines))
		elif self.fileType == TYPE_ACTIVEJOB:
			self.stStatus.SetLabel("Idle")
		else:
			self.stStatus.SetLabel("")

	def loadGCode(self, gcode):			
		self.gcode = gcode
		cnc = CNC()
				
		ln = 1
		for gl in self.gcode:
			cnc.execute(gl, ln)
			ln += 1
			
		self.gl.setPoints(cnc.getPoints())

	def onBLocalFile(self, _):
		wildcard = "G Code (*.gcode,*.nc)|*.gcode;*.nc|"  \
			"G Code (*.gcode)|*.gcode|" \
			"G Code (*.nc)|*.nc|" \
 			"All files (*.*)|*.*"

		dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.settings.localgcdir,
            defaultFile="",
            wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

		rc = dlg.ShowModal()
		if rc  == wx.ID_OK:
			path = dlg.GetPath()

		dlg.Destroy()

		if rc != wx.ID_OK:
			return

		try:
			with open(path, "r") as gcfp:
				gc = [ln.rstrip() for ln in gcfp.readlines()]
		except Exception as e:
			self.msgDlg("Exception %s trying to open/read file" % str(e), "Exception")
			return

		dn, bn = os.path.split(path)
		if dn != self.settings.localgcdir:
			self.settings.localgcdir = dn
			self.settings.save()

		self.fileType = TYPE_LOCALFILE
		self.fileLines = len(gc)
		self.fileName = bn
		self.loadGCode(gc)
		self.enableButtons()
		self.showFileInformation()
		self.showStatus()

	def onBShapeokoFile(self, _):
		fl = FileList(self.settings.ipaddr, self.settings.user, self.settings.password)
		files = [fn for fn in fl]

		dlg = wx.SingleChoiceDialog(
                self, "Choose a File:", "Shapeoko Files", files, wx.CHOICEDLG_STYLE)

		rc = dlg.ShowModal()
		if rc  == wx.ID_OK:
			fn = dlg.GetStringSelection()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		try:
			gc = self.controller.getRemoteFile(fn)
		except Exception as e:
			self.msgDlg("Exception trying to retrieve G Code for file %s: %s" % (fn, str(e)))
			self.fileName = None
			self.showStatus()
			return

		if gc is None:
			self.fileName = None
			dlg = self.msgDlg("Selected file does not exist on shapeoko", "File doesn't exist")
			self.showStatus()
			return

		self.fileName = fn
		self.fileType = TYPE_SHAPEOKOFILE
		self.fileLines = len(gc)
		self.loadGCode(gc)
		self.enableButtons()
		self.showFileInformation()
		self.showStatus()

	def onBFollow(self, _):
		if self.following:
			self.timer.Stop()
			self.following = False
			self.position = 0
			self.gl.setPosition(self.position)
			self.enableButtons()
		else:
			self.timer.Start(1000)
			self.following = True
			self.enableButtons()

		self.showStatus()

	def enableButtons(self):
		self.bRetrieveJob.Enable(not self.following)
		self.bLocalFile.Enable(not self.following)
		self.bShapeokoFile.Enable(not self.following)
		self.bFollow.Enable(self.fileType == TYPE_ACTIVEJOB)

	def msgDlg(self, msg, captian, style = wx.OK | wx.ICON_ERROR):
		dlg = wx.MessageDialog(self, msg, captian, style = style)
		dlg.ShowModal()
		dlg.Destroy()

	def onClose(self, _):
		self.doClose()

	def doClose(self):
		self.Destroy()

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True

app = App(False)
app.MainLoop()
