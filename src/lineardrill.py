import math

from cutdirection import cutDirection
from cncobject import cncObject

from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "anchorPoint": "The [x,y,z] coordinates of starting point",
			 "cutDirection": "which direction should the toolhead move: cutDirection.cw or cutDirection.ccw",
			 "depth": "how deep to cut the holes",
			 "angle": "the angle of toolhead movement(in degrees)",
			 "numberOfHoles": "how many holes to drill",
			 "holeSpacing": "the center-to-center distance between holes",
			 "holeDiameter": "the diameter of the drilled holes"}

class LinearDrill(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Linear Drill:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Linear Drill"

		if "anchorPoint" not in self.params:
			self.params["anchorPoint"] = [0, 0, 0]

		if "cutDirection" not in self.params:
			self.params["cutDirection"] = cutDirection.cw

		if "depth" not in self.params:
			self.params["depth"] = 10

		if "angle" not in self.params:
			self.params["angle"] = 0.0

		if "numberOfHoles" not in self.params:
			self.params["numberOfHoles"] = 10

		if "holeSpacing" not in self.params:
			self.params["holeSpacing"] = 10

		if "holeDiameter" not in self.params:
			self.params["holeDiameter"] = 3.0

	def getParameters(self):
		order = ["label", "anchorPoint", "cutDirection", "depth", "angle",
				 "numberOfHoles", "holeSpacing", "holeDiameter"]
		props = {
			"label": { "label": "Label", "dataType": "str", "value": self.params["label"]},
			"anchorPoint": {"label": "Anchor Point", "dataType": "point3d", "value": self.params["anchorPoint"]},
			"cutDirection": {"label": "Cut Direction", "dataType": "cutDirection", "value": self.params["cutDirection"]},
			"angle": {"label": "Angle", "dataType": "float", "value": self.params["angle"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]},
			"numberOfHoles": {"label": "Number of Holes", "dataType": "int", "value": self.params["numberOfHoles"]},
			"holeSpacing": {"label": "Hole Spacing", "dataType": "float", "value": self.params["holeSpacing"]},
			"holeDiameter": {"label": "Hole Diameter", "dataType": "float", "value": self.params["holeDiameter"]}
		}

		return props, order

	def render(self, cnc, reporter):
		self.reporter = reporter
		sx = float(self.params["anchorPoint"][0])
		sy = float(self.params["anchorPoint"][1])
		sz = float(self.params["anchorPoint"][2])

		angle = float(self.params["angle"])
		nHoles = int(self.params["numberOfHoles"])
		spacing = float(self.params["holeSpacing"])
		hDiam = float(self.params["holeDiameter"])
		depth = float(self.params["depth"])

		rendering = []

		cd = self.params["cutDirection"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Holes: Count: %d  Spacing: %f  Angle: %f  Diameter: %f" % (nHoles, spacing, angle, hDiam)))
		rendering.extend(cnc.comment("Depth: %f  CutDirection: %s" % (depth, cutDirection.names[cd])))

		tdiam = cnc.getToolDiameter()

		safez = cnc.getSafeZ()

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness


		passdepth = cnc.getPassDepth()
		passes = int(math.ceil(depth/float(passdepth)))

		stepover = cnc.getStepOver()

		if cd == cutDirection.cw:
			renderer = cnc.cutArcCw
		else:
			renderer = cnc.cutArcCcw

		dy = spacing * math.sin(math.radians(angle))
		dx = spacing * math.cos(math.radians(angle))

		rendering.extend(cnc.moveZ(safez))
		
		pts = []

		for ix in range(nHoles):
			cx = sx + ix * dx
			cy = sy + ix * dy
			pts.append([cx, cy])
			rendering.extend(cnc.moveXY([cx, cy]))
			cz = sz
			for iy in range(passes):
				cz -= passdepth
				if cz < -depth:
					cz = -depth

				rendering.extend(cnc.cutZ(cz))
				if hDiam > tdiam:
					maxyoff = (hDiam - tdiam) / 2.0
					yoff = stepover
					while True:
						if yoff > maxyoff:
							yoff = maxyoff
						rendering.extend(cnc.moveXY([None, cy-yoff]))
						rendering.extend(renderer(cx, cy - yoff, dy=yoff))
						if yoff >= maxyoff:
							break
						yoff += stepover

					rendering.extend(cnc.cutXY([cx, cy]))

			rendering.extend(cnc.moveZ(safez))

		self.checkExtents(mat, pts)
		
		return rendering
