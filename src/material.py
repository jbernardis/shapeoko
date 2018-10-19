'''
Created on Sep 17, 2018

@author: Jeff
'''
class Material:
	def __init__(self, params):
		self.params = params.copy()
		if "thickness" not in self.params:
			self.params["thickness"] = 1.0
		if "width" not in self.params:
			self.params["width"] = 100.0
		if "height" not in self.params:
			self.params["height"] = 100.0
			
	def setDimensions(self, thickness=None, width=None, height=None):
		if thickness:
			self.params["thickness"] = thickness
			
		if width:
			self.params["width"] = width
			
		if height:
			self.params["height"] = height
			
	def getThickness(self):
		return self.params["thickness"]
			
	def setThickness(self, thickness):
		self.params["thickness"] = thickness
			
	def getWidth(self):
		return self.params["width"]
			
	def setWidth(self, width):
		self.params["width"] = width
			
	def getHeight(self):
		return self.params["height"]
			
	def setHeight(self, height):
		self.params["height"] = height
	
	def toJson(self):
		return {type(self).__name__: self.params}

