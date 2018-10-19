import math

from cncobject import cncObject
from toolmovement import toolMovement
from offset import offsetPath

from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "points": "A list of [x,y] coordinates of the vertices of the path",
			 "toolMovement": "tool movement with respect to line: toolMovement.online, inside(right), or outside(left)",
			 "depth": "how deep to cut the path",
			 "startHeight": "the starting height of the cut"}


class Path(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Path:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Path"

		if "points" not in self.params:
			self.params["points"] = [[0,0], [10,10]]

		if "toolMovement" not in self.params:
			self.params["toolMovement"] = toolMovement.online

		if "depth" not in self.params:
			self.params["depth"] = 10

		if "startHeight" not in self.params:
			self.params["startHeight"] = 0.0

	def getParameters(self):
		order = ["label", "points", "toolMovement", "startHeight", "depth"]

		props = {
			"label": {"label": "Label", "dataType": "str", "value": self.params["label"]},
			"points": {"label": "Data Points", "dataType": "point2dlist", "value": self.params["points"]},
			"toolMovement": {"label": "Tool Movement", "dataType": "toolMovement", "value": self.params["toolMovement"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]},
			"startHeight": {"label": "Starting Height", "dataType": "float", "value": self.params["startHeight"]}
		}

		return props, order

	def render(self, cnc, reporter):
		self.reporter = reporter
		points = self.params["points"]

		depth = float(self.params["depth"])

		rendering = []

		tm = self.params["toolMovement"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Depth: %f" % depth))
		rendering.extend(cnc.comment("Tool Movement: %s" % toolMovement.names[tm]))

		tdiam = cnc.getToolDiameter()
		trad = tdiam/2.0

		if tm == toolMovement.inside:
			points, rc = offsetPath(points, -trad)
			if not rc:
				self.renderError("Error calculating path offset")

		elif tm == toolMovement.outside:
			points, rc = offsetPath(points, trad)
			if not rc:
				self.renderError("Error calculating path offset")

		safez = cnc.getSafeZ()

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness
			
		self.checkExtents(mat, points)

		passdepth = cnc.getPassDepth()
		passes = int(math.ceil(depth/float(passdepth)))

		cz = float(self.params["startHeight"])
		rendering.extend(cnc.moveZ(safez))
		for i in range(passes):
			cz -= passdepth
			if cz < -depth:
				cz = -depth

			rendering.extend(cnc.comment("pass %d" % (i+1)))

			rendering.extend(cnc.moveXY(points[0]))
			rendering.extend(cnc.cutZ(cz))

			for p in points[1:]:
				rendering.extend(cnc.cutXY(p))

			rendering.extend(cnc.moveZ(safez))

		return rendering
