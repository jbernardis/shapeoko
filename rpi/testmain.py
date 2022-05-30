import time

from shapeoko import Shapeoko
from pendant import Pendant

# <Run|MPos:91.863,0.000,-2.000|FS:330,0|Ov:100,100,100>
class Grbl:
	def __init__(self):
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

	def parseStatus(self, msg):
		terms = msg.split("|")
		ns = terms[0][1:]
		if ns != self.status:
			self.status = ns
			print("new status = (%s)" % self.status)

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
						#print("new x: %f" % nx)
					if self.y != ny:
						self.y = ny
						#print("new y: %f" % ny)
					if self.z != nz:
						self.z = nz
						#print("new z: %f" % nz)
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
						#print("new offx: %f" % nx)
					if self.offy != ny:
						self.offy = ny
						#print("new offy: %f" % ny)
					if self.offz != nz:
						self.offz = nz
						#print("new offz: %f" % nz)
				else:
					print("invalid WCO term (%s)" % term)

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
				self.sh.stopJog()

		elif len(terms) == 3:
			axis = terms[1]
			distance = int(terms[2])
			if axis == "X":
				self.sh.jogxy(self.getDistance(distance), None, 800)
			elif axis == "Y":
				self.sh.jogxy(None, self.getDistance(distance), 800)
			elif axis == "Z":
				self.sh.jogz(self.getDistance(distance), 800)


	def run(self):
		self.sh = Shapeoko()
		self.sh.startPoll()

		self.p = Pendant(tty="/dev/ttyACM1")

		self.sh.sendCommand("$G")
		#sh.sendGCodeFile("square.nc")


		while True:
			msg = self.sh.nextAsyncMessage()
			if msg is not None:
				if msg["data"].startswith("<"):
					self.parseStatus(msg["data"])
				else:
					print("Async: (%s)" % str(msg))

			pcmd = self.p.getCommand()
			if pcmd is not None:
				print("Pendant: (%s)" % pcmd)
				if pcmd.startswith("JOG "):
					self.jog(pcmd)
				elif pcmd.startswith("RESET "):
					axis = pcmd.split(" ")[1]
					if axis == "X":
						self.sh.resetAxis(0, None, None);
					elif axis == "Y":
						self.sh.resetAxis(None, 0, None);
					elif axis == "Z":
						self.sh.resetAxis(None, None, 0);
				else:
					print("skipping for now");

grbl = Grbl()
grbl.run()

time.sleep(1)
sh.terminate()
