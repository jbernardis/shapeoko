#!/bin/env python
import wx
try:
	from agw import floatspin as FS
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.floatspin as FS

import os
import inspect
import json

from propertiesgrid import PropertiesGrid
from images import Images

from settings import Settings
from shapeokodlg import ShapeokoDlg
from renderdlg import RenderDlg
from shapeoko import Shapeoko
from material import Material
from presets import Presets

from rectangle import Rectangle
from circle import Circle
from arc import Arc
from path import Path
from polygon import Polygon
from lineardrill import LinearDrill
from circulardrill import CircularDrill
from rectangulardrill import RectangularDrill
from carvegrid import CarveGrid
from carvediamond import CarveDiamond

cmdFolder = os.path.realpath(
	os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
BTNDIM = (64, 64) if os.name == 'posix' else (48,48)
SPDIM = (120, -1) if os.name == 'posix' else (60, -1)
SBMARGIN = 10 if os.name == 'posix' else 5

DEFAULT_TITLE = "Shapeoko"

MENU_FILE_NEW = 101
MENU_FILE_OPEN = 102
MENU_FILE_SAVE = 103
MENU_FILE_SAVEAS = 104
MENU_FILE_SAVEEACH = 105
MENU_FILE_RENDER = 106
MENU_FILE_EXIT = 199

MENU_ADD_BASE = 200
MENU_PRESETCAT_BASE = 500
MENU_PRESET_BASE = 600

MENU_SHAPEOKO_PROPERTIES = 400

class MyFrame(wx.Frame): 

	def __init__(self):
		wx.Frame.__init__(self, None, -1, DEFAULT_TITLE)
		
		self.settings = Settings(cmdFolder)

		self.materialSize = ""

		self.CreateStatusBar()
		self.SetStatusText("")

		self.images = Images(os.path.join(cmdFolder, "images"))
		
		ico = wx.Icon(os.path.join(cmdFolder, "images", "shapeoko.png"), wx.BITMAP_TYPE_PNG)
		self.SetIcon(ico)

		self.cnc = None
		self.material = None
		self.toolList = None
		self.pGrid = None
		self.objListBox = None
		self.bScrollUp = self.bScrollDown = None
		self.bMoveUp = self.bMoveDown = None
		self.fsWidth = self.fsHeight = self.fsThick = None
		self.bAdd = self.bDel = self.bRender = self.bNew = self.bLoad = self.bSave = self.bSaveAs = None


		self.setCnc()

		self.objectTypes = {
			"Rectangle": Rectangle,
			"Circle": Circle,
			"Arc": Arc,
			"Path": Path,
			"Polygon": Polygon,
			"Linear Drill": LinearDrill,
			"Circular Drill": CircularDrill,
			"Rectangular Drill": RectangularDrill,
			"Carve Grid": CarveGrid,
			"Carve Diamond": CarveDiamond
		}

		self.rawObjectTypes = {
			"Rectangle": Rectangle,
			"Circle": Circle,
			"Arc": Arc,
			"Path": Path,
			"Polygon": Polygon,
			"LinearDrill": LinearDrill,
			"CircularDrill": CircularDrill,
			"RectangularDrill": RectangularDrill,
			"CarveGrid": CarveGrid,
			"CarveDiamond": CarveDiamond
		}

		self.presets = Presets(cmdFolder)
		self.presetList = self.presets.getPresetList()

		self.fileMenu = None
		self.setMenu()

		self.t = 0
		self.seq = 1
		self.objList = []
		self.modified = False
		self.currentFile = None

		szLeft = self.listAndButtonSizer()

		szRight = self.propertySizer()

		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(szLeft)
		sz.Add(szRight, 1, wx.EXPAND)

		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.SetSizer(sz)
		self.Layout()
		self.Fit()

		self.Show()
		self.msgTimer = 0
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
		self.startTimer()

	def startTimer(self):
		self.timer.Start(1000)

	def stopTimer(self):
		self.timer.Stop()

	def OnTimer(self, _):
		if self.msgTimer > 0:
			self.msgTimer -= 1
			if self.msgTimer <= 0:
				self.SetStatusText("")

	def setMenu(self):
		menuBar = wx.MenuBar()

		# File
		menu1 = wx.Menu()
		menu1.Append(MENU_FILE_NEW, "&New", "Create a new model file")
		menu1.Append(MENU_FILE_OPEN, "&Open", "Open an existing model file")
		menu1.Append(MENU_FILE_SAVE, "&Save", "Save the current model")
		menu1.Append(MENU_FILE_SAVEAS, "Sa&ve as", "Save the current model to a specified file")
		menu1.AppendSeparator()
		menu1.Append(MENU_FILE_SAVEEACH, "Save &each object", "Saves each object to a different specified file")
		menu1.AppendSeparator()
		menu1.Append(MENU_FILE_RENDER, "&Render", "Render the current model and create a G Code file")
		menu1.AppendSeparator()
		menu1.Append(MENU_FILE_EXIT, "E&xit", "Exit the application")
		# Add menu to the menu bar
		menuBar.Append(menu1, "&File")
		self.fileMenu = menu1
		self.fileMenu.Enable(MENU_FILE_SAVE, False)
		self.fileMenu.Enable(MENU_FILE_SAVEAS, False)
		self.fileMenu.Enable(MENU_FILE_SAVEEACH, False)
		self.fileMenu.Enable(MENU_FILE_RENDER, False)

		menu2 = wx.Menu()
		addOffset = 0
		for ot in list(self.objectTypes.keys()):
			menu2.Append(MENU_ADD_BASE + addOffset, ot, "Add an object or type %s" % ot)	
			self.Bind(wx.EVT_MENU, lambda evt, text=ot: self.onMenuAddObject(evt, text), id=MENU_ADD_BASE + addOffset)
			addOffset += 1

		presetOffset = 0			
		presetCatOffset = 0	
		if len(self.presetList) > 0:
			menu2.AppendSeparator()
			presetMenu = wx.Menu()
			for cat in list(self.presetList.keys()):
				catMenu = wx.Menu()
				for lbl in list(self.presetList[cat].keys()):
					catMenu.Append(MENU_PRESET_BASE + presetOffset, lbl, "Add preset for %s: %s" % (cat, lbl))
					self.Bind(wx.EVT_MENU, lambda evt, text=self.presetList[cat][lbl]: self.onMenuAddPreset(evt, text), id=MENU_PRESET_BASE + presetOffset)
					presetOffset += 1

				presetMenu.AppendSubMenu(catMenu, cat)
				presetCatOffset += 1

			menu2.AppendSubMenu(presetMenu, "Preset")

		menuBar.Append(menu2, "&Add")

		menu3 = wx.Menu()
		menu3.Append(MENU_SHAPEOKO_PROPERTIES, "&Properties", "Set shapeoko properties")

		menuBar.Append(menu3, "&Shapeoko")

		self.SetMenuBar(menuBar)

		# Menu events
		self.Bind(wx.EVT_MENU, self.onBNew, id=MENU_FILE_NEW)
		self.Bind(wx.EVT_MENU, self.onBLoad, id=MENU_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.onBSave, id=MENU_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.onBSaveAs, id=MENU_FILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.onSaveEachObject, id=MENU_FILE_SAVEEACH)
		self.Bind(wx.EVT_MENU, self.onBRender, id=MENU_FILE_RENDER)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)

		self.Bind(wx.EVT_MENU, self.onShapeokoProperties, id=MENU_SHAPEOKO_PROPERTIES)

	def setTitle(self):
		t = DEFAULT_TITLE
		if self.currentFile is not None:
			t += " - %s" % self.currentFile

		if self.modified:
			t += " *"

		self.SetTitle(t)

	def setCnc(self):
		self.cnc = Shapeoko()

		self.loadTools()
		self.cnc.setTool(self.toolList[0])

		self.material = Material({})
		self.cnc.setMaterial(self.material)

	def loadTools(self):
		fn = os.path.join(cmdFolder, 'tools.json')
		try:
			with open(fn) as jfp:
				self.toolList = json.load(jfp)
		except (FileNotFoundError, PermissionError):
			print("Unable to open tools json file \"%s\"" % fn)
			self.toolList = []
			return

	def setModified(self, flag=True):
		self.modified = flag
		self.bSave.Enable(flag)
		self.bSaveAs.Enable(len(self.objList) > 0)
		self.fileMenu.Enable(MENU_FILE_SAVE, flag)
		self.fileMenu.Enable(MENU_FILE_SAVEAS, flag)
		self.fileMenu.Enable(MENU_FILE_SAVEEACH, flag)
		self.setTitle()

	def warnIfModified(self):
		if not self.modified:
			return True

		dlg = wx.MessageDialog(self, 'Are you sure you want to continue?',
							   'Discard Changes?',
							   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()

		if rc == wx.ID_NO:
			return False

		return True 

	def message(self, text, duration=10):
		self.SetStatusText(text)
		self.msgTimer = duration

	def propertySizer(self):
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)

		self.pGrid = PropertiesGrid(self, self.images)

		sz.Add(self.pGrid, 1, wx.EXPAND)

		sz.AddSpacer(20)

		szProp = wx.BoxSizer(wx.VERTICAL)
		szProp.AddSpacer(20)
		szProp.Add(sz, 1, wx.EXPAND)
		szProp.AddSpacer(20)

		return szProp

	def listAndButtonSizer(self):
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		sz.Add(wx.StaticText(self, wx.ID_ANY, "Object List:"))

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		self.objListBox = wx.ListBox(self, wx.ID_ANY, size=(200, 200))
		self.Bind(wx.EVT_LISTBOX, self.onLbProp, self.objListBox)
		hsz.Add(self.objListBox, 1, wx.ALIGN_CENTER_HORIZONTAL)

		hsz.AddSpacer(10)

		vsz = wx.BoxSizer(wx.VERTICAL)

		bhsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bScrollUp = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("scrollup"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBScrollUp, self.bScrollUp)
		self.bScrollUp.SetToolTip("Move the selection cursor up 1 line")
		self.bScrollUp.Enable(False)
		bhsz.Add(self.bScrollUp)

		bhsz.AddSpacer(20)

		self.bMoveUp = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("moveup"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBMoveUp, self.bMoveUp)
		self.bMoveUp.SetToolTip("Move the selected object up 1 line")
		self.bMoveUp.Enable(False)
		bhsz.Add(self.bMoveUp)

		vsz.Add(bhsz)
		vsz.AddSpacer(20)

		bhsz = wx.BoxSizer(wx.HORIZONTAL)
		self.bScrollDown = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("scrolldown"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBScrollDown, self.bScrollDown)
		self.bScrollDown.SetToolTip("Move the selection cursor down 1 line")
		self.bScrollDown.Enable(False)
		bhsz.Add(self.bScrollDown)

		bhsz.AddSpacer(20)

		self.bMoveDown = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("movedown"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBMoveDown, self.bMoveDown)
		self.bMoveDown.SetToolTip("Move the selected object down 1 line")
		self.bMoveDown.Enable(False)
		bhsz.Add(self.bMoveDown)

		vsz.Add(bhsz)
		hsz.Add(vsz)

		sz.Add(hsz)
		sz.AddSpacer(10)

		vsz = wx.BoxSizer(wx.VERTICAL)

		vsz.AddSpacer(5)

		box = wx.StaticBox(self, wx.ID_ANY, " Material Dimensions ")
		vbsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		bsizer = wx.BoxSizer(wx.HORIZONTAL)

		bsizer.AddSpacer(SBMARGIN)
		bsizer.Add(wx.StaticText(self, wx.ID_ANY, "Wd:"), 0, wx.TOP, 9)

		self.fsWidth = FS.FloatSpin(self, wx.ID_ANY, size=SPDIM, min_val=0, max_val=400,
				   increment=0.1, value=self.material.getWidth(), agwStyle=FS.FS_RIGHT)
		self.fsWidth.SetFormat("%f")
		self.fsWidth.SetDigits(1)
		bsizer.Add(self.fsWidth, 0, wx.TOP+wx.BOTTOM, 5)
		self.fsWidth.Bind(FS.EVT_FLOATSPIN, self.onFSMaterialWidth)

		bsizer.AddSpacer(SBMARGIN)
		bsizer.Add(wx.StaticText(self, wx.ID_ANY, "Ht:"), 0, wx.TOP, 9)

		self.fsHeight = FS.FloatSpin(self, wx.ID_ANY, size=SPDIM, min_val=0, max_val=400,
				   increment=0.1, value=self.material.getHeight(), agwStyle=FS.FS_RIGHT)
		self.fsHeight.SetFormat("%f")
		self.fsHeight.SetDigits(1)
		bsizer.Add(self.fsHeight, 0, wx.TOP+wx.BOTTOM, 5)
		self.fsHeight.Bind(FS.EVT_FLOATSPIN, self.onFSMaterialHeight)

		bsizer.AddSpacer(SBMARGIN)
		bsizer.Add(wx.StaticText(self, wx.ID_ANY, "Thk:"), 0, wx.TOP, 9)

		self.fsThick = FS.FloatSpin(self, wx.ID_ANY, size=SPDIM, min_val=0, max_val=50,
					increment=0.1, value=self.material.getThickness(), agwStyle=FS.FS_RIGHT)
		self.fsThick.SetFormat("%f")
		self.fsThick.SetDigits(1)
		bsizer.Add(self.fsThick, 0, wx.TOP+wx.BOTTOM, 5)
		self.fsThick.Bind(FS.EVT_FLOATSPIN, self.onFSMaterialThick)

		bsizer.AddSpacer(SBMARGIN)

		vbsizer.AddSpacer(SBMARGIN)
		vbsizer.Add(bsizer)
		vbsizer.AddSpacer(SBMARGIN)
		vsz.Add(vbsizer)

		sz.Add(vsz)

		sz.AddSpacer(10)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("add"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBAdd, self.bAdd)
		self.bAdd.SetToolTip("Add a new object to the bottom of the list")
		bsz.Add(self.bAdd)

		bsz.AddSpacer(10)

		self.bDel = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("delete"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBDel, self.bDel)
		self.bDel.SetToolTip("Delete the selected object")
		self.bDel.Enable(False)
		bsz.Add(self.bDel)

		bsz.AddSpacer(10)

		self.bRender = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("render"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBRender, self.bRender)
		self.bRender.SetToolTip("Render the G Code and save to file")
		self.bRender.Enable(False)
		bsz.Add(self.bRender)

		bsz.AddSpacer(10)

		self.bNew = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("new"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBNew, self.bNew)
		self.bNew.SetToolTip("Create a new empty model")
		bsz.Add(self.bNew)

		bsz.AddSpacer(10)

		self.bLoad = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("open"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBLoad, self.bLoad)
		self.bLoad.SetToolTip("Load a model from file")
		bsz.Add(self.bLoad)

		bsz.AddSpacer(10)

		self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("save"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBSave, self.bSave)
		self.bSave.SetToolTip("Save the model to the current file")
		self.bSave.Enable(False)
		bsz.Add(self.bSave)

		bsz.AddSpacer(10)

		self.bSaveAs = wx.BitmapButton(self, wx.ID_ANY, self.images.getByName("saveas"), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.onBSaveAs, self.bSaveAs)
		self.bSaveAs.SetToolTip("Save the model to a named file")
		self.bSaveAs.Enable(False)
		bsz.Add(self.bSaveAs)

		sz.AddSpacer(10)
		sz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(sz)

		return hsz

	def onLbProp(self, _):
		self.showObjectProperties()
		self.updateScrollButtons()

	def showObjectProperties(self):
		ox = self.objListBox.GetSelection()
		if ox == wx.NOT_FOUND:
			self.pGrid.clearProperties()
		else:
			self.pGrid.setProperties(self.objList[ox])

	def onClose(self, _):
		if not self.warnIfModified():
			return 

		self.Destroy()

	def onBScrollUp(self, _):
		ox = self.objListBox.GetSelection()
		self.objListBox.SetSelection(ox-1)
		self.showObjectProperties()
		self.updateScrollButtons()

	def onBScrollDown(self, _):
		ox = self.objListBox.GetSelection()
		self.objListBox.SetSelection(ox+1)
		self.showObjectProperties()
		self.updateScrollButtons()

	def onBMoveUp(self, _):
		ox = self.objListBox.GetSelection()
		sobj = self.objList[ox]
		self.objList[ox] = self.objList[ox-1]
		self.objList[ox-1] = sobj
		self.rebuildObjectListBox()
		self.objListBox.SetSelection(ox-1)
		self.updateScrollButtons()

	def onBMoveDown(self, _):
		ox = self.objListBox.GetSelection()
		sobj = self.objList[ox]
		self.objList[ox] = self.objList[ox+1]
		self.objList[ox+1] = sobj
		self.rebuildObjectListBox()
		self.objListBox.SetSelection(ox+1)
		self.updateScrollButtons()

	def updateScrollButtons(self):
		l = len(self.objList)
		ox = self.objListBox.GetSelection()
		if l <= 1 or ox == wx.NOT_FOUND:
			self.bScrollUp.Enable(False)
			self.bScrollDown.Enable(False)
			self.bMoveUp.Enable(False)
			self.bMoveDown.Enable(False)
			return

		self.bScrollUp.Enable(not(ox == 0))
		self.bMoveUp.Enable(not(ox == 0))
		self.bScrollDown.Enable(not (ox == (l-1)))
		self.bMoveDown.Enable(not (ox == (l-1)))

	def onMenuAddObject(self, _, objType):
		self.doObjectAddType(objType)

	def onMenuAddPreset(self, _, fn):
		path = os.path.join(cmdFolder, "presets", fn)
		try:
			with open(path, 'r') as f:
				j = json.load(f)
				obj = self.makeCncObject(j)
				self.doObjectAdd(obj)

		except IOError:
			self.message("Cannot read preset file '%s'." % path)

	def onFSMaterialWidth(self, _):
		nw = self.fsWidth.GetValue()
		self.material.setWidth(nw)

	def onFSMaterialHeight(self, _):
		nh = self.fsHeight.GetValue()
		self.material.setHeight(nh)

	def onFSMaterialThick(self, _):
		nt = self.fsThick.GetValue()
		self.material.setThickness(nt)

	def onBAdd(self, _):
		dlg = wx.SingleChoiceDialog(
				self, 'Choose the type of object to add', 'Add New Object',
				list(self.objectTypes.keys()),
				wx.OK | wx.CANCEL
				)

		rc = dlg.ShowModal()
		objType = None
		if rc == wx.ID_OK:
			objType = dlg.GetStringSelection()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.doObjectAddType(objType)

	def doObjectAddType(self, objType):
		obj = self.objectTypes[objType](self, {})
		el = obj.getErrors()
		if not el is None:
			for e in el:
				print(e)
		self.doObjectAdd(obj)

	def doObjectAdd(self, obj):
		self.setModified()
		self.pGrid.setProperties(obj)
		self.objListBox.Append(obj.getTitle())
		self.objList.append(obj)

		self.objListBox.SetSelection(len(self.objList)-1)

		self.bDel.Enable(True)
		self.bRender.Enable(True)
		self.fileMenu.Enable(MENU_FILE_RENDER, True)
		self.updateScrollButtons()

	def updateLabel(self):
		ox = self.objListBox.GetSelection()
		if ox == wx.NOT_FOUND:
			return
		self.rebuildObjectListBox()

	def rebuildObjectListBox(self):
		self.objListBox.Clear()
		for obj in self.objList:
			self.objListBox.Append(obj.getTitle())

	def onBDel(self, _):
		ox = self.objListBox.GetSelection()
		if ox == wx.NOT_FOUND:
			return
		
		ot = self.objList[ox].getTitle()
		dlg = wx.MessageDialog(self, "Are you sure you want to delete\n\n    \"%s\"?" % ot,
							   'Confirm Object Deletion',
							   wx.ICON_QUESTION | wx.YES_NO 
							   )
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if rc != wx.ID_YES:
			return

		self.setModified()

		del(self.objList[ox])
		self.rebuildObjectListBox()

		if ox >= len(self.objList):
			ox = len(self.objList)-1

		if ox >= 0:
			self.objListBox.SetSelection(ox)
		else:
			self.bDel.Enable(False)
			self.bSave.Enable(False)
			self.bSaveAs.Enable(False)
			self.bRender.Enable(False)
			self.fileMenu.Enable(MENU_FILE_SAVE, False)
			self.fileMenu.Enable(MENU_FILE_SAVEAS, False)
			self.fileMenu.Enable(MENU_FILE_SAVEEACH, False)
			self.fileMenu.Enable(MENU_FILE_RENDER, False)

		self.showObjectProperties()
		self.updateScrollButtons()

	def onBRender(self, _):
		dlg = RenderDlg(self, self.objList, self.cnc, self.toolList, self.images, self.settings)
		dlg.ShowModal()
		dlg.Destroy()

	
	def onBSave(self, evt):
		if self.currentFile is None:
			return self.onBSaveAs(evt)

		self.saveFile(self.currentFile)

	def saveFile(self, fn):
		j = [o.toJson() for o in self.objList]
		j.append(self.material.toJson())
		try:
			with open(fn, 'w') as f:
				f.write(json.dumps(j, indent=2))
				self.message("Model saved to file '%s'" % fn)

		except IOError:
			self.message("Cannot write current model file '%s'." % fn)

		self.setModified(False)

	def onBSaveAs(self, _):
		skey = "modeldir"
		sdir = self.settings.setting(skey)
		with wx.FileDialog(self, "Save Model file", wildcard="JSON files (*.json)|*.json",
					defaultDir=sdir,
					style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return	 # the user changed their mind
			
			self.currentFile = fileDialog.GetPath()
			ndir = os.path.dirname(self.currentFile)
			
			if ndir != sdir:
				self.settings.setSetting(skey, ndir)

			# save the current contents in the file
			self.saveFile(self.currentFile)

	def onSaveEachObject(self, _):
		skey = "objectdir"
		sdir = self.settings.setting(skey)
		for o in self.objList:
			lbl = o.getLabel()
			with wx.FileDialog(self, "Save Object '%s' to file" % lbl, wildcard="JSON files (*.json)|*.json",
						defaultDir = sdir,
						style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

				if fileDialog.ShowModal() == wx.ID_CANCEL:
					continue	 # the user changed their mind

				# save the current object in the file
				fn = fileDialog.GetPath()
				ndir = os.path.dirname(fn)
			
				if ndir != sdir:
					self.settings.setSetting(skey, ndir)
					
				j = o.toJson()
				try:
					with open(fn, 'w') as f:
						f.write(json.dumps(j, indent=2))
					self.message("Object '%s' saved to file '%s'" % (lbl, fn))

				except IOError:
					self.message("Cannot write current object '%s' to file '%s'." % (lbl, fn))

	def onBLoad(self, evt):
		if not self.warnIfModified():
			return 

		skey = "modeldir"
		sdir = self.settings.setting(skey)
		with wx.FileDialog(self, "Open Model file", wildcard="JSON files (*.json)|*.json",
					   defaultDir=sdir, style=wx.FD_OPEN) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return	 # the user changed their mind

			# load the current contents in the file
			fn = fileDialog.GetPath()
			
			ndir = os.path.dirname(fn)
		
			if ndir != sdir:
				self.settings.setSetting(skey, ndir)
					
			try:
				with open(fn, 'r') as f:
					j = json.load(f)
				self.currentFile = fn

			except IOError:
				self.message("Cannot read from input model file '%s'." % fn)
				return self.onBNew(evt)

		self.objList = []
		self.objListBox.Clear()
		for o in j:
			obj = self.makeCncObject(o)
			if obj is None:
				continue
			self.pGrid.setProperties(obj)
			self.objListBox.Append(obj.getTitle())
			self.objList.append(obj)

		self.objListBox.SetSelection(len(self.objList)-1)

		if len(self.objList) > 0:
			self.bDel.Enable(True)
		else:
			self.bDel.Enable(False)
		self.bRender.Enable(True)
		self.fileMenu.Enable(MENU_FILE_RENDER, False)
		self.updateScrollButtons()
		self.setModified(False)

	def makeCncObject(self, o):
		k = list(o.keys())[0]
		params = o[k]
		if k == "Material":
			self.material = Material(params)
			self.fsWidth.SetValue(self.material.getWidth())
			self.fsHeight.SetValue(self.material.getHeight())
			self.fsThick.SetValue(self.material.getThickness())
			self.cnc.setMaterial(self.material)
			return None

		if k not in self.rawObjectTypes.keys():
			print("Unknown object type: (%s)" % k)
			return None

		obj = self.rawObjectTypes[k](self, params)
		el = obj.getErrors()
		if not el is None:
			print("errors in makecncobject")
			for e in el:
				print(e)
		return obj

	def onBNew(self, _):
		if not self.warnIfModified():
			return 

		self.objList = []
		self.objListBox.Clear()
		self.pGrid.clearProperties()
		self.currentFile = None 
		self.updateScrollButtons()
		self.setModified(False)

	def onShapeokoProperties(self, _):
		dlg = ShapeokoDlg(self, self.cnc, self.images)
		dlg.ShowModal()
		dlg.Destroy()

if __name__ == '__main__':
	app = wx.App()
	frame = MyFrame()
	frame.Show(True)
	app.MainLoop()
