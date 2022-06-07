import time
import threading

from shapeoko import Shapeoko
from pendant import Pendant

from common import XAXIS, YAXIS, ZAXIS

# <Run|MPos:91.863,0.000,-2.000|FS:330,0|Ov:100,100,100>
class Grbl(threading.Thread):
	def __init__(self, ttyShapeoko, ttyPendant):
		threading.Thread.__init__(self)
		self.status = None
		self.x = None
		self.y = None
		self.z = None
		self.offx = None
		self.offy = None
		self.offz = None
		self.jogx = 0
		self.jogy = 0
		self.jogz = 0
		self.jogging = False
		self.cycleCount = 0
		self.invertXJog = False
		self.inveryYJog = True
		self.invertZJog = False

		self.running = False
		self.endOfLife = False

		self.cbNewStatus = None
		self.cbNewPosition = None

		self.shapeoko = Shapeoko(tty=ttyShapeoko)
		self.shapeoko.startPoll()

		self.pendant = Pendant(tty=ttyPendant)

	def go(self):
		self.start()

	def registerNewStatus(self, cbNewStatus):
		self.cbNewStatus = cbNewStatus

	def registerNewPosition(self, cbNewPosition):
		self.cbNewPosition = cbNewPosition

	def parseStatus(self, msg):
		terms = msg.split("|")
		ns = terms[0][1:]
		if ns != self.status:
			self.status = ns
			if callable(self.cbNewStatus):
				self.cbNewStatus(self.status)

		posChanged = False
		for term in terms[1:]:
			if term.startswith("MPos:"):
				posterm = term[5:].replace(">", "")
				newpos = posterm.split(",")
				if len(newpos) == 3:
					nx = float(newpos[0])
					ny = float(newpos[1])
					nz = float(newpos[2])
					if self.x != nx:
						self.x = nx
						posChanged = True
						#print("new x: %f" % nx)
					if self.y != ny:
						self.y = ny
						posChanged = True
						#print("new y: %f" % ny)
					if self.z != nz:
						self.z = nz
						posChanged = True
						#print("new z: %f" % nz)
				else:
					print("invalid MPos term (%s)" % term)

			elif term.startswith("WPos:"):
				posterm = term[5:].replace(">", "")
				newpos = posterm.split(",")
				if len(newpos) == 3:
					nx = float(newpos[0])
					ny = float(newpos[1])
					nz = float(newpos[2])
					if self.x != nx - self.offx:
						self.x = nx - self.offx
						posChanged = True
						#print("new WC x: %f, MP: %f" % (nx, self.x))
					if self.y != ny - self.offy:
						self.y = ny - self.offy
						posChanged = True
						#print("new WC y: %f, MP: %f" % (ny, self.y))
					if self.z != nz - self.offz:
						self.z = nz - self.offz
						posChanged = True
						#print("new WC z: %f, MP: %f" % (nz, self.z))
				else:
					print("invalid MPos term (%s)" % term)

			elif term.startswith("WCO:"):
				posterm = term[4:].replace(">", "")
				newpos = posterm.split(",")
				if len(newpos) == 3:
					nx = float(newpos[0])
					ny = float(newpos[1])
					nz = float(newpos[2])
					if self.offx != nx:
						self.offx = nx
						posChanged = True
						#print("new offx: %f" % nx)
					if self.offy != ny:
						self.offy = ny
						posChanged = True
						#print("new offy: %f" % ny)
					if self.offz != nz:
						self.offz = nz
						posChanged = True
					#print("new offz: %f" % nz)
				else:
					print("invalid WCO term (%s)" % term)

		if posChanged:
			if callable(self.cbNewPosition):
				self.cbNewPosition({ XAXIS: self.x, YAXIS: self.y, ZAXIS: self.z }, { XAXIS: self.offx, YAXIS: self.offy, ZAXIS: self.offz })

	def getDistance(self, dx):
		if dx < 0:
			sign = -1
			dx = -dx
		else:
			sign = 1
		if dx == 4:
			return sign*1000.0
		elif dx == 3:
			return sign*10.0
		elif dx == 2:
			return sign*1.0
		elif dx == 1:
			return sign*0.1
		return 0

	def jog(self, cmd):
		terms = cmd.split(" ")
		if len(terms) == 2:
			if terms[1] == "STOP":
				self.shapeoko.stopJog()

		elif len(terms) == 3:
			axis = terms[1]
			distance = int(terms[2])
			if axis == "X":
				self.shapeoko.jogxy(self.getDistance(distance), None, 800)
			elif axis == "Y":
				self.shapeoko.jogxy(None, self.getDistance(distance), 800)
			elif axis == "Z":
				self.shapeoko.jogz(self.getDistance(distance), 800)

	def kill(self):
		self.isRunning = False

	def run(self):
		self.isRunning = True
		while self.isRunning:
			msg = self.shapeoko.nextAsyncMessage()
			if msg is not None:
				if msg["data"].startswith("<"):
					self.parseStatus(msg["data"])
				else:
					print("Async: (%s)" % str(msg))

			pcmd = self.pendant.getCommand()
			if pcmd is not None:
				print("Pendant: (%s)" % pcmd)
				if pcmd.startswith("JOG "):
					self.jog(pcmd)
				elif pcmd.startswith("RESET "):
					axis = pcmd.split(" ")[1]
					if axis == "X":
						self.shapeoko.resetAxis(0, None, None);
					elif axis == "Y":
						self.shapeoko.resetAxis(None, 0, None);
					elif axis == "Z":
						self.shapeoko.resetAxis(None, None, 0);

		self.endOfLife = True

	def terminate(self):
		if self.shapeoko is not None:
			self.shapeoko.terminate()

		self.kill()
		while not self.endOfLife:
			time.sleep(0.1)
