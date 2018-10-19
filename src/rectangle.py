import math

from cncobject import cncObject
from anchortype import anchorType
from pockettype import pocketType
from cutdirection import cutDirection
from toolmovement import toolMovement

from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "anchorPoint": "The [x,y,z] coordinates of the rectangles reference point",
			 "anchorType": "Where of the rectangle the reference point is located: anchorType.lowerleft\n.centerleft, .upperleft, .uppercenter, .upperright, .centerright, .lowerright, .lowercenter, .center",
			 "pocketType": "The type of pocket to cut: pocketType.none, .centered, .vertical, or .horizontal",
			 "cutDirection": "which direction should the toolhead move: cutDirection.cw or cutDirection.ccw",
			 "toolMovement": "tool movement with respect to line: toolMovement.online, inside, or outside",
			 "angle": "angle of rotation of the rectangle (around [0, 0])",
			 "height": "the \"vertical\" dimension of the rectangle",
			 "width": "the \"horizontal\" dimension of the rectangle",
			 "depth": "how deep to cut the rectangle"}

class Rotater:
	def __init__(self, angle):
		self.cosv = math.cos(math.radians(angle))
		self.sinv = math.sin(math.radians(angle))

	def rotate(self, x, y):
		return x*self.cosv-y*self.sinv, x*self.sinv+y*self.cosv


