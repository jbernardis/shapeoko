
class cncObject:
	def __init__(self, parent):
		self.parent = parent
		self.errors = None
		self.reporter = None
		self.params = {}
		
	def getTitle(self):
		return "%s: %s" % (type(self).__name__, self.params["label"])

	def getLabel(self):
		return self.params["label"]

	def setParam(self, tag, value):
		self.params[tag] = value

	def getParam(self, tag):
		if tag not in self.params:
			return None

		return self.params[tag]

	def createErrors(self, elist):
		self.errors = [e for e in elist]
		
	def checkExtents(self, mat, pts):
		t = self.getTitle()
		w = mat.getWidth()
		h = mat.getHeight()
		minx = min([p[0] for p in pts])
		maxx = max([p[0] for p in pts])
		miny = min([p[1] for p in pts])
		maxy = max([p[1] for p in pts])
		dx = maxx - minx
		dy = maxy - miny
		if dx > w:
			self.renderWarning("Object %s delta x is larger than material width (%f > %f)" % (t, dx, w))

		if dy > h:
			self.renderWarning("Object %s delta y is larger than material height (%f > %f)" % (t, dy, h))

		
	def getErrors(self):
		return self.errors

	def renderError(self, s):
		if self.reporter is None:
			print("Render Error: %s" % s)
		else:
			self.reporter.renderError(s)

	def renderWarning(self, s):
		if self.reporter is None:
			print("Render Warning: %s" % s)
		else:
			self.reporter.renderWarning(s)

	def renderInfo(self, s):
		if self.reporter is None:
			print("Render Info: %s" % s)
		else:
			self.reporter.renderInfo(s)
	
	def toJson(self):
		return {type(self).__name__: self.params}
