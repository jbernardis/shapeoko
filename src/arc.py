import math

from cncobject import cncObject
from cutdirection import cutDirection
from toolmovement import toolMovement

from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "centerPoint": "The [x,y,z] coordinates of arc/circle center",
			 "diameter": "The diameter of the arc",
			 "cutDirection": "which direction should the toolhead move: cutDirection.cw or cutDirection.ccw",
			 "toolMovement": "tool movement with respect to line: toolMovement.online, inside, or outside",
			 "depth": "how deep to cut the arc",
			 "startAngle": "the starting angle of the arc (in degrees)",
			 "endAngle": "the ending angle of the arc (in degrees)"}


class Arc(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Arc:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Arc"

		if "centerPoint" not in self.params:
			self.params["centerPoint"] = [0, 0, 0]

		if "diameter" not in self.params:
			self.params["diameter"] = 10.0

		if "cutDirection" not in self.params:
			self.params["cutDirection"] = cutDirection.cw

		if "toolMovement" not in self.params:
			self.params["toolMovement"] = toolMovement.online

		if "depth" not in self.params:
			self.params["depth"] = 10

		if "startAngle" not in self.params:
			self.params["startAngle"] = 0.0

		if "endAngle" not in self.params:
			self.params["endAngle"] = 90.0


	def getParameters(self):
		order = ["label", "centerPoint", "diameter", "cutDirection", "toolMovement", "depth", "startAngle", "endAngle"]
		props = {
			"label": { "label": "Label", "dataType": "str", "value": self.params["label"]},
			"centerPoint": {"label": "Center Point", "dataType": "point3d", "value": self.params["centerPoint"]},
			"cutDirection": {"label": "Cut Direction", "dataType": "cutDirection", "value": self.params["cutDirection"]},
			"toolMovement": {"label": "Tool Movement", "dataType": "toolMovement", "value": self.params["toolMovement"]},
			"startAngle": {"label": "Starting Angle", "dataType": "float", "value": self.params["startAngle"]},
			"endAngle": {"label": "Ending Angle", "dataType": "float", "value": self.params["endAngle"]},
			"diameter": {"label": "Diameter", "dataType": "float", "value": self.params["diameter"]},
			"depth": {"label": "Depth", "dataType": "float", "value": self.params["depth"]}
		}

		return props, order


	def render(self, cnc, reporter):
		self.reporter = reporter
		sx = float(self.params["centerPoint"][0])
		sy = float(self.params["centerPoint"][1])
		sz = float(self.params["centerPoint"][2])

		diam = float(self.params["diameter"])
		rad = diam/2.0
		depth = float(self.params["depth"])

		sa = float(self.params["startAngle"])
		ea = float(self.params["endAngle"])

		rendering = []

		cd = self.params["cutDirection"]
		tm = self.params["toolMovement"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Center:(%f, %f, %f)Diameter:%f Depth:%f" % (sx, sy, sz, diam, depth)))
		rendering.extend(cnc.comment("Start Angle: %f   End Angle:%f" % (sa, ea)))
		rendering.extend(cnc.comment("Cut Direction:%s Tool Movement: %s" % (cutDirection.names[cd], toolMovement.names[tm])))

		tdiam = cnc.getToolDiameter()
		trad = tdiam/2.0

		if tm == toolMovement.inside:
			rad -= trad
		elif tm == toolMovement.outside:
			rad += trad

		if cd == cutDirection.cw:
			renderer = cnc.cutArcCw
		else:
			renderer = cnc.cutArcCcw

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness

		safez = cnc.getSafeZ()
		passdepth = cnc.getPassDepth()
		passes = int(math.ceil(depth/float(passdepth)))

		stx = rad * math.cos(math.radians(sa)) + sx
		sty = rad * math.sin(math.radians(sa)) + sy
		enx = rad * math.cos(math.radians(ea)) + sx
		eny = rad * math.sin(math.radians(ea)) + sy
		
		self.checkExtents(mat, [[stx, sty], [enx, eny]])

		rendering.extend(cnc.moveZ(safez))

		cz = sz
		for i in range(passes):
			rendering.extend(cnc.comment("pass %d" % (i+1)))
			rendering.extend(cnc.moveXY([stx, sty]))
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			rendering.extend(cnc.cutZ(cz))
			rendering.extend(renderer(enx, eny, dx=sx-stx, dy=sy-sty))
			rendering.extend(cnc.moveZ(safez))

		return rendering
