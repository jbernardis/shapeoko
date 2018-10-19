class Model:
	def __init__(self, params={}):
		self.params = params.copy()
		self.objectList = []

	def addObject(self, obj):
		self.objectList.append(obj)

	def getObjectList(self):
		return self.objectList
	
	def render(self, cnc, reporter, addPreamble=True):
		rendering = []
		if addPreamble:
			rendering.extend(cnc.preamble())

		for o in self.objectList:
			ro = o.render(cnc, reporter)
			reporter.renderInfo("%s rendered as %d lines of G Code" % (o.getTitle(), len(ro)))
			rendering.extend(ro)

		return rendering