import math

from cncobject import cncObject
from anchortype import anchorType

from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "anchorPoint": "The [x,y,z] coordinates of the grid reference point",
			 "anchorType": "Where on the grid the reference point is located: anchorType.lowerleft\n.centerleft, .upperleft, .uppercenter, .upperright, .centerright, .lowerright, .lowercenter, .center",
			 "height": "the \"vertical\" dimension of the grid",
			 "width": "the \"horizontal\" dimension of the grid",
			 "depth": "how deep to cut the grid",
			 "border": "True or False - carve the rectangular border",
			 "segments": "How many segments on the horizontal and vertical axes"}


class CarveDiamond(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Carve Diamond:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Carve Diamond"

		if "anchorPoint" not in self.params:
			self.params["anchorPoint"] = [0, 0, 0]

		if "anchorType" not in self.params:
			self.params["anchorType"] = anchorType.lowerleft

		if "height" not in self.params:
			self.params["height"] = 10

		if "width" not in self.params:
			self.params["width"] = 10

		if "depth" not in self.params:
			self.params["depth"] = 1

		if "segments" not in self.params:
			self.params["segments"] = 10

		if "border" not in self.params:
			self.params["border"] = True

	def getParameters(self):
		order = ["label", "anchorPoint", "anchorType", "height", "width",
				 "depth", "segments", "border"]
		props = {
			"label": {"label": "Label", "dataType": "str", "value": self.params["label"]},
			"anchorPoint": {"label": "Anchor Point", "dataType": "point3d", "value": self.params["anchorPoint"]},
			"anchorType": {"label": "Anchor Type", "dataType": "anchorType", "value": self.params["anchorType"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]},
			"height": {"label": "Height", "dataType": "float", "value": self.params["height"]},
			"width": {"label": "Width", "dataType": "float", "value": self.params["width"]},
			"segments": {"label": "Number of Segments", "dataType": "int", "value": self.params["segments"]},
			"border": {"label": "Carve Border", "dataType": "bool", "value": self.params["border"]}
		}

		return props, order

	def render(self, cnc, reporter):
		self.reporter = reporter
		sx = float(self.params["anchorPoint"][0])
		sy = float(self.params["anchorPoint"][1])
		sz = float(self.params["anchorPoint"][2])

		width = float(self.params["width"])
		height = float(self.params["height"])
		depth = float(self.params["depth"])

		rendering = []

		at = self.params["anchorType"]

		segments = int(self.params["segments"])

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Anchor:(%f, %f, %f)-%s   W:%f H:%f D:%f" % (sx, sy, sz,
											anchorType.names[at], width, height, depth)))
		rendering.extend(cnc.comment("Segments: %d" % segments))

		safez = cnc.getSafeZ()

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness


		passdepth = cnc.getPassDepth()

		segszx = width / float(segments)
		segszy = height / float(segments)

		adjx = 0
		adjy = 0

		border = self.params["border"]

		if at == anchorType.upperleft:
			adjy = -height
		elif at == anchorType.uppercenter:
			adjy = -height
			adjx = -width / 2.0
		elif at == anchorType.upperright:
			adjy = -height
			adjx = -width
		elif at == anchorType.centerleft:
			adjy = -height/2.0
		elif at == anchorType.center:
			adjx = -width / 2.0
			adjy = -height / 2.0
		elif at == anchorType.centerright:
			adjx = -width
			adjy = -height / 2.0
		elif at == anchorType.lowercenter:
			adjx = -width / 2.0
		elif at == anchorType.lowerright:
			adjx = -width

		xvals = [sx + i*segszx + adjx for i in range(segments+1)]
		yvals = [sy + i*segszy + adjy for i in range(segments+1)]
		
		self.checkExtents(mat, [[min(xvals), min(yvals)], [max(xvals), max(yvals)]])

		points = []

		for i in range(1, segments):
			points.append([xvals[0], yvals[segments-i], xvals[i], yvals[segments]])

		points.append([xvals[0], yvals[0], xvals[segments], yvals[segments]])

		for i in range(1, segments):
			points.append([xvals[i], yvals[0], xvals[segments], yvals[segments-i]])

		for i in range(1, segments):
			points.append([xvals[segments-i], yvals[segments], xvals[segments], yvals[segments-i]])

		points.append([xvals[0], yvals[segments], xvals[segments], yvals[0]])

		for i in range(1, segments):
			points.append([xvals[0], yvals[segments-i], xvals[segments-i], yvals[0]])

		passes = int(math.ceil(float(depth)/float(passdepth)))

		cdepth = 0
		flag = True
		for i in range(passes):
			cdepth += passdepth
			if cdepth > depth:
				cdepth = depth

			rendering.extend(cnc.moveZ(safez))
			for p in points:
				if flag:
					xa = p[0]
					ya = p[1]
					xb = p[2]
					yb = p[3]
				else:
					xa = p[2]
					ya = p[3]
					xb = p[0]
					yb = p[1]
				flag = not flag

				rendering.extend(cnc.moveXY([xa, ya]))
				rendering.extend(cnc.cutZ(sz-cdepth))
				rendering.extend(cnc.cutXY([xb, yb]))
				rendering.extend(cnc.moveZ(safez))
			if border:
				rendering.extend(cnc.moveXY([xvals[0], yvals[0]]))
				rendering.extend(cnc.cutZ(sz-cdepth))
				rendering.extend(cnc.cutXY([xvals[segments], yvals[0]]))
				rendering.extend(cnc.cutXY([xvals[segments], yvals[segments]]))
				rendering.extend(cnc.cutXY([xvals[0], yvals[segments]]))
				rendering.extend(cnc.cutXY([xvals[0], yvals[0]]))
				rendering.extend(cnc.moveZ(safez))

		rendering.extend(cnc.moveXY([sx, sy]))

		return rendering
