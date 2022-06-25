import time
import threading
import queue
import socket   

from grbl import Grbl
from pendant import Pendant
from httpserver import ShapeokoHTTPServer

from common import XAXIS, YAXIS, ZAXIS, Settings

# <Run|MPos:91.863,0.000,-2.000|FS:330,0|Ov:100,100,100>
class Shapeoko(threading.Thread):
	def __init__(self, parent, settings):
		threading.Thread.__init__(self)

		self.parent = parent
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

		self.isRunning = False
		self.endOfLife = False

		self.cbStatusHandlers = []
		self.cbPositionHandlers = []
		self.cbParserStateHandlers = []
		self.cbAlarmHandlers = []
		self.cbErrorHandlers = []
		self.cbMessageHandlers = []
		self.cbConfigHandlers = []

		self.shapeokoserver = None

		self.grbl = Grbl(tty=self.settings.ttyshapeoko, pollInterval=self.settings.pollinterval)
		self.grbl.startPoll()

		self.pendant = Pendant(tty=self.settings.ttypendant)
		self.config = {}
		for k in Settings.keys():
			self.config[k] = None
		
		self.startHttpServer(self.settings.ipaddr, self.settings.port)

	def go(self):
		self.start()

	def getPosition(self):
		return self.grbl.getPosition()

	def registerStatusHandler(self, cbStatusHandler):
		self.cbStatusHandlers.append(cbStatusHandler)

	def sendStatus(self, stat):
		for cb in self.cbStatusHandlers:
			cb(stat)

	def registerConfigHandler(self, cbConfigHandler):
		self.cbConfigHandlers.append(cbConfigHandler)

	def sendConfigData(self, cfg):
		# record the configuration locally
		cx, val = cfg[1:].split("=", 1)
		try:
			icx = int(cx)
		except:
			icx = None
		if icx is not None and icx in Settings.keys():
			self.config[icx] = val

		for cb in self.cbConfigHandlers:
			cb(cfg)

	def registerPositionHandler(self, cbPositionHandler):
		self.cbPositionHandlers.append(cbPositionHandler)

	def sendPosition(self, position, offset):
		for cb in self.cbPositionHandlers:
			cb(position, offset)

	def registerParserStateHandler(self, cbParserStateHandler):
		self.cbParserStateHandlers.append(cbParserStateHandler)

	def sendParserState(self, parserState):
		pstate = parserState[4:-1]
		for cb in self.cbParserStateHandlers:
			cb(pstate)

	def registerAlarmHandler(self, cbAlarmHandler):
		self.cbAlarmHandlers.append(cbAlarmHandler)

	def sendAlarm(self, msg):
		for cb in self.cbAlarmHandlers:
			cb(msg)

	def registerErrorHandler(self, cbErrorHandler):
		self.cbErrorHandlers.append(cbErrorHandler)

	def sendError(self, status, msg):
		for cb in self.cbErrorHandlers:
			cb(status, msg)

	def registerMessageHandler(self, cbMessageHandler):
		self.cbMessageHandlers.append(cbMessageHandler)

	def sendMessage(self, msg, verbose=False, status=False):
		for cb in self.cbMessageHandlers:
			cb(msg, verbose=verbose, status=status)

	def parseStatus(self, msg):
		terms = msg.split("|")
		ns = terms[0][1:].split(":")[0]
		if ns != self.status:
			self.status = ns
			self.sendStatus(self.status)

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

		if posChanged:
			self.sendPosition({ XAXIS: self.x, YAXIS: self.y, ZAXIS: self.z }, { XAXIS: self.offx, YAXIS: self.offy, ZAXIS: self.offz })

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

	def getConfig(self):
		return self.grbl.getConfig()

	def clearAlarm(self):
		return self.grbl.clearAlarm()

	def checkMode(self):
		return self.grbl.checkMode()

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

	def resetAxis(self, x=None, y=None, z=None):
		return self.grbl.resetAxis(x, y, z)

	def goto(self, x=None, y=None, z=None):
		return self.grbl.goto(x, y, z)

	def startHttpServer(self, ip, port):
		self.HttpCmdQ = queue.Queue(0)
		self.HttpRespQ = queue.Queue(0)
		self.serving = True
		self.shapeokoserver = ShapeokoHTTPServer(ip, port, self.HttpCmdQ, self.HttpRespQ)

	def HTTPProcess(self):
		if self.HttpCmdQ.empty():
			return

		try:
			cmd = self.HttpCmdQ.get(False)
		except queue.Empty:
			return

		if cmd is None:
			return

		try:
			verb = cmd["cmd"][0]
		except KeyError:
			self.HttpRespQ.put((400, b'missing verb'))
			return
		except:
			self.HttpRespQ.put((400, b'unexpected error retrieving command'))
			return

		if verb == "getcfg":
			resp = str(self.config)
			self.HttpRespQ.put((200, resp.encode()))
		elif verb == "setcfg":
			errKeys = []
			cmds = []
			for k in cmd.keys():
				if k in [ "cmd" ]:
					continue
				try:
					ik = int(k)
				except:
					ik = None
				if ik is None or ik not in Settings.keys():
					errKeys.append(k)
					continue

				cmds.append("$%s=%s" % (k, cmd[k][0]))

			if len(errKeys) > 0:
				resp = "action(s) not performed due to badkeys: (" + ", ".join([str(x) for x in errKeys]) + ")"
				self.HttpRespQ.put((200, resp.encode()))
			else:
				if len(cmds) > 0:
					for c in cmds:
						self.grbl.sendCommand(c)
					self.grbl.getConfig()
				resp = "%d action(s) performed" % len(cmds)
				self.HttpRespQ.put((400, resp.encode()))
		elif verb == "getjob":
			resp = self.parent.getJobInfo()
			self.HttpRespQ.put((200, resp.encode()))
		elif verb == "exit":
			self.parent.requestClose(shutdown=False)
			resp = "exit pending"
			self.HttpRespQ.put((200, resp.encode()))
		elif verb == "shutdown":
			self.parent.requestClose(shutdown=True)
			resp = "shutdown pending"
			self.HttpRespQ.put((200, resp.encode()))
		else:
			msg = "Unknown command: %s" % cmd
			self.HttpRespQ.put((400, msg.encode()))


	def run(self):
		self.isRunning = True
		while self.isRunning:
			self.HTTPProcess()

			msg = self.grbl.nextAsyncMessage()
			if msg is not None:
				if msg["type"] == "status":
					self.sendMessage(msg["data"], verbose=True, status=True)
					self.parseStatus(msg["data"])

				elif msg["type"] == "config":
					self.sendMessage(msg["data"])
					self.sendConfigData(msg["data"])

				elif msg["type"] == "parserstate":
					self.sendMessage(msg["data"])
					self.sendParserState(msg["data"])

				elif msg["type"] == "response":
					if msg["status"] != "ok":
						self.sendError(msg["status"], msg["data"])

					else:
						self.sendMessage("%s (ok)" % msg["data"], verbose=True)

				elif msg["type"] == "alarm":
					self.sendAlarm(msg["data"])

				elif msg["type"] == "abort":
					self.sendMessage("File aborted: (%s)" % msg["file"])

				elif msg["type"] == "eof":
					self.sendMessage("File (%s) processing successfully completed" % msg["file"])

				elif msg["type"] == "message":
					self.sendMessage(msg["data"])

				else:
					self.sendMessage("Unknown Message Type: (%s)" % str(msg))

			pcmd = self.pendant.getCommand()
			if pcmd is not None:
				if self.status.lower() not in ["jog", "idle", "check"]:
					self.sendMessage("Ignoring pendant commands when in %s state" % self.status)
				else:
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

		if self.shapeokoserver is not None:
			self.shapeokoserver.close()

