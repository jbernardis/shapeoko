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
		self.feedspeed = 0
		self.spindlespeed = 0
		self.feedov = 100
		self.rapidov = 100
		self.spindleov = 100

		self.isRunning = False
		self.endOfLife = False

		self.versionString = ""
		self.config = {}
		for k in Settings.keys():
			self.config[k] = None

		self.cbStatusHandlers = []
		self.cbPositionHandlers = []
		self.cbParserStateHandlers = []
		self.cbAlarmHandlers = []
		self.cbProbeHandlers = []
		self.cbSpeedHandlers = []
		self.cbErrorHandlers = []
		self.cbMessageHandlers = []
		self.cbConfigHandlers = []
		self.cbOverrideHandlers = []

		self.shapeokoserver = None

		try:
			self.grbl = Grbl(tty=self.settings.ttyshapeoko, pollInterval=self.settings.pollinterval)
		except:
			print("unable to connect to GRBL - exiting")
			self.parent.requestClose(shutdown=False)
			return
			
		self.grbl.startPoll()

		try:
			self.pendant = Pendant(tty=self.settings.ttypendant)
		except:
			self.pendant = None  # allow operation without pendant
		
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
		if cfg.startswith("$"):
			cx, val = cfg[1:].split("=", 1)
			try:
				icx = int(cx)
			except:
				icx = None
			if icx is not None and icx in Settings.keys():
				self.config[icx] = val
		else:
			l = cfg.split()
			self.versionString = "%s %s" % (l[0], l[1])

		for cb in self.cbConfigHandlers:
			cb(cfg)

	def registerPositionHandler(self, cbPositionHandler):
		self.cbPositionHandlers.append(cbPositionHandler)

	def sendPosition(self, position, offset):
		for cb in self.cbPositionHandlers:
			cb(position, offset)

	def registerSpeedHandler(self, cbSpeedHandler):
		self.cbSpeedHandlers.append(cbSpeedHandler)

	def sendSpeeds(self, feed, spindle):
		for cb in self.cbSpeedHandlers:
			cb(feed, spindle)

	def registerOverrideHandler(self, cbOverrideHandler):
		self.cbOverrideHandlers.append(cbOverrideHandler)

	def sendOverrides(self, feed, rapid, spindle):
		for cb in self.cbOverrideHandlers:
			cb(feed, rapid, spindle)

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

	def registerProbeHandler(self, cbProbeHandler):
		self.cbProbeHandlers.append(cbProbeHandler)

	def sendProbe(self, msg):
		for cb in self.cbProbeHandlers:
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
		spdChanged = False
		ovChanged = False
		nf = None
		ns = None
		ovf = None
		ovr = None
		ovs = None
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

			elif term.startswith("FS:"):
				spdterm = term[3:].replace(">", "")
				newspd = spdterm.split(",")
				if len(newspd) == 2:
					nf = float(newspd[0])
					ns = float(newspd[1])
					if self.feedspeed != nf:
						self.feedspeed = nf
						spdChanged = True
					else:
						nf = None

					if self.spindlespeed != ns:
						self.spindlespeed = ns
						spdChanged = True
					else:
						ns = None

			elif term.startswith("Ov:"):
				ovterm = term[3:].replace(">", "")
				newov = ovterm.split(",")
				if len(newov) == 3:
					ovf = float(newov[0])
					ovr = float(newov[1])
					ovs = float(newov[2])
					if self.feedov != ovf:
						self.feedov = ovf
						ovChanged = True
					else:
						ovf = None

					if self.rapidov != ovr:
						self.rapidov = ovr
						ovChanged = True
					else:
						ovr = None

					if self.spindleov != ovs:
						self.spindleov = ovs
						ovChanged = True
					else:
						ovs = None

		if posChanged:
			self.sendPosition({ XAXIS: self.x, YAXIS: self.y, ZAXIS: self.z }, { XAXIS: self.offx, YAXIS: self.offy, ZAXIS: self.offz })

		if spdChanged:
			self.sendSpeeds(nf, ns)

		if ovChanged:
			print("sending overrides")
			self.sendOverrides(ovf, ovr, ovs)

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

	def spindleOn(self):
		return self.grbl.spindleOn()

	def spindleOff(self):
		return self.grbl.spindleOff()

	def setSpindleSpeed(self, speed):
		return self.grbl.setSpindleSpeed(speed)

	def adjustSpindleSpeed(self, inc):
		return self.grbl.adjustSpindleSpeed(inc)

	def adjustFeedRate(self, inc):
		return self.grbl.adjustFeedRate(inc)

	def adjustRapidRate(self, inc):
		return self.grbl.adjustRapidRate(inc)	

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

	def gotoHome(self):
		return self.grbl.gotoHome()

	def probe(self):
		self.grbl.probe()

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
			verb = cmd["__cmd"][0]
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
				if k in [ "__cmd" ]:
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

		elif verb == "command":
			badKeys = []
			for k in cmd.keys():
				if k in ["__cmd", "cmd"]:
					continue
				badKeys.append(k)

			if len(badKeys) > 0:
				self.HttpRespQ.put((400, "Invalid paremeter(s): %s" ", ".join(badKeys)))
			else:
				if "cmd" in cmd.keys():
					cmdString = cmd["cmd"][0]
					self.grbl.sendCommand(cmdString)
					self.HttpRespQ.put((200, "Command '%s' queued" % cmdString))
				else:
					self.HttpRespQ.put((400, "Missing 'cmd' parameter"))

		elif verb == "getjob":
			resp = self.parent.getJobInfo()
			resp["mpos"] = [self.x, self.y, self.z]
			resp["wco"] = [self.offx, self.offy, self.offz]
			respstr = str(resp)
			self.HttpRespQ.put((200, respstr.encode()))

		elif verb == "exit":
			self.parent.requestClose(shutdown=False)
			resp = "exit requested"
			self.HttpRespQ.put((200, resp.encode()))

		elif verb == "shutdown":
			self.parent.requestClose(shutdown=True)
			resp = "shutdown requested"
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
					if msg["status"] == "ok":
						self.sendMessage("%s (ok)" % msg["data"], verbose=True)

					elif msg["status"] == "<missing>":
						self.sendMessage("%s (ok not received)" % msg["data"], verbose=True)

					else:
						self.sendError(msg["status"], msg["data"])

				elif msg["type"] == "feedback":
					fb = msg["data"]
					self.sendMessage("[MSG: %s]" % fb)
					self.parent.showFeedback(fb.replace("$H", "Home").replace("$X", "Clear Alarm"))

				elif msg["type"] == "alarm":
					self.sendAlarm(msg["data"])

				elif msg["type"] == "probe":
					self.sendProbe(msg["data"])
					self.sendMessage(msg["data"])

				elif msg["type"] == "abort":
					self.sendMessage("File aborted: (%s)" % msg["file"])

				elif msg["type"] == "eof":
					self.sendMessage("File (%s) processing successfully completed" % msg["file"])

				elif msg["type"] == "message":
					self.sendMessage(msg["data"])

				else:
					self.sendMessage("Unknown Message Type: (%s)" % str(msg))

			if self.pendant is not None:
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

