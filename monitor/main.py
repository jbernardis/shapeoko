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
		self.titleString = "Shapeoko Monitor:  "
		self.SetTitle(self.titleString)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))
		self.SetClientSize((800, 480))

		self.settings = Settings()
		self.images = Images("images")

		self.showAxes = True
		self.showZAxis = False
		self.showTool = False
		self.showGrid = True
		self.fileName = None
		self.position = 0
		self.fileLines = 0
		self.fileType = None
		self.controller = None
		self.following = False
		self.status = ""
			
		self.fileInfo = ""
		self.followStatus = ""

		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 

		vsz = wx.BoxSizer(wx.HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.VERTICAL)
		hsz.AddSpacer(20)

		self.gl = ViewCanvas(self, buildarea=(200, 200))
		hsz.Add(self.gl)

		hsz.AddSpacer(20)
		vsz.Add(hsz)
		vsz.AddSpacer(20)

		vsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.VERTICAL)

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

		btnsz.AddSpacer(50)

		self.cbshowAxes = wx.CheckBox(self, wx.ID_ANY, "Draw Axes")
		self.cbshowAxes.SetValue(self.showAxes)
		self.gl.setDrawAxes(self.showAxes)
		self.Bind(wx.EVT_CHECKBOX, self.onshowAxes, self.cbshowAxes)		
		btnsz.Add(self.cbshowAxes)

		btnsz.AddSpacer(20)

		self.cbshowZAxis = wx.CheckBox(self, wx.ID_ANY, "Draw Z Axis")
		self.cbshowZAxis.SetValue(self.showZAxis)
		self.gl.setDrawZAxis(self.showZAxis)
		self.Bind(wx.EVT_CHECKBOX, self.onshowZAxis, self.cbshowZAxis)		
		btnsz.Add(self.cbshowZAxis)
		self.cbshowZAxis.Enable(self.showAxes)

		btnsz.AddSpacer(20)

		self.cbshowGrid = wx.CheckBox(self, wx.ID_ANY, "Draw Grid")
		self.cbshowGrid.SetValue(self.showGrid)
		self.gl.setDrawGrid(self.showGrid)
		self.Bind(wx.EVT_CHECKBOX, self.onshowGrid, self.cbshowGrid)		
		btnsz.Add(self.cbshowGrid)

		btnsz.AddSpacer(20)

		self.cbShowTool = wx.CheckBox(self, wx.ID_ANY, "Draw Tool")
		self.cbShowTool.SetValue(self.showTool)
		self.gl.setDrawTool(self.showTool)
		self.Bind(wx.EVT_CHECKBOX, self.onShowTool, self.cbShowTool)		
		btnsz.Add(self.cbShowTool)
		self.cbShowTool.Enable(self.following)

		vsz.Add(btnsz, 0, wx.ALIGN_CENTER_VERTICAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
	
		self.initialized = False

		self.timer = wx.Timer(self)

		wx.CallAfter(self.initialize)

	def initialize(self):
		self.gl.setDrawAxes(self.showAxes)
		self.gl.setDrawZAxis(self.showZAxis)
		self.gl.setDrawTool(self.showTool)
		self.gl.setDrawGrid(self.showGrid)

		self.controller = Controller(self.settings.ipaddr, self.settings.port, self.settings.user, self.settings.password)
		self.position = 0
		self.tx = 0
		self.ty = 0
		self.tz = 0
		
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

			nx = json["mpos"][0] - json["wco"][0]
			ny = json["mpos"][1] - json["wco"][1]
			nz = json["mpos"][2] - json["wco"][2]

			if self.position != json["position"] or nx != self.tx or ny != self.ty or nz != self.tz:
				self.position = json["position"]
				self.tx = nx
				self.ty = ny
				self.tz = nz
				self.gl.setPosition(self.position, nx, ny, nz)
				self.showStatus()

	def onshowAxes(self, _):
		self.showAxes = self.cbshowAxes.GetValue()
		self.gl.setDrawAxes(self.showAxes)
		self.cbshowZAxis.Enable(self.showAxes)
		
	def onshowZAxis(self, _):
		self.showZAxis = self.cbshowZAxis.GetValue()
		self.gl.setDrawZAxis(self.showZAxis)
		
	def onshowGrid(self, _):
		self.showGrid = self.cbshowGrid.GetValue()
		self.gl.setDrawGrid(self.showGrid)
		
	def onShowTool(self, _):
		self.showTool = self.cbShowTool.GetValue()
		self.gl.setDrawTool(self.showTool)

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
			self.fileInfo = ""
		else:
			self.fileInfo = "%s%s" % (self.fileName, ft)
		self.updateTitle()

	def showStatus(self):
		if self.fileName is None:
			self.followStatus = ""
		elif self.following:
			pct = (self.position/self.fileLines)*100.0
			self.followStatus = "Following (line %d/%d - %5.1f%%)" % (self.position, self.fileLines, pct)
		elif self.fileType == TYPE_ACTIVEJOB:
			self.followStatus = "Not Following"
		else:
			self.followStatus = ""
			#self.stStatus.SetLabel("")
		self.updateTitle()

	def updateTitle(self):
		title = self.titleString

		if self.fileInfo != "":
			title += " %s" % self.fileInfo

			if self.followStatus != "":
				title += " / %s" % self.followStatus

		self.SetTitle(title)

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
			self.showTool = False
			self.position = 0
			self.tx = 0
			self.ty = 0
			self.tz = 0
			self.gl.setDrawTool(self.showTool)
			self.gl.setPosition(self.position, self.tx, self.ty, self.tx)
			
		else:
			self.timer.Start(250)
			self.following = True
			self.showTool = self.cbShowTool.GetValue()
			self.gl.setDrawTool(self.showTool)

		
		self.enableButtons()

		self.showStatus()

	def enableButtons(self):
		self.bRetrieveJob.Enable(not self.following)
		self.bLocalFile.Enable(not self.following)
		self.bShapeokoFile.Enable(not self.following)
		self.bFollow.Enable(self.fileType == TYPE_ACTIVEJOB)
		self.cbShowTool.Enable(self.following)


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
