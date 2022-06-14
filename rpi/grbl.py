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
		self.waitOKQ = queue.Queue(0)
		self.sequence = 0
		self.inFile = False

		self.start()
		
	def kill(self):
		self.isRunning = False

	def isKilled(self):
		return self.endOfLife

	def run(self):
		self.isRunning = True
		while self.isRunning:
			while not self.immedQ.empty():
				string = self.immedQ.get(False)
				self.sendMessage(string)
				
			if not self.waitOKQ.empty():
				self.checkForOK()

			elif not self.commandQ.empty():
				string = self.commandQ.get(False)
				self.waitOKQ.put({"seq": self.sequence, "data": string.rstrip()})
				self.sendMessage(string)
				self.sequence += 1
				
			elif not self.gcodeQ.empty():
				msg = self.gcodeQ.get(False)
				if msg["cmd"] == "START":
					self.lineCt = 0
					self.inFile = True

				elif msg["cmd"] == "DATA":
					if self.inFile:
						self.lineCt += 1
					self.waitOKQ.put({"seq": self.sequence, "data": msg["data"].rstrip()})
					self.sendMessage(msg["data"])
					self.sequence += 1

				elif msg["cmd"] == "END":
					self.inFile = False
					self.asyncQ.put({"event": "EOF", "file": msg["name"], "lines": self.lineCt, "data": ""})

				elif msg["cmd"] == "LINE":
					self.waitOKQ.put({"seq": self.sequence, "data": msg["data"].rstrip()})
					self.sendMessage(msg["data"])
					self.sequence += 1
			time.sleep(0.01)

		self.endOfLife = True

	def checkForOK(self):
		if self.responseQ.empty():
			return True

		response = self.responseQ.get(False)
		message = self.waitOKQ.get(False)
		outMsg = {"event": "response", "type": response, "data": message["data"], "sequence": message["seq"]}
		self.asyncQ.put(outMsg)
		return False

	def getPosition(self):
		return self.lineCt
				
	def sendMessage(self, string):
		try:
			if string[0] != "?":
				print(self.port.out_waiting)
			bmsg = bytes(string, 'UTF-8')
			self.port.write(bmsg)
			if string[0] != "?":
				print(self.port.out_waiting)
			self.port.flush()
			if string[0] != "?":
				print(self.port.out_waiting)
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
					self.asyncQ.put({"event": "ABORT", "file": msg["name"]})
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
					#print("rcvd: (%s)" % line.strip())
					llow = line.lower()
					
					if self.isResponse(llow):
						self.responseQ.put(llow)
		
					else:
						self.asyncQ.put({"event": "message", "data": line})
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
		print(jogcmd)
		return self.sendCommand(jogcmd)

	def jogz(self, z, speed, absolute=False, metric=True):
		jogcmd = "$J="
		jogcmd += "G90" if absolute else "G91"
		jogcmd += "G21" if metric else "G20"
		if z is not None:
			jogcmd += "Z%.3f" % z
		jogcmd += "F%d" % speed
		print(jogcmd)
		return self.sendCommand(jogcmd)

	def resetAxis(self, x, y, z):
		resetCmd = "G10 P0 L20 "
		if x is not None:
			resetCmd += "X%.3f " % x
		if y is not None:
			resetCmd += "Y%.3f " % y
		if z is not None:
			resetCmd += "Z%.3f " % z
		print(resetCmd)
		return self.sendCommand(resetCmd)

	def stopJog(self):
		print("stop jog immediate")
		return self.sendImmediate(chr(0x85))

	def holdFeed(self):
		return self.sendImmediate("!")

	def resume(self):
		return self.sendImmediate("~")

	def softReset(self):
		return self.sendImmediate(chr(0x18))

	def startPoll(self):
		if not self.connected:
			return False

		self.stopPoll = threading.Event()
		self.pollTimer = RepeatTimer(self.stopPoll, self.pollInterval, self.sendPoll)
		self.pollTimer.start()
		return True

	def sendPoll(self):
		self.sendImmediate("?")

	def sendCommand(self, cmd):
		if not self.connected:
			return False

		self.commandQ.put(cmd + '\n')
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
