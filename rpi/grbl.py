from serial import Serial
import threading
import queue
import time

class RepeatTimer(threading.Thread):
	def __init__(self, event, interval, function):
		threading.Thread.__init__(self)
		self.interval = interval
		self.stopped = event
		self.function = function

	def run(self):
		while not self.stopped.wait(self.interval):
			self.function()

class SendThread(threading.Thread):
	def __init__(self, port, immedQ, commandQ, gcodeQ, responseQ, asyncQ):
		super(SendThread,self).__init__()
		self.port = port
		self.immedQ = immedQ
		self.commandQ = commandQ
		self.gcodeQ = gcodeQ		
		self.responseQ = responseQ
		self.asyncQ = asyncQ	
		self.isRunning = False
		self.endOfLife = False
		self.lineCt = 0
		self.waitOK = None
		self.sequence = 0
		self.inFile = False

		self.start()
	
	def kill(self):
		self.isRunning = False

	def isKilled(self):
		return self.endOfLife

	def run(self):
		self.isRunning = True
		self.waitOK = None
		while self.isRunning:
			while not self.immedQ.empty():
				string = self.immedQ.get(False)
				self.sendMessage(string)

				if string == chr(0x18): # soft reset
					self.drainQueue()
					self.inFile = False
					self.lineCt = 0

			if self.waitOK is None and not self.commandQ.empty():
				string, tries = self.commandQ.get(False)
				self.waitOK = {"seq": self.sequence, "data": string.rstrip(), "command": True, "tries": tries}
				self.sendMessage(string)
				self.sequence += 1
				
			elif self.waitOK is None and not self.gcodeQ.empty():
				msg = self.gcodeQ.get(False)
				if msg["cmd"] == "START":
					self.lineCt = 0
					self.inFile = True

				elif msg["cmd"] == "DATA":
					if self.inFile:
						self.lineCt += 1
					self.waitOK = {"seq": self.sequence, "data": msg["data"].rstrip(), "command": False}
					self.sendMessage(msg["data"])
					self.sequence += 1

				elif msg["cmd"] == "END":
					self.inFile = False
					self.asyncQ.put({"type": "eof", "file": msg["name"], "lines": self.lineCt})

				elif msg["cmd"] == "LINE":
					self.waitOK = {"seq": self.sequence, "data": msg["data"].rstrip(), "command": False}
					self.sendMessage(msg["data"])
					self.sequence += 1

			if self.waitOK is not None:
				try:
					response = self.responseQ.get(True, 0.25)
				except queue.Empty:
					if self.waitOK["command"]:
						self.waitOK["tries"] -= 1
						if self.waitOK["tries"] == 0:
							outMsg = {"type": "response", "status": "<missing>", "data": self.waitOK["data"], "sequence": self.waitOK["seq"]}
							self.asyncQ.put(outMsg)
							self.waitOK = None
				else:
					outMsg = {"type": "response", "status": response, "data": self.waitOK["data"], "sequence": self.waitOK["seq"]}
					self.asyncQ.put(outMsg)
					self.waitOK = None

			time.sleep(0.01)

		self.endOfLife = True

	def getPosition(self):
		return self.lineCt
				
	def sendMessage(self, string):
		try:
			bmsg = bytes(string, 'UTF-8')
			self.port.write(bmsg)
			self.port.flush()
		except:
			print("write failure sending (%s)" % string)
			self.killJob()
			
	def killJob(self):
		self.drainQueue()
			
	def drainQueue(self):
		while True:
			try:
				msg = self.gcodeQ.get(False)
				if msg["cmd"] == "END":
					self.asyncQ.put({"type": "abort", "file": msg["name"]})
			except queue.Empty:
				break
	
