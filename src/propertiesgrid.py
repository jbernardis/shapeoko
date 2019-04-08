import wx
import wx.propgrid as wxpg

import os
import re
import inspect

from pointlisteditdlg import PointListEditDialog
from anchortype import anchorType
from pockettype import pocketType
from cutdirection import cutDirection
from toolmovement import toolMovement

cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))


class Point2DProperty(wxpg.PGProperty):
	def __init__(self, label, name, value):
		wxpg.PGProperty.__init__(self, label, name)

		self.AddPrivateChild(wxpg.StringProperty("X", value=value[0]))
		self.AddPrivateChild(wxpg.StringProperty("Y", value=value[1]))

		self.m_value = value

	def GetClassName(self):
		return self.__class__.__name__

	def DoGetEditorClass(self):
		return wxpg.PropertyGridInterface.GetEditorByName("TextCtrl")

	def RefreshChildren(self):
		size = self.m_value
		self.Item(0).SetValue(size[0])
		self.Item(1).SetValue(size[1])

	def ChildChanged(self, thisValue, childIndex, childValue):
		size = self.m_value
		if childIndex == 0:
			size[0] = childValue
		elif childIndex == 1:
			size[1] = childValue
		else:
			raise AssertionError

		return size

	def ValueToString(self, value, argFlags):
		# TODO: Convert given property value to a string and return it
		return "[%s, %s]" % (value[0], value[1])

	def StringToValue(self, text, argFlags):
		# TODO: Adapt string to property value and return it
		value = eval(text)
		return (True, value)


class Point3DProperty(wxpg.PGProperty):
	def __init__(self, label, name, value):
		wxpg.PGProperty.__init__(self, label, name)

		self.AddPrivateChild(wxpg.StringProperty("X", value=value[0]))
		self.AddPrivateChild(wxpg.StringProperty("Y", value=value[1]))
		self.AddPrivateChild(wxpg.StringProperty("Z", value=value[2]))

		self.m_value = value

	def GetClassName(self):
		return self.__class__.__name__

	def DoGetEditorClass(self):
		return wxpg.PropertyGridInterface.GetEditorByName("TextCtrl")

	def RefreshChildren(self):
		size = self.m_value
		self.Item(0).SetValue(size[0])
		self.Item(1).SetValue(size[1])
		self.Item(2).SetValue(size[2])

	def ChildChanged(self, thisValue, childIndex, childValue):
		size = self.m_value
		if childIndex == 0:
			size[0] = childValue
		elif childIndex == 1:
			size[1] = childValue
		elif childIndex ==2:
			size[2] = childValue
		else:
			raise AssertionError

		return size

	def ValueToString(self, value, argFlags):
		# TODO: Convert given property value to a string and return it
		#return "[\"%s\", \"%s\", \"%s\"]" % (value[0], value[1], value[2])
		return "[%s, %s, %s]" % (value[0], value[1], value[2])

	def StringToValue(self, text, argFlags):
		# TODO: Adapt string to property value and return it
		value = eval(text)
		return (True, value)


