import time
import threading

from grbl import Grbl
from pendant import Pendant

from common import XAXIS, YAXIS, ZAXIS

# <Run|MPos:91.863,0.000,-2.000|FS:330,0|Ov:100,100,100>
class Shapeoko(threading.Thread):
	def __init__(self, settings):
		threading.Thread.__init__(self)
		self.settings = settings
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

		self.cbNewStatus = []
		self.cbNewPosition = []

		self.grbl = Grbl(tty=self.settings.ttyshapeoko, pollInterval=self.settings.pollinterval)
		self.grbl.startPoll()

		self.pendant = Pendant(tty=self.settings.ttypendant)

	def go(self):
		self.start()

	def getPosition(self):
		return self.grbl.getPosition()

	def registerNewStatus(self, cbNewStatus):
		self.cbNewStatus.append(cbNewStatus)

	def registerNewPosition(self, cbNewPosition):
		self.cbNewPosition.append(cbNewPosition)

	def parseStatus(self, msg):
		terms = msg.split("|")
		ns = terms[0][1:]
		if ns != self.status:
			self.status = ns
			for cb in self.cbNewStatus:
				cb(self.status)

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
					if self.y != ny:
						self.y = ny
						posChanged = True
					if self.z != nz:
						self.z = nz
						posChanged = True
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
					if self.y != ny - self.offy:
						self.y = ny - self.offy
						posChanged = True
					if self.z != nz - self.offz:
						self.z = nz - self.offz
						posChanged = True
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
					if self.offy != ny:
						self.offy = ny
						posChanged = True
					if self.offz != nz:
						self.offz = nz
						posChanged = True
				else:
					print("invalid WCO term (%s)" % term)

		if posChanged:
			for cb in self.cbNewPosition:
				cb({ XAXIS: self.x, YAXIS: self.y, ZAXIS: self.z }, { XAXIS: self.offx, YAXIS: self.offy, ZAXIS: self.offz })

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

	def sendGCodeFile(self, fn):
		return self.grbl.sendGCodeFile(fn)

	def sendGcodeLines(self, lines):
		return self.grbl.sendGCodeLines(lines)

	def holdFeed(self):
		return self.grbl.holdFeed()

	def resume(self):
		return self.grbl.resume()

	def softReset(self):
		return self.grbl.softReset()

	def getParserState(self):
		return self.grbl.getParserState()

	def jog(self, cmd):
		terms = cmd.split(" ")
		if len(terms) == 2:
			if terms[1] == "STOP":
				self.grbl.stopJog()

		elif len(terms) == 3:
			axis = terms[1]
			distance = int(terms[2])
			if axis == "X":
				self.grbl.jogxy(self.getDistance(distance), None, 800)
			elif axis == "Y":
				self.grbl.jogxy(None, self.getDistance(distance), 800)
			elif axis == "Z":
				self.grbl.jogz(self.getDistance(distance), 800)

	def kill(self):
		self.isRunning = False

	def run(self):
		self.isRunning = True
		while self.isRunning:
			msg = self.grbl.nextAsyncMessage()
			if msg is not None:
				if msg["data"].startswith("<"):
					#print("status")
					self.parseStatus(msg["data"])
				else:
					print("Async: (%s)" % str(msg))

			pcmd = self.pendant.getCommand()
			if pcmd is not None:
				if self.status.lower() not in ["jog", "idle"]:
					print("ignoring pendant commands when in %s state" % self.status)
				else:
					print("Pendant: (%s)" % pcmd)
					if pcmd.startswith("JOG "):
						self.jog(pcmd)
					elif pcmd.startswith("RESET "):
						axis = pcmd.split(" ")[1]
						if axis == "X":
							self.grbl.resetAxis(0, None, None);
						elif axis == "Y":
							self.grbl.resetAxis(None, 0, None);
						elif axis == "Z":
							self.grbl.resetAxis(None, None, 0);
			time.sleep(0.01)

		self.endOfLife = True

	def terminate(self):
		self.kill()
		while not self.endOfLife:
			time.sleep(0.1)

		if self.grbl is not None:
			self.grbl.terminate()

