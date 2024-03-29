from cnc import MT_NORMAL, MT_RAPID
import wx
from wx import glcanvas

from OpenGL.GL import (glViewport, GLfloat, glColor3f, glClearColor, glEnable, GL_DEPTH_TEST, GL_CULL_FACE,
			GL_LIGHTING, GL_LIGHT0, GL_LIGHT1, glLightfv, GL_POSITION, GL_SPECULAR, GL_DIFFUSE,
					   glMaterialf, glMaterialfv, GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, GL_SHININESS,
					   GL_EMISSION, glMatrixMode, GL_PROJECTION, glLoadIdentity, glFrustum, GL_MODELVIEW,
					   glRotatef, glTranslatef, glClear, glColorMaterial, GL_COLOR_MATERIAL,
					   GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glBegin, GL_LINES, GL_TRIANGLES, glColor, glVertex3f, glEnd,
					   glDisable, GL_LINE_STRIP, GL_FLOAT, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY,
					   glEnableClientState, glVertexPointer, glNormalPointer, glDrawArrays)
from OpenGL.GLU import gluLookAt

from tool import Tool

def vec(*args):
	return (GLfloat * len(args))(*args)


	
colors = {
	MT_RAPID:  [0.0, 1.0, 1.0, 1],
	MT_NORMAL: [1.0, 1.0, 1.0, 1]
}
colorsDone = {
	MT_RAPID:  [0.0, 1.0, 0.0, 1],
	MT_NORMAL: [0.0, 0.0, 1.0, 1]
}