class ListenThread(threading.Thread):
	def __init__(self, port, responseQ, asyncQ):
		super(ListenThread,self).__init__()
		self.port = port
		self.responseQ = responseQ		
		self.isRunning = False
		self.endOfLife = False
		self.asyncQ = asyncQ

		self.start()
		
	def kill(self):
		self.isRunning = False

	def isKilled(self):
		return self.endOfLife
		
	def run(self):
		self.isRunning = True
		while self.isRunning:
			if self.port.in_waiting > 0:
				line=self.port.read_until().decode("UTF-8").strip()

				if (len(line)>=1):
					llow = line.lower()
					
					if self.isResponse(llow):
						self.responseQ.put(llow)
		
					else:
						if line.startswith("<"):
							msg = {"type": "status", "data": line}
						elif line.startswith("$") or line.startswith("Grbl"):
							msg = {"type": "config", "data": line}
						elif line.startswith("[GC:"):
							msg = {"type": "parserstate", "data": line}
						elif line.startswith("ALARM"):
							msg = {"type": "alarm", "data": line}
						elif line.startswith("[MSG:"):
							try:
								body = line[5:-1]
							except:
								body = line
							msg = {"type": "feedback", "data": body}
						elif line.startswith("[PRB:"):
							msg = {"type": "probe", "data": line}
						else:
							msg = {"type": "message", "data": line}

						self.asyncQ.put(msg)
			time.sleep(0.01)

		self.endOfLife = True

	def isResponse(self, string):
		if string.startswith("ok"):
			return True
		if string.startswith("error:"):
			return True

		return False
		