class Rectangle(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Rectangle:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Rectangle"

		if "anchorPoint" not in self.params:
			self.params["anchorPoint"] = [0, 0, 0]

		if "anchorType" not in self.params:
			self.params["anchorType"] = anchorType.lowerleft

		if "pocketType" not in self.params:
			self.params["pocketType"] = pocketType.none

		if "cutDirection" not in self.params:
			self.params["cutDirection"] = cutDirection.cw

		if "toolMovement" not in self.params:
			self.params["toolMovement"] = toolMovement.online

		if "angle" not in self.params:
			self.params["angle"] = 0.0

		if "height" not in self.params:
			self.params["height"] = 10

		if "width" not in self.params:
			self.params["width"] = 10

		if "depth" not in self.params:
			self.params["depth"] = 10

	def getParameters(self):
		order = ["label", "anchorPoint", "anchorType", "pocketType", "cutDirection", "toolMovement",
				 "angle", "height", "width", "depth"]
		props = {
			"label": { "label": "Label", "dataType": "str", "value": self.params["label"]},
			"anchorPoint": {"label": "Anchor Point", "dataType": "point3d", "value": self.params["anchorPoint"]},
			"anchorType": {"label": "Anchor Type", "dataType": "anchorType", "value": self.params["anchorType"]},
			"pocketType": {"label": "Pocket Type", "dataType": "pocketType", "value": self.params["pocketType"]},
			"cutDirection": {"label": "Cut Direction", "dataType": "cutDirection", "value": self.params["cutDirection"]},
			"toolMovement": {"label": "Tool Movement", "dataType": "toolMovement", "value": self.params["toolMovement"]},
			"angle": { "label": "Angle", "dataType": "float", "value": self.params["angle"]},
			"height": {"label": "Height", "dataType": "float", "value": self.params["height"]},
			"width": {"label": "Width", "dataType": "float", "value": self.params["width"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]}
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
		pt = self.params["pocketType"]
		cd = self.params["cutDirection"]
		tm = self.params["toolMovement"]

		angle = self.params["angle"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Anchor:(%f, %f, %f)-%s   W:%f H:%f D:%f" % (sx, sy, sz,
											anchorType.names[at], width, height, depth)))
		rendering.extend(cnc.comment("Pocket:%s Cut Direction:%s Tool Movement: %s Angle: %f" % (pocketType.names[pt],
											cutDirection.names[cd], toolMovement.names[tm], angle)))

		rot = Rotater(angle)

		tdiam = cnc.getToolDiameter()
		trad = tdiam/2.0

		points = [[sx, sy], [sx, sy+height], [sx+width, sy+height], [sx+width, sy], [sx, sy]]

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

		for p in points:
			p[0] += adjx
			p[1] += adjy

		if tm == toolMovement.inside:
			points[0][0] += trad
			points[0][1] += trad
			points[1][0] += trad
			points[1][1] -= trad
			points[2][0] -= trad
			points[2][1] -= trad
			points[3][0] -= trad
			points[3][1] += trad
			points[4][0] += trad
			points[4][1] += trad

		elif tm == toolMovement.outside:
			points[0][0] -= trad
			points[0][1] -= trad
			points[1][0] -= trad
			points[1][1] += trad
			points[2][0] += trad
			points[2][1] += trad
			points[3][0] += trad
			points[3][1] -= trad
			points[4][0] -= trad
			points[4][1] -= trad

		if cd == cutDirection.ccw:
			np = points[::-1]
			points = np

		rendering.extend(cnc.comment("pass 1"))

		safez = cnc.getSafeZ()
		if pt == pocketType.none:
			rendering.extend(cnc.moveZ(safez))
			rendering.extend(cnc.moveXY(rot.rotate(points[0][0], points[0][1])))

		xmin = min(points[0][0], points[2][0]) + trad
		xmax = max(points[0][0], points[2][0]) - trad
		ymin = min(points[0][1], points[2][1]) + trad
		ymax = max(points[0][1], points[2][1]) - trad

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness
			
		self.checkExtents(map, [[xmin, ymin], [xmax, ymax]])


		passdepth = cnc.getPassDepth()
		passes = int(math.ceil(depth/float(passdepth)))
		stepover = cnc.getStepOver()

		cz = sz
		xlast = 0
		ylast = 0
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth

			if i != 0:
				rendering.extend(cnc.comment("pass %d" % (i+1)))

			if pt == pocketType.horizontal:
				first = True
				alt = True
				y = ymin
				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY(rot.rotate(xmin, ymin)))

				rendering.extend(cnc.cutZ(cz))
				while y <= ymax:
					if not first:
						rendering.extend(cnc.cutXY(rot.rotate(xlast, y)))

					if alt:
						rendering.extend(cnc.cutXY(rot.rotate(xmax, y)))
						xlast = xmax
					else:
						rendering.extend(cnc.cutXY(rot.rotate(xmin, y)))
						xlast = xmin
					y += tdiam * stepover
					first = False
					alt = not alt

				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY(rot.rotate(points[0][0], points[0][1])))

			elif pt == pocketType.vertical:
				first = True
				alt = True
				x = xmin
				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY(rot.rotate(xmin, ymin)))

				rendering.extend(cnc.cutZ(cz))
				while x <= xmax:
					if not first:
						rendering.extend(cnc.cutXY(rot.rotate(x, ylast)))

					if alt:
						rendering.extend(cnc.cutXY(rot.rotate(x, ymax)))
						ylast = ymax
					else:
						rendering.extend(cnc.cutXY(rot.rotate(x, ymin)))
						ylast = ymin
					x += tdiam * stepover
					first = False
					alt = not alt

				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY(rot.rotate(points[0][0], points[0][1])))

			elif pt == pocketType.centered:
				vertical = False
				if (xmax-xmin) > (ymax-ymin):
					ya = (ymax+ymin)/2.0
					yb = ya
					d = ymax - ya
					xa = xmin + d
					xb = xmax - d
				elif (xmax-xmin) < (ymax-ymin):
					vertical = True
					xa = (xmax+xmin)/2.0
					xb = xa
					d = xmax - xa
					ya = ymin + d
					yb = ymax - d
				else:
					xa = (xmax+xmin)/2.0
					xb = xa
					ya = (ymax+ymin)/2.0
					yb = ya

				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY(rot.rotate(xb, yb)))
				rendering.extend(cnc.cutZ(cz))
				rendering.extend(cnc.cutXY(rot.rotate(xa, ya)))

				d = stepover * tdiam
				while (xa-d) >= xmin:
					if cd == cutDirection.cw:
						rendering.extend(cnc.cutXY(rot.rotate(xa-d, ya-d)))
						if vertical:
							rendering.extend(cnc.cutXY(rot.rotate(xa-d, yb+d)))
						else:
							rendering.extend(cnc.cutXY(rot.rotate(xa-d, ya+d)))
						rendering.extend(cnc.cutXY(rot.rotate(xb+d, yb+d)))
						if vertical:
							rendering.extend(cnc.cutXY(rot.rotate(xb+d, ya-d)))
						else:
							rendering.extend(cnc.cutXY(rot.rotate(xb+d, yb-d)))
						rendering.extend(cnc.cutXY(rot.rotate(xa-d, ya-d)))
					else:
						rendering.extend(cnc.cutXY(rot.rotate(xa-d, ya-d)))
						if vertical:
							rendering.extend(cnc.cutXY(rot.rotate(xb+d, ya-d)))
						else:
							rendering.extend(cnc.cutXY(rot.rotate(xb+d, yb-d)))
						rendering.extend(cnc.cutXY(rot.rotate(xb+d, yb+d)))
						if vertical:
							rendering.extend(cnc.cutXY(rot.rotate(xa-d, yb+d)))
						else:
							rendering.extend(cnc.cutXY(rot.rotate(xa-d, ya+d)))
						rendering.extend(cnc.cutXY(rot.rotate(xa-d, ya-d)))
					d += stepover * tdiam

				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY(rot.rotate(points[0][0], points[0][1])))

			rendering.extend(cnc.cutZ(cz))
			for p in points[1:]:
				rendering.extend(cnc.cutXY(rot.rotate(p[0], p[1])))

		rendering.extend(cnc.moveZ(safez))
		return rendering
