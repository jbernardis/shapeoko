import math

from cutdirection import cutDirection
from anchortype import anchorType
from cncobject import cncObject

from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "anchorPoint": "The [x,y,z] coordinates of anchor point",
			 "anchorType": "Where of the rectangle the reference point is located: anchorType.lowerleft\n.centerleft, .upperleft, .uppercenter, .upperright, .centerright, .lowerright, .lowercenter, .center",
			 "height": "the \"vertical\" dimension of the rectangle",
			 "width": "the \"horizontal\" dimension of the rectangle",
			 "cutDirection": "which direction should the toolhead move: cutDirection.cw or cutDirection.ccw",
			 "depth": "how deep to cut the holes",
			 "holeSpacing": "the center-to-center distance between holes",
			 "holeDiameter": "the diameter of the drilled holes",
			 "perimeterOnly": "true or false - only drill the perimeter - not the inside",
			 "insideOnly": "true or false - only drill the inside - not the perimeter",
			 "staggerRows": "true or false - stagger each row of the pattern"}

class RectangularDrill(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Rectangular Drill:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Rectangular Drill"

		if "anchorPoint" not in self.params:
			self.params["anchorPoint"] = [0, 0, 0]

		if "anchorType" not in self.params:
			self.params["anchorType"] = anchorType.lowerleft

		if "height" not in self.params:
			self.params["height"] = 10

		if "width" not in self.params:
			self.params["width"] = 10

		if "cutDirection" not in self.params:
			self.params["cutDirection"] = cutDirection.cw

		if "depth" not in self.params:
			self.params["depth"] = 10

		if "holeSpacing" not in self.params:
			self.params["holeSpacing"] = 10

		if "holeDiameter" not in self.params:
			self.params["holeDiameter"] = 3.0

		if "insideOnly" not in self.params:
			self.params["insideOnly"] = False

		if "perimeterOnly" not in self.params:
			self.params["perimeterOnly"] = False

		if "staggerRows" not in self.params:
			self.params["staggerRows"] = False

	def getParameters(self):
		order = ["label", "anchorPoint", "anchorType", "height", "width",
				 "cutDirection", "depth", "holeSpacing", "holeDiameter",
				 "insideOnly", "perimeterOnly", "staggerRows"]
		props = {
			"label": { "label": "Label", "dataType": "str", "value": self.params["label"]},
			"anchorPoint": {"label": "Anchor Point", "dataType": "point3d", "value": self.params["anchorPoint"]},
			"anchorType": {"label": "Anchor Type", "dataType": "anchorType", "value": self.params["anchorType"]},
			"cutDirection": {"label": "Cut Direction", "dataType": "cutDirection", "value": self.params["cutDirection"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]},
			"height": {"label": "Height", "dataType": "float", "value": self.params["height"]},
			"width": {"label": "Width", "dataType": "float", "value": self.params["width"]},
			"holeSpacing": {"label": "Hole Spacing", "dataType": "float", "value": self.params["holeSpacing"]},
			"holeDiameter": {"label": "Hole Diameter", "dataType": "float", "value": self.params["holeDiameter"]},
			"insideOnly": {"label": "Drill Inside Only", "dataType": "bool", "value": self.params["insideOnly"]},
			"perimeterOnly": {"label": "Drill Perimeter Only", "dataType": "bool", "value": self.params["perimeterOnly"]},
			"staggerRows": {"label": "Drill Staggered Rows", "dataType": "bool", "value": self.params["staggerRows"]}
		}

		return props, order

	def render(self, cnc, reporter):
		self.reporter = reporter
		sx = float(self.params["anchorPoint"][0])
		sy = float(self.params["anchorPoint"][1])
		sz = float(self.params["anchorPoint"][2])

		width = float(self.params["width"])
		height = float(self.params["height"])

		spacing = float(self.params["holeSpacing"])
		hDiam = float(self.params["holeDiameter"])
		depth = float(self.params["depth"])

		insideOnly = self.params["insideOnly"]
		perimeterOnly = self.params["perimeterOnly"]
		staggerRows = self.params["staggerRows"]
		if perimeterOnly:
			insideOnly = False
			staggerRows = False

		rendering = []

		cd = self.params["cutDirection"]
		at = self.params["anchorType"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Anchor:(%f, %f, %f)-%s   W:%f H:%f D:%f" % (sx, sy, sz,
											anchorType.names[at], width, height, depth)))
		rendering.extend(cnc.comment("Holes: Spacing: %f  Diameter: %f" % (spacing, hDiam)))
		rendering.extend(cnc.comment("Depth: %f  CutDirection: %s" % (depth, cutDirection.names[cd])))
		if insideOnly:
			rendering.extend(cnc.comment("Interior drilling only"))
		if perimeterOnly:
			rendering.extend(cnc.comment("Perimeter drilling only"))
		if staggerRows:
			rendering.extend(cnc.comment("With staggered rows"))

		if at == anchorType.centerleft:
			sy -= height / 2.0
		elif at == anchorType.upperleft:
			sy -= height
		elif at == anchorType.uppercenter:
			sx -= width / 2.0
			sy -= height
		elif at == anchorType.upperright:
			sy -= height
			sx -= width
		elif at == anchorType.centerright:
			sx -= width
			sy -= height / 2.0
		elif at == anchorType.lowerright:
			sx -= width
		elif at == anchorType.lowercenter:
			sx -= width / 2.0
		elif at == anchorType.center:
			sx -= width / 2.0
			sy -= height / 2.0

		tdiam = cnc.getToolDiameter()

		safez = cnc.getSafeZ()

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness


		passdepth = cnc.getPassDepth()

		stepover = cnc.getStepOver()

		if cd == cutDirection.cw:
			renderer = cnc.cutArcCw
		else:
			renderer = cnc.cutArcCcw

		if insideOnly:
			minx = sx + hDiam/2.0
			maxx = sx + width - hDiam/2.0
			miny = sy + hDiam/2.0
			maxy = sy + height - hDiam/2.0
		else:
			minx = sx
			maxx = sx + width
			miny = sy
			maxy = sy + height
			
		self.checkExtents(mat, [[minx, miny], [maxx, maxy]])

		nrows = int((maxy - miny)/spacing)
		ncols = int((maxx - minx)/spacing)

		xstep = (maxx - minx) / float(ncols)
		ystep = (maxy - miny) / float(nrows)

		if staggerRows:
			ystep *= 0.866
			nrows = int((nrows/0.866)+0.5)

		cx = minx
		cy = miny

		rendering.extend(cnc.moveZ(safez))

		passes = int(math.ceil(depth/passdepth))
		for iy in range(nrows+1):
			for ix in range(ncols+1):
				includeHole = False
				if not perimeterOnly:
					if cx <= maxx and cy <= maxy:
						includeHole = True
				else:
					if ix == 0 or ix == ncols or iy == 0 or iy == nrows:
						includeHole = True

				if includeHole:
					rendering.extend(cnc.moveXY([cx, cy]))
					cz = sz
					for i in range(passes):
						cz -= passdepth
						if cz < -depth:
							cz = -depth
						rendering.extend(cnc.cutZ(cz))
						if hDiam > tdiam:
							maxyoff = (hDiam-tdiam)/2.0
							yoff = stepover
							while True:
								if yoff > maxyoff:
									yoff = maxyoff
								rendering.extend(cnc.cutXY([None, cy-yoff]))
								rendering.extend(renderer(cx, cy-yoff, dy=yoff))
								if yoff >= maxyoff:
									break
								yoff += stepover

							rendering.extend(cnc.cutXY([cx, cy]))

					rendering.extend(cnc.moveZ(safez))

				cx += xstep
			cy += ystep
			if staggerRows and iy%2 == 0:
				cx = minx + xstep/2
			else:
				cx = minx

		return rendering