class Grbl:
	def __init__(self, tty="/dev/ttyACM0", baud=115200, pollInterval=0.5):
		try:
			self.port = Serial(tty, baud, timeout=None)  #0.02)
			self.connected = True
		except Exception as e:
			self.connected = False
			raise e

		self.immedQ = queue.Queue(0)
		self.commandQ = queue.Queue(0)
		self.gcodeQ = queue.Queue(0)

		self.stopPoll = None
		self.pollTimer = None
		self.pollInterval = pollInterval

		self.responseQ = queue.Queue(0)
		self.asyncQ = queue.Queue(0)

		if self.connected:		
			self.listener = ListenThread(self.port, self.responseQ, self.asyncQ)
			self.sender = SendThread(self.port, self.immedQ, self.commandQ, self.gcodeQ, self.responseQ, self.asyncQ)
			self.sendImmediate("\r\n") # wake up grbl
			self.sendImmediate("\r\n")
			time.sleep(2)
			self.getConfig()

		else:
			self.listener = None
			self.sender = None

	def isConnected(self):
		return self.connected

	def jogxy(self, x, y, speed, absolute=False, metric=True):
		jogcmd = "$J="
		jogcmd += "G90" if absolute else "G91"
		jogcmd += "G21" if metric else "G20"
		if x is not None:
			jogcmd += "X%.3f" % x
		if y is not None:
			jogcmd += "Y%.3f" % y
		jogcmd += "F%d" % speed
		return self.sendCommand(jogcmd)

	def jogz(self, z, speed, absolute=False, metric=True):
		jogcmd = "$J="
		jogcmd += "G90" if absolute else "G91"
		jogcmd += "G21" if metric else "G20"
		if z is not None:
			jogcmd += "Z%.3f" % z
		jogcmd += "F%d" % speed
		return self.sendCommand(jogcmd)

	def gotoHome(self):
		return self.sendCommand("$H", tries=400)

	def probe(self):
		return self.sendCommand("G38.2 Z-50 F24", tries=200)

	def goto(self, x, y, z):
		gotocmd = "G90 G0"
		if x is not None or y is not None:
			if x is not None:
				gotocmd += " X%.3f" % x
			if y is not None:
				gotocmd += " Y%.3f" % y
			if not self.sendCommand(gotocmd):
				return False

		gotocmd = "G90 G0"
		if z is not None:
			gotocmd += " Z%.3f" % z
			if not self.sendCommand(gotocmd):
				return False
		
		return True

	def resetAxis(self, x, y, z):
		resetCmd = "G10 P0 L20 "
		if x is not None:
			resetCmd += "X%.3f " % x
		if y is not None:
			resetCmd += "Y%.3f " % y
		if z is not None:
			resetCmd += "Z%.3f " % z
		return self.sendCommand(resetCmd)

	def stopJog(self):
		return self.sendImmediate(chr(0x85))

	def holdFeed(self):
		return self.sendImmediate("!")

	def resume(self):
		return self.sendImmediate("~")

	def softReset(self):
		return self.sendImmediate(chr(0x18))

	def getParserState(self):
		return self.sendCommand("$G")

	def getConfig(self):
		return self.sendCommand("$$")

	def clearAlarm(self):
		return self.sendCommand("$X")

	def checkMode(self):
		return self.sendCommand("$C")

	def spindleOn(self):
		return self.sendCommand("M3")

	def spindleOff(self):
		return self.sendCommand("M5")

	def setSpindleSpeed(self, speed):
		return self.sendCommand("S%d" % speed)

	def adjustFeedRate(self, inc):
		if inc in [0, 100]:
			return self.sendImmediate(chr(0x90))

		if inc == 1:
			return self.sendImmediate(chr(0x93))

		if inc == 10:
			return self.sendImmediate(chr(0x91))

		if inc == -1:
			return self.sendImmediate(chr(0x94))

		if inc == -10:
			return self.sendImmediate(chr(0x92))

	def adjustRapidRate(self, inc):
		if inc in [0, 100]:
			return self.sendImmediate(chr(0x95))

		if inc == 50:
			return self.sendImmediate(chr(0x96))

		if inc == 25:
			return self.sendImmediate(chr(0x97))

	def adjustSpindleSpeed(self, inc):
		if inc in [0, 100]:
			return self.sendImmediate(chr(0x99))

		if inc == 1:
			return self.sendImmediate(chr(0x9c))

		if inc == 10:
			return self.sendImmediate(chr(0x9a))

		if inc == -1:
			return self.sendImmediate(chr(0x9d))

		if inc == -10:
			return self.sendImmediate(chr(0x9b))


	def startPoll(self):
		if not self.connected:
			return False

		self.stopPoll = threading.Event()
		self.pollTimer = RepeatTimer(self.stopPoll, self.pollInterval, self.sendPoll)
		self.pollTimer.start()
		return True

	def sendPoll(self):
		self.sendImmediate("?")

	def sendCommand(self, cmd, tries=2):
		if not self.connected:
			return False

		self.commandQ.put((cmd + '\n', tries))
		return True

	def sendImmediate(self, cmd):
		if not self.connected:
			return False

		self.immedQ.put(cmd)
		return True

	def sendGCodeLines(self, lines):
		if not self.connected:
			return False

		for ln in lines:
			self.gcodeQ.put({"cmd": "LINE", "data": ln.strip() + '\n'})
		return True

	def sendGCodeFile(self, fn):
		if not self.connected:
			return False

		self.gcodeQ.put({"cmd": "START", "name": fn})

		with open(fn,'r') as fp:
			for ln in fp:
				self.gcodeQ.put({"cmd": "DATA", "data": ln.strip() + '\n'})

		self.gcodeQ.put({"cmd": "END", "name": fn})
		return True

	def getPosition(self):
		return self.sender.getPosition()

	def nextAsyncMessage(self, wait=False):
		if not self.connected:
			return None

		if wait:
			response = self.asyncQ.get(True, timeout=None)
		else:
			if self.asyncQ.empty():
				return None
			response = self.asyncQ.get(False)

		if response["type"] == "alarm":
			self.softReset()
		return response
		
	def terminate(self):
		if self.stopPoll:
			self.stopPoll.set()

		senderKilled = True
		if self.sender is not None:
			senderKilled = False
			try:
				self.sender.kill()
			except:
				senderKilled = True

		listenerKilled = True
		if self.listener is not None:
			listenerKilled = False
			try:
				self.listener.kill()
			except:
				listenerKilled = True

		while not (senderKilled and listenerKilled):
			if not senderKilled:
				senderKilled = self.sender.isKilled()
			if not listenerKilled:
				listenerKilled = self.listener.isKilled()
			time.sleep(0.1)

		self.connected = False
		self.sender = None
		self.listener = None
