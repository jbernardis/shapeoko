import json

class Shapeoko:
	def __init__(self):
		self.modified = False

		self.tool = None
		self.toolName = ""
		self.offX = 0.0
		self.offY = 0.0
		self.offZ = 0.0

		self.material = None

		self.fmt = None
		self.speedTerm = None

		# TODO: CNC/Shapeoko parameters - save to/load from alternate files, etc, set as default
		fn = "shapeoko.json"
		try:
			with open(fn, 'r') as f:
				self.params = json.load(f)

		except IOError:
			print("Cannot read from shapeoko json file '%s'." % fn)
			self.params = {}

		if "safez" not in self.params:
			self.params["safez"] = 10.0

		if "metric" not in self.params:
			self.params["metric"] = True

		if "xyMoveSpeed" not in self.params:
			self.params["xyMoveSpeed"] = 140

		if "xyCutSpeed" not in self.params:
			self.params["xyCutSpeed"] = 70

		if "zMoveSpeed" not in self.params:
			self.params["zMoveSpeed"] = 140

		if "zCutSpeed" not in self.params:
			self.params["zCutSpeed"] = 70

		if "passDepth" not in self.params:
			self.params["passDepth"] = 0.5

		self.commentCode = True
		self.addSpeed = True
		self.decimalPlaces = 4
		self.zMoveSpeed = self.params["zMoveSpeed"]
		self.zCutSpeed = self.params["zCutSpeed"]
		self.xyMoveSpeed = self.params["xyMoveSpeed"]
		self.xyCutSpeed = self.params["xyCutSpeed"]

		self.preambleAdded = False
		self.setFormatters()
		
	def setOptions(self, commentCode=None, addSpeed=None, decimalPlaces=None):
		if commentCode is not None:
			self.commentCode = commentCode
			
		if addSpeed is not None:
			self.addSpeed = addSpeed
			
		if decimalPlaces is not None:
			self.decimalPlaces = decimalPlaces
		
	def setModified(self, flag=True):
		self.modified = flag

	def setParam(self, tag, value):
		self.params[tag] = value
		self.setModified()
		self.zMoveSpeed = self.params["zMoveSpeed"]
		self.zCutSpeed = self.params["zCutSpeed"]
		self.xyMoveSpeed = self.params["xyMoveSpeed"]
		self.xyCutSpeed = self.params["xyCutSpeed"]

		self.setFormatters()

	def getParameters(self):
		order = ["safez", "metric", "xyMoveSpeed", "xyCutSpeed", "zMoveSpeed", "zCutSpeed", "passDepth"]
		props = {
			"safez": { "label": "Safe Z", "dataType": "float", "value": self.params["safez"]},
			"metric": {"label": "Metric", "dataType": "bool", "value": self.params["metric"]},
			"xyMoveSpeed": {"label": "XY Move Speed", "dataType": "float", "value": self.params["xyMoveSpeed"]},
			"xyCutSpeed": {"label": "XY Cutting Speed", "dataType": "float", "value": self.params["xyCutSpeed"]},
			"zMoveSpeed": {"label": "Z Move Speed", "dataType": "float", "value": self.params["zMoveSpeed"]},
			"zCutSpeed": {"label": "Z Cut Speed", "dataType": "float", "value": self.params["zCutSpeed"]},
			"passDepth": {"label": "Pass Depth", "dataType": "float", "value": self.params["passDepth"]}
		}

		return props, order

	def setFormatters(self):
		self.fmt = "%0." + str(self.decimalPlaces) + "f"
		self.speedTerm = lambda x: (" F%%0.%df" % self.decimalPlaces) % x if self.addSpeed else ""

	def setTool(self, tool):
		self.tool = tool
		self.toolName = tool["name"]

	def getToolDiameter(self):
		if self.tool is None:
			print("Tool not selected")
			return 0.0

		try:
			return float(self.tool["diameter"])
		except KeyError:
			return 0.0

	def getStepOver(self):
		if self.tool is None:
			print("Tool not selected")
			return 0.0

		try:
			return float(self.tool["stepover"])
		except KeyError:
			return 0.75
		except ValueError:
			return 0.75

	def setMaterial(self, material):
		self.material = material
		
	def getMaterial(self):
		return self.material

	def getSafeZ(self):
		return self.params["safez"]

	def getPassDepth(self):
		return self.params["passDepth"]

	def comment(self, s):
		if not self.commentCode:
			return []
		return ["; %s" % s]

	def toolInfo(self):
		if self.tool is None or not self.commentCode:
			return []
		return ["; Selected tool: %s" % self.tool["name"], "; diameter: %f  stepover: %f" % (self.tool["diameter"], self.tool["stepover"])]
	
	def setOffset(self, x=None, y=None, z=None):
		if x:
			self.offX = x
			
		if y:
			self.offY = y
			
		if z:
			self.offZ = z
			
	def moveZ(self, z):
		return [("G0 Z"+self.fmt+self.speedTerm(self.zMoveSpeed)) % (z+self.offZ)]

	def cutZ(self, z):
		return [("G1 Z"+self.fmt+self.speedTerm(self.zCutSpeed)) % (z + self.offZ)]

	def moveXY(self, xy):
		x = xy[0]
		y = xy[1]
		if x is None and y is None:
			print("Must specify at least one of x or y for moveXY")
			return []

		if x is None:
			return [("G0 Y"+self.fmt+self.speedTerm(self.xyMoveSpeed)) % (y+self.offY)]
		elif y is None:
			return [("G0 X"+self.fmt+self.speedTerm(self.xyMoveSpeed)) % (x+self.offX)]
		else:
			return [("G0 X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.xyMoveSpeed)) % (x+self.offX, y+self.offY)]

	def cutXY(self, xy):
		x = xy[0]
		y = xy[1]
		if x is None and y is None:
			print("Must specify at least one of x or y for cutXY")
			return []

		if x is None:
			return [("G1 Y" + self.fmt + self.speedTerm(self.xyCutSpeed)) % (y+self.offY)]
		elif y is None:
			return [("G1 X" + self.fmt + self.speedTerm(self.xyCutSpeed)) % (x+self.offX)]
		else:
			return [("G1 X" + self.fmt + " Y" + self.fmt + self.speedTerm(self.xyCutSpeed)) % (x+self.offX, y+self.offY)]

	def cutArcCw(self, x, y, dx=None, dy=None):
		return self.__cutArc("G2", x+self.offX, y+self.offY, dx, dy)

	def cutArcCcw(self, x, y, dx=None, dy=None):
		return self.__cutArc("G3", x+self.offX, y+self.offY, dx, dy)

	def __cutArc(self, cmd, x, y, dx, dy): 
		if dx is None and dy is None:
			print("Must specify at least one of dx or dy for arc")
			return []

		if dx is None:
			return [("%s J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.xyCutSpeed)) % (cmd, dy, x, y)]
		elif dy is None:
			return [("%s I"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.xyCutSpeed)) % (cmd, dx, x, y)]
		else:
			return [("%s I"+self.fmt+" J"+self.fmt+" X"+self.fmt+" Y"+self.fmt+self.speedTerm(self.xyCutSpeed)) % (cmd, dx, dy, x, y)]

	def preamble(self):
		if self.preambleAdded:
			return []

		self.preambleAdded = True
		result = []

		if self.commentCode:
			if self.params["metric"]:
				result.append("; using metric")
			else:
				result.append("; using imperial")
			if self.addSpeed:
				result.append("; move speeds: XY:%f  Z:%f" % (self.xyMoveSpeed, self.zMoveSpeed))
				result.append(";  cut speeds: XY:%f  Z:%f" % (self.xyCutSpeed, self.zCutSpeed))
			else:
				result.append("; using default speeds")

			result.append("; safe Z height: %f" % self.params["safez"])
			result.append("; pass depth: %f" % self.params["passDepth"])
			result.append(";")
			if self.material is None:
				result.append("; material not specified")
			else:
				result.append("; Material: Thickness: %f  Width: %f  Height: %f" %
							  (self.material.getThickness(), self.material.getWidth(), self.material.getHeight()))
			result.append(";")

		result.append("G90")
		if self.params["metric"]:
			result.append("G21")
		else:
			result.append("G20")

		return result
