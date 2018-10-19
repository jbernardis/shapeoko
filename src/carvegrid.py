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
			 "xSegments": "How many grid segments on the horizontal axis",
			 "ySegments": "How many grid segments on the vertical axis"}


class CarveGrid(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Carve Grid:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Carve Grid"

		if "anchorPoint" not in self.params:
			self.params["anchorPoint"] = [0, 0, 0]

		if "anchorType" not in self.params:
			self.params["anchorType"] = anchorType.lowerleft

		if "height" not in self.params:
			self.params["height"] = 10

		if "width" not in self.params:
			self.params["width"] = 10

		if "depth" not in self.params:
			self.params["depth"] = 10

		if "xSegments" not in self.params:
			self.params["xSegments"] = 10

		if "ySegments" not in self.params:
			self.params["ySegments"] = 10

	def getParameters(self):
		order = ["label", "anchorPoint", "anchorType", "height", "width",
				 "depth", "xSegments", "ySegments"]
		props = {
			"label": {"label": "Label", "dataType": "str", "value": self.params["label"]},
			"anchorPoint": {"label": "Anchor Point", "dataType": "point3d", "value": self.params["anchorPoint"]},
			"anchorType": {"label": "Anchor Type", "dataType": "anchorType", "value": self.params["anchorType"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]},
			"height": {"label": "Height", "dataType": "float", "value": self.params["height"]},
			"width": {"label": "Width", "dataType": "float", "value": self.params["width"]},
			"xSegments": {"label": "Horizontal Segments", "dataType": "int", "value": self.params["xSegments"]},
			"ySegments": {"label": "Vertical Segments", "dataType": "int", "value": self.params["ySegments"]}
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

		xSegments = int(self.params["xSegments"])
		ySegments = int(self.params["ySegments"])

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Anchor:(%f, %f, %f)-%s   W:%f H:%f D:%f" % (sx, sy, sz,
											anchorType.names[at], width, height, depth)))
		rendering.extend(cnc.comment("X Segments: %d   Y Segments: %d" % (xSegments, ySegments)))

		safez = cnc.getSafeZ()

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness


		passdepth = cnc.getPassDepth()

		segszx = height / float(xSegments)
		segszy = height / float(ySegments)

		adjx = 0
		adjy = 0

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

		xvals = [sx + i*segszx + adjx for i in range(xSegments+1)]
		yvals = [sy + i*segszy + adjy for i in range(ySegments+1)]
		
		self.checkExtents(mat, [[min(xvals), min(yvals)], [max(xvals), max(yvals)]])

		points = []

		flag = False
		for i in range(0, xSegments+1):
			if not flag:
				points.append([xvals[i], yvals[0], xvals[i], yvals[-1]])
			else:
				points.append([xvals[i], yvals[-1], xvals[i], yvals[0]])
			flag = not flag

		flag = False
		for i in range(0, ySegments+1):
			if not flag:
				points.append([xvals[0], yvals[i], xvals[-1], yvals[i]])
			else:
				points.append([xvals[-1], yvals[i], xvals[0], yvals[i]])
			flag = not flag

		passes = int(math.ceil(float(depth)/float(passdepth)))

		cdepth = 0
		for i in range(passes):
			rendering.extend(cnc.comment("pass %d" % (i+1)))

			cdepth += passdepth
			if cdepth > depth:
				cdepth = depth

			rendering.extend(cnc.moveZ(safez))
			for p in points:
				rendering.extend(cnc.moveXY([p[0], p[1]]))
				rendering.extend(cnc.cutZ(sz-cdepth))
				rendering.extend(cnc.cutXY([p[2], p[3]]))
				rendering.extend(cnc.moveZ(safez))

		rendering.extend(cnc.moveXY([sx, sy]))

		return rendering
