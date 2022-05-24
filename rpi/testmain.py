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

	def jog(self, cmd):
		if self.cycleCount == 0:
			return

		self.cycleCount -= 1
		if self.cycleCount == 0:
			print("reset cc")
			self.jogx = 0
			self.jogy = 0
			self.jogz = 0

		try:
			jog = eval(pcmd)
		except:
			print("unable to parse")
			return

		if len(jog) != 4:
			print("not 4 parameters")
			return

		if self.status not in ["Idle", "Jog"]:
			print("ignoring jog while not in valid state")
			return

		#print("dx = %d, dy = %d, zup = %d, zdown=%d" % (jog[0], jog[1], jog[2], jog[3]))
		if jog[0] != 0 or jog[1] != 0:
			jogxy = False
			if self.jogx != jog[0]:
				self.jogx = jog[0]
				jogxy = True
			if self.jogy != jog[1]:
				self.jogy = jog[1]
				jogxy = True

			if jogxy:
				print("jog x,y %d,%d" % (self.jogx, self.jogy))
				if self.jogx == 0:
					jx = 0
				elif self.jogx > 0:
					jx = 10
				else:
					jx = -10
				if self.jogy == 0:
					jy = 0
				elif self.jogy > 0:
					jy = 10
				else:
					jy = -10

				if self.invertXJog:
					jx = -jx
				if self.invertYJog:
					jy = -jy

				sx = abs(self.jogx)*300;
				sy = abs(self.jogy)*300;

				self.sh.jogxy(jx, jy, max(sx, sy))

				self.jogging = True
				self.cycleCount = 3

		elif jog[2] == 0 or jog[3] == 0:
			if jog[2] == 0:
				jogz = 1
			elif jog[3] == 0:
				jogz = -1
			else:
				jogz = 0

			if self.invertZJog:
				jogz = -jogz

			if jogz != 0:
				if self.jogz != jogz:
					self.jogz = jogz
					print("jog z %d" % self.jogz)
					self.sh.jogz(jogz*10, 300)
					self.jogging = True
					self.cycleCount = 3
			
		elif self.jogging:
			print("stop jogging")
			self.sh.stopJog()
			self.jogging = False
			self.cycleCount = 0
			self.jogx = 0
			self.jogy = 0
			self.jogz = 0


	def run(self):
		self.sh = Shapeoko()
		self.sh.startPoll()

		self.p = Pendant(tty="/dev/ttyACM1")

		self.sh.sendCommand("$G")
		#sh.sendGCodeFile("square.nc")


		while True:
			msg = self.sh.nextAsyncMessage()
			if msg is not None:
				if msg.startswith("<"):
					self.parseStatus(msg)
				else:
					print("Async: (%s)" % str(msg))

			pcmd = self.p.getCommand()
			if pcmd is not None:
				print("Pendant: (%s)" % pcmd)
				#self.jog(pcmd)

grbl = Grbl()
grbl.run()

time.sleep(1)
sh.terminate()
