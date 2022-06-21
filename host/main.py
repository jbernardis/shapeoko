import wx
import os

from images import Images
from filelist import FileList
from shapeokofileslistctrl import ShapeokoFilesListCtrl

import pprint

BUTTONSIZE = (48, 48)

class MainFrame(wx.Frame):
	def __init__(self):		
		wx.Frame.__init__(self, None)
		self.SetTitle("Shapeoko File Manager")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour(wx.Colour(196, 196, 196))
		self.SetClientSize((800, 480))

		self.images = Images("images")

		self.flc = ShapeokoFilesListCtrl(self, self.images)
		self.flc.SetPosition((50, 50))

		self.bRefresh = wx.BitmapButton(self, wx.ID_ANY, self.images.pngRefresh, size=(BUTTONSIZE))
		self.bRefresh.SetPosition((50, 400))
		self.Bind(wx.EVT_BUTTON, self.onBRefresh, self.bRefresh)

		self.bCheckAll = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCheckall, size=(BUTTONSIZE))
		self.bCheckAll.SetPosition((120, 400))
		self.Bind(wx.EVT_BUTTON, self.onBCheckAll, self.bCheckAll)

		self.bCheckOne = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCheckone, size=(BUTTONSIZE))
		self.bCheckOne.SetPosition((190, 400))
		self.Bind(wx.EVT_BUTTON, self.onBCheckOne, self.bCheckOne)

		self.bCheckNone = wx.BitmapButton(self, wx.ID_ANY, self.images.pngChecknone, size=(BUTTONSIZE))
		self.bCheckNone.SetPosition((260, 400))
		self.Bind(wx.EVT_BUTTON, self.onBCheckNone, self.bCheckNone)



		self.bUpload = wx.BitmapButton(self, wx.ID_ANY, self.images.pngUpload, size=(BUTTONSIZE))
		self.bUpload.SetPosition((400, 400))
		self.Bind(wx.EVT_BUTTON, self.onBUpload, self.bUpload)

		self.bDelete = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDelete, size=(BUTTONSIZE))
		self.bDelete.SetPosition((470, 400))
		self.bDelete.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.onBDelete, self.bDelete)

		self.initialized = False

		wx.CallAfter(self.initialize)

	def initialize(self):
		self.fileList = FileList(self, "shapeoko.local", "jeff", "5braxton")
		self.flc.setFl(self.fileList)
		self.flc.SetPosition((50, 50))
		self.initialized = True

	def onBRefresh(self, _):
		self.fileList.refresh()
		self.flc.refreshAll()

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