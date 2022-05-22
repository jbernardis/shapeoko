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

		self.start()
		
	def kill(self):
		self.isRunning = False

	def isKilled(self):
		return self.endOfLife

	def run(self):
		self.isRunning = True
		while self.isRunning:
			if not self.immedQ.empty():
				string = self.immedQ.get(False)
				self.sendMessage(string)
				
			elif not self.waitOKQ.empty():
				self.checkForOK()

			elif not self.commandQ.empty():
				string = self.commandQ.get(False)
				self.sendMessage(string)
				self.waitOKQ.put(string.rstrip())
				
			elif not self.gcodeQ.empty():
				msg = self.gcodeQ.get(False)
				if msg["cmd"] == "START":
					self.lineCt = 0
				elif msg["cmd"] == "DATA":
					self.lineCt += 1
					#print("(%s)" % msg["data"])
					self.sendMessage(msg["data"])
					self.waitOKQ.put(msg["data"].rstrip())
				elif msg["cmd"] == "END":
					self.asyncQ.put("[EOF,%s]" % msg["name"])
					#print("EOF: %d lines" % self.lineCt)

			else:
				time.sleep(0.001)

		self.endOfLife = True

	def checkForOK(self):
		if self.responseQ.empty():
			return True

		response = self.responseQ.get(False)
		message = self.waitOKQ.get(False)
		outMsg = "[%s: %s]" % (response, message)
		#print(outMsg)
		if response != "ok":
			self.asyncQ.put(outMsg)
		return False

	def getPosition(self):
		return self.lineCt
				
	def sendMessage(self, string):
		try:
			#print("sending (%s)" % string)
			bmsg = bytes(string, 'UTF-8')
			self.port.write(bmsg)
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
					self.asyncQ.put("[ABORT,%s]" % msg["name"])
					#print("ABORT: %d lines" % self.lineCt)
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
			line=self.port.readline().decode("UTF-8").strip()

			if (len(line)>=1):
				#print("input (%s)" % line)
				llow = line.lower()
				
				if self.isResponse(llow):
					self.responseQ.put(llow)
	
				else:
					#print("got async (%s)" % line)
					self.asyncQ.put(line)

		self.endOfLife = True

	def isResponse(self, string):
		if string.startswith("ok"):
			return True
		if string.startswith("error:"):
			return True

		return False
		
class Shapeoko:
	def __init__(self, tty="/dev/ttyACM0", baud=115200, pollInterval=0.2):
		try:
			self.port = Serial(tty, baud, timeout=0.02)
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
			jogcmd += "X%f" % x
		if y is not None:
			jogcmd += "Y%f" % y
		jogcmd += "F%d\n" % speed
		return self.sendCommand(jogcmd)

	def jogz(self, z, speed, absolute=False, metric=True):
		jogcmd = "$J="
		jogcmd += "G90" if absolute else "G91"
		jogcmd += "G21" if metric else "G20"
		if z is not None:
			jogcmd += "Z%f" % z
		jogcmd += "F%d\n" % speed
		return self.sendCommand(jogcmd)

	def stopJog(self):
		return self.sendImmediate(chr(0x85))

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

	def sendGCodeFile(self, fn):
		if not self.connected:
			return False

		self.gcodeQ.put({"cmd": "START", "name": fn})

		with open(fn,'r') as fp:
			for ln in fp:
				self.gcodeQ.put({"cmd": "DATA", "data": ln.strip() + '\n'})

		self.gcodeQ.put({"cmd": "END", "name": fn})
		return True

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