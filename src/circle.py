import math

from cncobject import cncObject
from pockettype import pocketType
from cutdirection import cutDirection
from toolmovement import toolMovement
from utilities import validateKeys

validKeys = {"label": "Meaningful object name",
			 "centerPoint": "The [x,y,z] coordinates of arc/circle center",
			 "diameter": "The diameter of the circle",
			 "pocketType": "The type of pocket to cut: pocketType.none or pocketType.centered",
			 "cutDirection": "which direction should the toolhead move: cutDirection.cw or cutDirection.ccw",
			 "toolMovement": "tool movement with respect to line: toolMovement.online, inside, or outside",
			 "depth": "how deep to cut the arc"}

class Circle(cncObject):
	def __init__(self, parent, params):
		cncObject.__init__(self, parent)
		self.params = params.copy()

		valid = validateKeys(self.params.keys(), validKeys)
		if valid is not None:
			self.createErrors(["Parameter errors for Circle:"] + valid)

		if "label" not in self.params:
			self.params["label"] = "Circle"

		if "centerPoint" not in self.params:
			self.params["centerPoint"] = [0, 0, 0]

		if "diameter" not in self.params:
			self.params["diameter"] = 10.0

		if "pocketType" not in self.params:
			self.params["pocketType"] = pocketType.none

		if "cutDirection" not in self.params:
			self.params["cutDirection"] = cutDirection.cw

		if "toolMovement" not in self.params:
			self.params["toolMovement"] = toolMovement.online

		if "depth" not in self.params:
			self.params["depth"] = 10


	def getParameters(self):
		order = ["label", "centerPoint", "diameter", "pocketType", "cutDirection", "toolMovement", "depth"]
		props = {
			"label": { "label": "Label", "dataType": "str", "value": self.params["label"]},
			"centerPoint": {"label": "Center Point", "dataType": "point3d", "value": self.params["centerPoint"]},
			"pocketType": {"label": "Pocket Type", "dataType": "pocketType", "value": self.params["pocketType"]},
			"cutDirection": {"label": "Cut Direction", "dataType": "cutDirection", "value": self.params["cutDirection"]},
			"toolMovement": {"label": "Tool Movement", "dataType": "toolMovement", "value": self.params["toolMovement"]},
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
		depth = float(self.params["depth"])

		rendering = []

		pt = self.params["pocketType"]
		cd = self.params["cutDirection"]
		tm = self.params["toolMovement"]

		rendering.extend(cnc.comment(""))
		rendering.extend(cnc.comment("%s" % self.params["label"]))
		rendering.extend(cnc.toolInfo())
		rendering.extend(cnc.comment("Center:(%f, %f, %f)Diameter:%f Depth:%f" % (sx, sy, sz, diam, depth)))
		rendering.extend(cnc.comment("Pocket:%s Cut Direction:%s Tool Movement: %s" % (pocketType.names[pt], cutDirection.names[cd], toolMovement.names[tm])))

		tdiam = cnc.getToolDiameter()

		if tm == toolMovement.inside:
			diam -= tdiam

		elif tm == toolMovement.outside:
			diam += tdiam

		if cd == cutDirection.cw:
			renderer = cnc.cutArcCw
		else:
			renderer = cnc.cutArcCcw

		mat = cnc.getMaterial()
		materialthickness = mat.getThickness()
		if depth > materialthickness:
			self.renderWarning("Object %s exceeds material depth (%f > %f)" % (self.params["label"], depth, materialthickness))
			depth = materialthickness
			
		self.checkExtents(mat, [[sx-diam/2-tdiam/2, sy-diam/2-tdiam/2], [sx+diam/2+tdiam/2, sy+diam/2+tdiam/2]])

		safez = cnc.getSafeZ()
		passdepth = cnc.getPassDepth()
		passes = int(math.ceil(depth/float(passdepth)))
		stepover = cnc.getStepOver()

		if pt == pocketType.none:
			rendering.extend(cnc.moveZ(safez))
			rendering.extend(cnc.moveXY([sx, sy-diam/2]))

		cz = sz
		for i in range(passes):
			rendering.extend(cnc.comment("pass %d" % (i+1)))
			cz -= passdepth
			if cz < -depth:
				cz = -depth
			if pt == pocketType.none:
				rendering.extend(cnc.cutZ(cz))
			else:
				rendering.extend(cnc.moveZ(safez))
				rendering.extend(cnc.moveXY([sx, sy]))
				rendering.extend(cnc.cutZ(cz))
				r = tdiam * stepover
				while r < diam/2:
					rendering.extend(cnc.cutXY([None, sy-r]))
					rendering.extend(renderer(sx, sy-r, dy=r))
					r += tdiam * stepover

				rendering.extend(cnc.cutXY([None, sy-diam/2]))

			rendering.extend(renderer(sx, sy-diam/2, dy=diam/2))

		rendering.extend(cnc.moveZ(safez))

		return rendering
