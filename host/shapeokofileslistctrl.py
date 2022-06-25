import wx


class ShapeokoFilesListCtrl(wx.ListCtrl):
	def __init__(self, parent, images):
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(750, 280),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.parent = parent
		self.images = images
		
		font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.SetFont(font)

		self.fl = None
		self.selectedItem = None
		
		self.InsertColumn(0, "File")
		self.InsertColumn(1, "Modified")
		self.InsertColumn(2, "Mode")
		self.InsertColumn(3, "Size")
		self.SetColumnWidth(0, 240)
		self.SetColumnWidth(1, 260)
		self.SetColumnWidth(2, 160)
		self.SetColumnWidth(3, 90)
		
		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))
		
		self.il = wx.ImageList(16, 16)
		empty = self.makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxSelected = self.il.Add(self.images.pngSelected)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

	def checkAll(self):
		if self.fl is None:
			return
		self.selected = [True for _ in range(self.fl.count())]
		self.refreshAll(preserveSelection=True)
		self.notifyParent()

	def checkOne(self):
		if self.selectedItem is None:
			return

		self.selected[self.selectedItem] = not self.selected[self.selectedItem]
		self.RefreshItem(self.selectedItem)
		self.notifyParent()

	def checkNone(self):
		if self.fl is None:
			return
		self.selected = [False for _ in range(self.fl.count())]
		self.refreshAll()
		self.notifyParent()
		
	def setFl(self, fl):
		self.fl = fl
		self.selected = [False for _ in range(self.fl.count())]
		self.refreshItemCount()
		self.notifyParent()
		
	def refreshItemCount(self):
		oldItemCount = self.GetItemCount()
		newItemCount = self.fl.count()
		self.SetItemCount(newItemCount)	
		if newItemCount != oldItemCount:
			self.selected = [False for _ in range(newItemCount)]
			if newItemCount > 0:
				self.RefreshItems(0, newItemCount-1)
			self.notifyParent()
		
	def refreshAll(self, preserveSelection=False):
		if not preserveSelection:
			self.SetItemCount(0)
		self.refreshItemCount()
		if self.GetItemCount() > 0:
			self.RefreshItems(0, self.GetItemCount()-1)

	def notifyParent(self):
		self.parent.selectionChange(self.selected)

	def makeBlank(self):
		empty = wx.Bitmap(16,16,32)
		dc = wx.MemoryDC(empty)
		dc.SetBackground(wx.Brush((0,0,0,0)))
		dc.Clear()
		del dc
		empty.SetMaskColour((0,0,0))
		return empty

	def setSelection(self, tx, dclick=False):
		self.selectedItem = tx
		if tx is not None:
			self.Select(tx)
			
		if dclick:
			self.selected[tx] = not self.selected[tx]
			self.RefreshItem(tx)
			self.notifyParent()
		
	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index, dclick=True)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)
			
	def OnGetItemImage(self, item):
		if self.selected[item]:
			return self.idxSelected
		return self.idxEmpty
		

	def OnGetItemText(self, item, col):
		fl = self.fl.getFileByPosition(item)
		if fl is None:
			return "??"

		if col == 0:
			return fl.filename
		elif col == 1:
			return fl.mtime
		elif col == 2:
			return fl.mode
		elif col == 3:
			return fl.size

		return "??"

	def OnGetItemAttr(self, item):		
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