colorDoing = [1.0, 0.0, 0.0, 1]
colorTool = [0.93, 0.25, 0.14, 1]

	
class ViewCanvas(glcanvas.GLCanvas):
	def __init__(self, parent, wid=-1, buildarea=(1000, 1000), pos=wx.DefaultPosition,
				 size=(1000, 1000), style=0):
		attribList = (glcanvas.WX_GL_RGBA,  # RGBA
					  glcanvas.WX_GL_DOUBLEBUFFER,  # Double Buffered
					  glcanvas.WX_GL_DEPTH_SIZE, 24)  # 24 bit

		glcanvas.GLCanvas.__init__(self, parent, wid, size=size, style=style, pos=pos, attribList=attribList)
		self.init = False
		self.context = glcanvas.GLContext(self)

		self.gridVertices = None
		self.gridColors = None
		self.dataPoints = []
		self.currentLine = 0

		self.minx = -100
		self.miny = -100
		self.maxx = 100
		self.maxy = 100
		self.midx = 0
		self.midy = 0

		self.tool = Tool()
		self.toolSize = self.tool.getSize()

		# initial mouse position
		self.lastx = self.x = 0
		self.lasty = self.y = 0
		self.anglex = self.angley = self.anglez = 0
		self.transx = self.transy = 0
		self.resetView = True
		self.light0Pos = [0, 50, 150]
		self.light1Pos = [0, -50, 150]
		self.size = None
		
		self.clientwidth = size[0]
		self.drawAxes = True
		self.drawZAxis = False
		self.drawGrid = True
		self.drawTool = False
		self.zoom = 1.0
		self.buildarea = buildarea
		self.adjPt = [x/2 for x in buildarea]
		
		self.setGridArrays()

		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

	def OnEraseBackground(self, event):
		pass # Do nothing, to avoid flashing on MSW.

	def OnSize(self, event):
		size = self.size = self.GetClientSize()
		if self.GetParent().IsShown():
			if self.context is not None:
				self.SetCurrent(self.context)
			glViewport(0, 0, size.width, size.height)
		event.Skip()

	def OnPaint(self, _):
		_ = wx.PaintDC(self)
		if self.IsShown():
			self.SetCurrent(self.context)
			if not self.init:
				self.init = True
				self.InitGL()
			self.OnDraw()

	def OnMouseDown(self, evt):
		self.SetFocus()
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
		
	def OnMouseRightDown(self, evt):
		self.SetFocus()
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

	def OnMouseUp(self, _):
		if self.HasCapture():
			self.ReleaseMouse()

	def OnMouseRightUp(self, _):
		if self.HasCapture():
			self.ReleaseMouse()
		
	def OnMouseDouble(self, _):
		self.resetView = True
		self.setZoom(1.0)
		self.Refresh(False)

	def OnMouseMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			self.lastx, self.lasty = self.x, self.y
			self.x, self.y = evt.GetPosition()
			self.anglex = self.x - self.lastx
			self.angley = self.y - self.lasty
			self.transx = 0
			self.transy = 0
			self.Refresh(False)

		elif evt.Dragging() and evt.RightIsDown():
			self.lastx, self.lasty = self.x, self.y
			self.x, self.y = evt.GetPosition()
			self.anglex = 0
			self.angley = 0
			self.transx = (self.x - self.lastx)*self.zoom/3.0
			self.transy = -(self.y - self.lasty)*self.zoom/3.0
			self.Refresh(False)
		
	def OnWheel(self, evt):
		z = evt.GetWheelRotation()
		if z < 0:
			zoom = self.zoom*0.9
		else:
			zoom = self.zoom*1.1
				
		self.setZoom(zoom)
		self.Refresh(False)
		
	def InitGL(self):
		glClearColor(0.0, 0.0, 0.0, 1)
		glColor3f(1, 0, 0)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_CULL_FACE)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_LIGHT1)

		glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
		glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 0.5, 1))
		glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
		glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
		glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
		glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

		glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
		glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
		glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 80)
		glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(0.1, 0.1, 0.1, 0.9))
		
		glLightfv(GL_LIGHT0, GL_POSITION, vec(0.0, 200.0, 100.0, 1))
		glLightfv(GL_LIGHT1, GL_POSITION, vec(0.0, -200.0, 100.0, 1))
		
	def setDrawAxes(self, flag):
		self.drawAxes = flag
		self.setGridArrays()
		self.Refresh(True)
		
	def setDrawZAxis(self, flag):
		self.drawZAxis = flag
		self.setGridArrays()
		self.Refresh(True)

	def setDrawTool(self, flag):
		self.drawTool = flag
		self.Refresh(True)

	def setDrawGrid(self, flag):
		self.drawGrid = flag
		self.setGridArrays()
		self.Refresh(True)

	def setZoom(self, zoom):
		self.zoom = zoom
				
	def setGridArrays(self):
		self.gridVertices = []
		self.gridColors = []

		if self.drawGrid:
			for x in range(-500, 501, 10):
				if not(self.drawAxes and x == 0):
					self.gridVertices.append([x, -500, 0, x, 500, 0])
					if x % 100 == 0:
						self.gridColors.append([1.0, 1.0, 1.0, 1])
					else:
						self.gridColors.append([0.25, 0.25, 0.25, 1])

			for y in range(-500, 501, 10):
				if not(self.drawAxes and y == 0):
					self.gridVertices.append([-500, y, 0, 500, y, 0])
					if y % 100 == 0:
						self.gridColors.append([1.0, 1.0, 1.0, 1])
					else:
						self.gridColors.append([0.25, 0.25, 0.25, 1])

		if self.drawAxes:		
			self.gridVertices.append([-500, 0, 0, 500, 0, 0])
			self.gridColors.append([1.0, 0.0, 0.0, 1])
			v = -500
			while v <= 500:
				if v % 50 == 0:
					vl = 4
				else:
					vl = 2
				if v != 0:
					self.gridVertices.append([v, -vl, 0, v, vl, 0])
					self.gridColors.append([1.0, 0.0, 0.0, 1])
				v += 10
	
			self.gridVertices.append([0, -500, 0, 0, 500, 0])
			self.gridColors.append([0.0, 1.0, 0.0, 1])
			v = -500
			while v <= 500:
				if v % 50 == 0:
					vl = 4
				else:
					vl = 2
				if v != 0:
					self.gridVertices.append([-vl, v, 0, vl, v, 0])
					self.gridColors.append([0.0, 1.0, 0.0, 1])
				v += 10

		if self.drawAxes and self.drawZAxis:			
			self.gridVertices.append([0, 0, -500, 0, 0, 500])
			self.gridColors.append([0.0, 0.0, 1.0, 1])
			v = -500
			while v <= 500:
				if v % 50 == 0:
					vl = 4
				else:
					vl = 2
				if v != 0:
					self.gridVertices.append([0, -vl, v, 0, vl, v])
					self.gridColors.append([0.0, 0.0, 1.0, 1])
				v += 10
			
			
	def setPoints(self, pts):
		self.dataPoints = pts[:]
		self.minx = 9999
		self.miny = 9999
		self.maxx = -9999
		self.maxy = -9999
		for p in self.dataPoints:
			if p[0] < self.minx:
				self.minx = p[0]
			if p[0] > self.maxx:
				self.maxx = p[0]
			if p[1] < self.miny:
				self.miny = p[1]
			if p[1] > self.maxy:
				self.maxy = p[1]
		self.midx = (self.minx + self.maxx)/2.0
		self.midy = (self.miny + self.maxy)/2.0

		self.resetView = True
		self.setZoom(1.0)
		self.Refresh(True)

	def setPosition(self, p, nx, ny, nz):
		self.currentLine = p
		self.tool.setPosition(nx, ny, nz)
		self.Refresh(True)

	def OnDraw(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glFrustum(-50.0*self.zoom, 50.0*self.zoom, -50.0*self.zoom, 50.0*self.zoom, 200, 800.0)
		#gluLookAt (200.0, -200.0, 400.0, 0.0, 0.0, 0.0, -1.0, 1.0, 0.0)
		distance = 5 * max(self.maxx - self.minx, self.maxy - self.miny)
		if distance > 500:
			distance = 500
		if distance < 200:
			distance = 200
		gluLookAt (self.midx, self.midy-100, distance,    self.midx, self.midy, 0.0,    0.0, 0.0, 1.0)

		glMatrixMode(GL_MODELVIEW)
		if self.resetView:
			glLoadIdentity()
			self.lastx = self.x = 0
			self.lasty = self.y = 0
			self.anglex = self.angley = self.anglez = 0
			self.transx = self.transy = 0
			self.resetView = False
			
		if self.size is None:
			self.size = self.GetClientSize()
		w, h = self.size
		w = max(w, 1.0)
		h = max(h, 1.0)
		xScale = 180.0 / w
		yScale = 180.0 / h
		glRotatef(self.angley * yScale, 1.0, 0.0, 0.0)
		glRotatef(self.anglex * xScale, 0.0, 1.0, 0.0)
		glRotatef(self.anglez, 0.0, 0.0, 1.0)
		glTranslatef(self.transx, self.transy, 0.0)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		glEnable(GL_COLOR_MATERIAL)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_LIGHT1)
		
		if self.drawAxes or self.drawGrid:
			glBegin(GL_LINES)
			for i in range(len(self.gridVertices)):
				glColor(self.gridColors[i])
				p = self.gridVertices[i]
				glVertex3f(p[0], p[1], p[2])
				glVertex3f(p[3], p[4], p[5])
			glEnd()

		currentLineType = MT_RAPID
		currentColor = colors[MT_RAPID]
		glColor(currentColor)
		
		glBegin(GL_LINE_STRIP)
		for p in self.dataPoints:
			currentLineType = p[3]
			if self.currentLine > p[4]:
				nc = colorsDone[currentLineType]
			elif self.currentLine == p[4]:
				nc = colorDoing
			else:
				nc = colors[currentLineType]
			if currentColor != nc:
				currentColor = nc
				glColor(nc)
			glVertex3f(p[0], p[1], p[2])
			
		glEnd()

		if self.drawTool:
			glColor(colorTool)
			self.vertexPositions = self.tool.getVertexPositions()
			self.normalPositions = self.tool.getNormalPositions()
			self.vertexPositions.bind()
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer(3, GL_FLOAT, 0, self.vertexPositions)
			
			self.normalPositions.bind()
			glEnableClientState(GL_NORMAL_ARRAY)
			glNormalPointer(GL_FLOAT, 0, self.normalPositions)

			glDrawArrays(GL_TRIANGLES, 0, self.toolSize)
				
		self.SwapBuffers()
		
		glDisable(GL_LIGHT0)
		glDisable(GL_LIGHT1)
		glDisable(GL_LIGHTING)
			
		self.anglex = self.angley = self.anglez = 0
		self.transx = self.transy = 0