class PointList2DProperty(wxpg.ArrayStringProperty):
	""" Sample of a custom custom ArrayStringProperty.

		Because currently some of the C++ helpers from wxArrayStringProperty
		and wxProperytGrid are not available, our implementation has to quite
		a bit 'manually'. Which is not too bad since Python has excellent
		string and list manipulation facilities.
	"""
	def __init__(self, label, name = wxpg.PG_LABEL, value=[], images=None):
		wxpg.ArrayStringProperty.__init__(self, label, name, value)
		self.m_display = '[ ]'
		self.images = images
		self.minvals = 2
		
	def setMinVals(self, mv):
		self.minvals = mv

	# NOTE: In the Classic version of the propgrid classes, all of the wrapped
	# property classes override DoGetEditorClass so it calls GetEditor and
	# looks up the class using that name, and hides DoGetEditorClass from the
	# usable API. Jumping through those hoops is no longer needed in Phoenix
	# as Phoenix allows overriding all necessary virtual methods without
	# special support in the wrapper code, so we just need to override
	# DoGetEditorClass here instead.
	def DoGetEditorClass(self):
		return wxpg.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")

	def ValueToString(self, value, flags):
		# let's just use the cached display value
		return self.m_display

	def OnSetValue(self):
		self.GenerateValueAsString()

	def DoSetAttribute(self, name, value):
		retval = super(PointList2DProperty, self).DoSetAttribute(name, value)
		return retval

	def GenerateValueAsString(self, delim=None):
		ls = self.GetValue()
		self.m_display = str(ls)

	def StringToValue(self, text, argFlags):
		""" If failed, return False or (False, None). If success, return tuple
			(True, newValue).
		"""
		delim = self.GetAttribute("Delimiter") 
		if delim == '"' or delim == "'":
			# Proper way to call same method from super class
			return super(PointList2DProperty, self).StringToValue(text, 0)
		v = [a.strip() for a in text.split(delim)]
		return (True, v)


	def OnEvent(self, propgrid, primaryEditor, event):
		if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
			data = self.GetValue()
			dlg = PointListEditDialog(propgrid, data, self.minvals, self.images)

			if dlg.ShowModal() == wx.ID_OK:
				nl = dlg.getValues()
				self.SetValueInEvent(nl)
				retval = True
			else:
				retval = False

			dlg.Destroy()
			return retval

		return False


