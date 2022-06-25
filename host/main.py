import wx
import os

from images import Images
from settings import Settings
from filelist import FileList
from shapeokofileslistctrl import ShapeokoFilesListCtrl

BUTTONSIZE = (48, 48)

class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None)
		self.SetTitle("Shapeoko File Manager")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))
		self.SetClientSize((800, 480))

		self.settings = Settings()
		self.images = Images("images")

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.flc = ShapeokoFilesListCtrl(self, self.images)
		hsz.Add(self.flc)

		hsz.AddSpacer(20)
		vsz.Add(hsz)

		vsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, self.images.pngRefresh, size=(BUTTONSIZE))
		self.bRefresh.SetToolTip("Refresh File List")
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)
		btnsz.Add(self.bRefresh)

		btnsz.AddSpacer(50)

		self.bCheckAll = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCheckall, size=(BUTTONSIZE))
		self.bCheckAll.SetToolTip("Check All Files")
		self.bCheckAll.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBCheckAll, self.bCheckAll)
		btnsz.Add(self.bCheckAll)

		btnsz.AddSpacer(10)

		self.bCheckOne = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCheckone, size=(BUTTONSIZE))
		self.bCheckOne.SetToolTip("Check/Uncheck selected file")
		self.bCheckOne.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBCheckOne, self.bCheckOne)
		btnsz.Add(self.bCheckOne)

		btnsz.AddSpacer(10)

		self.bCheckNone = wx.BitmapButton(self, wx.ID_ANY, self.images.pngChecknone, size=(BUTTONSIZE))
		self.bCheckNone.SetToolTip("Uncheck All Files")
		self.bCheckNone.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBCheckNone, self.bCheckNone)
		btnsz.Add(self.bCheckNone)

		btnsz.AddSpacer(50)

		self.bUpload = wx.BitmapButton(self, wx.ID_ANY, self.images.pngUpload, size=(BUTTONSIZE))
		self.bUpload.SetPosition((400, 400))
		self.bUpload.SetToolTip("Upload file(s) to shapeoko")
		self.Bind(wx.EVT_BUTTON, self.onBUpload, self.bUpload)
		btnsz.Add(self.bUpload)

		btnsz.AddSpacer(10)

		self.bDelete = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDelete, size=(BUTTONSIZE))
		self.bDelete.SetPosition((470, 400))
		self.bDelete.SetToolTip("Delete checked file(s)")
		self.bDelete.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBDelete, self.bDelete)
		btnsz.Add(self.bDelete)

		vsz.Add(btnsz, 1, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
	

		self.initialized = False

		wx.CallAfter(self.initialize)

	def initialize(self):
		try:
			self.fileList = FileList(self, self.settings.ipaddr, self.settings.user, self.settings.derivedPassword)
		except Exception as e:
			self.connectionError()
			return

		self.flc.setFl(self.fileList)
		self.initialized = True

	def onBRefresh(self, _):
		try:
			self.fileList.refresh()
		except Exception as e:
			self.connectionError()
			return

		self.flc.refreshAll()

	def connectionError(self):
		dlg = wx.MessageDialog(self, "Unable to connect to %s\nPress OK to exit program." % self.settings.ipaddr, "Failed Connection",
			style = wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		self.doClose()

	def onBCheckAll(self, _):
		self.flc.checkAll()

	def onBCheckOne(self, _):
		self.flc.checkOne()

	def onBCheckNone(self, _):
		self.flc.checkNone()

	def selectionChange(self, sel):
		self.selectedFiles = []
		for fx in range(self.fileList.count()):
			if sel[fx]:
				self.selectedFiles.append(self.fileList.getFileName(fx))
		self.bDelete.Enable(len(self.selectedFiles) + 0)

		flag = self.fileList.count() > 0
		self.bCheckAll.Enable(flag)
		self.bCheckOne.Enable(flag)
		self.bCheckNone.Enable(flag)


	def onBUpload(self, _):
		wildcard = "G Code (*.gcode,*.nc)|*.gcode;*.nc|"  \
			"G Code (*.gcode)|*.gcode|" \
			"G Code (*.nc)|*.nc|" \
 			"All files (*.*)|*.*"

		dlg = wx.FileDialog(
            self, message="Choose file(s) to upload",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:	
			paths = dlg.GetPaths()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.fileList.uploadFiles(paths)
		self.flc.refreshAll()

	def onBDelete(self, _):
		self.fileList.deleteFiles(self.selectedFiles)
		self.flc.refreshAll()

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