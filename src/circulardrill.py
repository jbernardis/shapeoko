import math

from cutdirection import cutDirection
from cncobject import cncObject

from utilities import validateKeys, triangulate

validKeys = {"label": "Meaningful object name",
			 "centerPoint": "The [x,y,z] coordinates of circle center",
			 "cutDirection": "which direction should the toolhead move: cutDirection.cw or cutDirection.ccw",
			 "depth": "how deep to cut the holes",
			 "circleDiameter": "the diameter of the overall circle",
			 "holeSpacing": "the center-to-center distance between holes",
			 "holeDiameter": "the diameter of the drilled holes",
			 "insideOnly": "true or false - only drill inside the circle - not on perimeter",
			 "staggerRows": "true or false - stagger each row of the pattern"}

class CircularDrill(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Circular Drill:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Circular Drill"

		if "centerPoint" not in self.params:
			self.params["centerPoint"] = [0, 0, 0]

		if "cutDirection" not in self.params:
			self.params["cutDirection"] = cutDirection.cw

		if "depth" not in self.params:
			self.params["depth"] = 10

		if "circleDiameter" not in self.params:
			self.params["circleDiameter"] = 10.0

		if "holeSpacing" not in self.params:
			self.params["holeSpacing"] = 10

		if "holeDiameter" not in self.params:
			self.params["holeDiameter"] = 3.0

		if "insideOnly" not in self.params:
			self.params["insideOnly"] = False

		if "staggerRows" not in self.params:
			self.params["staggerRows"] = False

	def getParameters(self):
		order = ["label", "centerPoint", "cutDirection", "depth", "circleDiameter",
				 "holeSpacing", "holeDiameter", "insideOnly", "staggerRows"]
		props = {
			"label": { "label": "Label", "dataType": "str", "value": self.params["label"]},
			"centerPoint": {"label": "Center Point", "dataType": "point3d", "value": self.params["centerPoint"]},
			"cutDirection": {"label": "Cut Direction", "dataType": "cutDirection", "value": self.params["cutDirection"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]},
			"circleDiameter": {"label": "Circle Diameter", "dataType": "float", "value": self.params["circleDiameter"]},
			"holeSpacing": {"label": "Hole Spacing", "dataType": "float", "value": self.params["holeSpacing"]},
			"holeDiameter": {"label": "Hole Diameter", "dataType": "float", "value": self.params["holeDiameter"]},
			"insideOnly": {"label": "Drill Inside Only", "dataType": "bool", "value": self.params["insideOnly"]},
			"staggerRows": {"label": "Drill Staggered Rows", "dataType": "bool", "value": self.params["staggerRows"]}
		}

		return props, order

	def render(self, cnc, reporter):
		self.reporter = reporter
		sx = float(self.params["centerPoint"][0])
		sy = float(self.params["centerPoint"][1])
		sz = float(self.params["centerPoint"][2])

		spacing = float(self.params["holeSpacing"])
		hDiam = float(self.params["holeDiameter"])
		cDiam = float(self.params["circleDiameter"])
		depth = float(self.params["depth"])
		insideOnly = self.params["insideOnly"]
		staggerRows = self.params["staggerRows"]

		rendering = []

		cd = self.params["cutDirection"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Circle center: [%f, %f, %f]  Diameter: %f" % (sx, sy, sz, cDiam)))
		rendering.extend(cnc.comment("Holes: Spacing: %f  Diameter: %f" % (spacing, hDiam)))
		rendering.extend(cnc.comment("Depth: %f  CutDirection: %s" % (depth, cutDirection.names[cd])))
		if insideOnly:
			rendering.extend(cnc.comment("Interior drilling only"))
		elif staggerRows:
			rendering.extend(cnc.comment("With staggered rows"))

		tdiam = cnc.getToolDiameter()

		safez = cnc.getSafeZ()

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness


		minx = sx - cDiam/2
		maxx = sx + cDiam/2
		miny = sy - cDiam/2
		maxy = sy + cDiam/2
			
		self.checkExtents(mat, [[minx, miny], [maxx, maxy]])

		passdepth = cnc.getPassDepth()

		stepover = cnc.getStepOver()

		if cd == cutDirection.cw:
			renderer = cnc.cutArcCw
		else:
			renderer = cnc.cutArcCcw

		if insideOnly:
			radlimit = cDiam/2 - hDiam/2
		else:
			radlimit = cDiam/2

		nrows = int((maxy - miny)/(spacing))
		ncols = int((maxx - minx)/(spacing))

		xstep = (maxx - minx) / float(ncols)
		ystep = (maxy - miny) / float(nrows)

		if staggerRows:
			ystep *= 0.866
			# nrows = int((nrows/0.866)+0.5)

		rendering.extend(cnc.moveZ(safez))

		points = [(sx, sy)]
		ix = 1
		while sx + ix*xstep <= maxx:
			if ix*xstep <= radlimit:
				points = [(sx - ix*xstep, sy)] + points + [(sx + ix*xstep, sy)]
			ix += 1

		iy = 1
		while sy + iy*ystep <= maxy:
			rowu = []
			rowd = []
			ix = 0
			if staggerRows and iy%2 != 0:
				bx = xstep/2
			else:
				bx = 0

			while sx + ix*xstep + bx <= maxx:
				r = triangulate((0,0), (ix*xstep+bx, iy*ystep))
				if r <= radlimit:
					if bx == 0 and ix == 0:
						rowu.append((sx + ix*xstep + bx, sy + iy*ystep))
						rowd.append((sx + ix*xstep + bx, sy - iy*ystep))
					else:
						rowu = [(sx - ix*xstep - bx, sy + iy*ystep)] + rowu + [(sx + ix*xstep + bx, sy + iy*ystep)]
						rowd = [(sx - ix*xstep - bx, sy - iy*ystep)] + rowd + [(sx + ix*xstep + bx, sy - iy*ystep)]
				ix += 1

			points = rowu + points + rowd
			iy += 1

		passes = int(math.ceil(depth/passdepth))
		for p in points:
			rendering.extend(cnc.moveXY(p))
			cz = sz
			for i in range(passes):
				cz -= passdepth
				if cz < -materialthickness:
					cz = -materialthickness
				rendering.extend(cnc.cutZ(cz))
				if hDiam > tdiam:
					maxyoff = (hDiam-tdiam)/2.0
					yoff = stepover
					while True:
						if yoff > maxyoff:
							yoff = maxyoff
						rendering.extend(cnc.cutXY([None, p[1]-yoff]))
						rendering.extend(renderer(p[0], p[1]-yoff, dy=yoff))
						if yoff >= maxyoff:
							break
						yoff += stepover

					rendering.extend(cnc.cutXY(p))

			rendering.extend(cnc.moveZ(safez))

		return rendering