class PropertiesGrid(wxpg.PropertyGrid):
	def __init__(self, parent, images, size=(400, 200)):

		pgFont = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		wxpg.PropertyGrid.__init__(self, parent, size=size, style=wxpg.PG_TOOLBAR)

		self.Bind(wxpg.EVT_PG_CHANGED, self.onPropertyChanged)
		self.definitionsMap = {}

		self.SetFont(pgFont)
		self.parent = parent
		self.images = images

		self.cncobj = None
		self.properties = None
		self.propertyOrder = None

		self.modified = False

		self.SetColumnCount(2)
		self.SetCaptionBackgroundColour(wx.Colour(215, 255, 215))
		self.SetCaptionTextColour(wx.Colour(0, 0, 0))
		self.SetMarginColour(wx.Colour(215, 255, 215))
		self.SetCellBackgroundColour(wx.Colour(255, 255, 191))
		self.SetCellTextColour(wx.Colour(0, 0, 0))
		self.SetCellDisabledTextColour(wx.Colour(0, 0, 0))
		self.SetEmptySpaceColour(wx.Colour(215, 255, 215))
		self.SetLineColour(wx.Colour(0, 0, 0))

		self.props = {}
		self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
		self.SetSize((500, -1))
		self.SetSplitterLeft()

	def clearProperties(self):
		self.properties = None
		self.propertyOrder = None
		self.props = {}
		self.Clear()

	def setProperties(self, cncobj):
		self.cncobj = cncobj
		self.properties, self.propertyOrder = cncobj.getParameters()
		self.Clear()
		self.Append(wxpg.PropertyCategory("Parameters for %s:" % type(cncobj).__name__))
		lines = 0
		self.props = {}
		for k in self.propertyOrder:
			pid = self.properties[k]["label"]
			dt = self.properties[k]["dataType"]

			pgp = self.getPropertyForType(k, pid, dt)
			self.Append(pgp)
			if dt == "bool":
				self.SetPropertyAttribute(pgp, "UseCheckbox", True)
			elif dt == "point2dlist":
				if "minvals" in self.properties[k]:
					mv = self.properties[k]["minvals"]
				else:
					mv = 2;
					
				pgp.setMinVals(mv)

			lines += 1
			self.props[k] = pgp

		self.setBaseValues()

	def getPropertyForType(self, name, label, dt):
		if dt == "str":
			pgp = wxpg.StringProperty(label, name, value="")

		elif dt == "float":
			pgp = wxpg.FloatProperty(label, name, value=0.0)

		elif dt == "int":
			pgp = wxpg.IntProperty(label, name, value=0)

		elif dt == "bool":
			pgp = wxpg.BoolProperty(label, name, value=False)

		elif dt == "point2dlist":
			pgp = PointList2DProperty(label, name, value=[], images=self.images)

		elif dt == "point2d":
			pgp = Point2DProperty(label, name, ["0.0", "0.0"])

		elif dt == "point3d":
			pgp = Point3DProperty(label, name, ["0.0", "0.0", "0.0"])

		elif dt == "anchorType":
			pgp = wxpg.EnumProperty(label, name, labels=anchorType.names, values=range(len(anchorType.names)), value=0)

		elif dt == "pocketType":
			pgp = wxpg.EnumProperty(label, name, labels=pocketType.names, values=range(len(pocketType.names)), value=0)

		elif dt == "cutDirection":
			pgp = wxpg.EnumProperty(label, name, labels=cutDirection.names, values=range(len(cutDirection.names)), value=0)

		elif dt == "toolMovement":
			pgp = wxpg.EnumProperty(label, name, labels=toolMovement.names, values=range(len(toolMovement.names)), value=0)

		elif dt == "enum":
			pgp = wxpg.EnumProperty(label, name, labels=["a", "b", "c"], values=range(3), value=0)

		else:
			#self.log("taking default action for unknown data type: %s" % dt)
			pgp = wxpg.StringProperty(label, name, value="")

		return pgp


	def setBaseValues(self):
		for tag in self.props.keys():
			self.setBaseValue(tag)

	def setBaseValue(self, tag):
		dt = self.properties[tag]["dataType"]
		pg = self.props[tag]
		try:
			v = self.properties[tag]["value"]
		except:
			v = None

		if dt == "str":
			if v is None:
				self.SetPropertyValue(pg, "")
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "float":
			if v is None:
				self.SetPropertyValue(pg, 0.0)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "int":
			if v is None:
				self.SetPropertyValue(pg, 0)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "point2dlist":
			if v is None:
				self.SetPropertyValue(pg, [])
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "point2d":
			if v is None:
				self.SetPropertyValue(pg, ["0.0", "0.0"])
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "point3d":
			if v is None:
				self.SetPropertyValue(pg, ["0.0", "0.0", "0.0"])
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "bool":
			if v is None:
				self.SetPropertyValue(pg, False)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "anchorType":
			if v is None:
				self.SetPropertyValue(pg, 0)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "pocketType":
			if v is None:
				self.SetPropertyValue(pg, 0)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "cutDirection":
			if v is None:
				self.SetPropertyValue(pg, 0)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "toolMovement":
			if v is None:
				self.SetPropertyValue(pg, 0)
			else:
				self.SetPropertyValue(pg, v)

		elif dt == "enum":
			self.SetPropertyValue(pg, 0)

		else:
			self.SetPropertyValue(pg, "")

	def onPropertyChanged(self, evt):
		self.setModified()
		p = evt.GetProperty()
		if p:
			self.cncobj.setParam(p.GetName(), p.GetValue())
			if p.GetName() == "label":
				self.parent.updateLabel()
			self.parent.setModified()

	def hasBeenModified(self):
		return self.modified

	def setModified(self, flag=True):
		self.modified = flag

	def formHelpText(self, stg, cv):
		ht = stg.getDescription()

		ut = stg.getUnit()
		if ut is not None:
			ht += " (%s)" % ut

		dft = stg.getDefault()
		dt = stg.getDType()
		if dt == "str":
			if dft is not None:
				dft = "\\n".join(re.split('\n', dft))

		if cv != dft:
			ht += " Default: %s" % str(dft)

		return ht

	def setProperty(self, pid, value):
		if pid not in self.properties.keys():
			self.log("Unknown property key: %s" % pid)
			return

		self.properties[pid].SetValue(value)
