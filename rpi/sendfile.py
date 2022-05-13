import serial
import time

class CNC:
	def __init__(self, port):
		self.port = port
		self.millimeters = True
		self.absolute = True

	def sendFile(self, fn):
		self.port.write("\r\n\r\n") # wake up grbl
		time.sleep(2)   # Wait for grbl to initialize 
		self.port.flushInput()  # Flush startup text 
		with open(fn,'r') as fp:
			for ln in fp:
				self.port.write(ln.strip() + '\n')
				response = self.port.readline() 
				print(ln.strip() + " : " + response)
				
			fp.close()

	def setMillimeters(self, millimeters=True):
		self.millimeters = millimeters

	def sendMillimeters(self, endline=True):
		if self.millimeters:
			self.port.write("G21")
		else:
			self.port.write("G20")
		if endline:
			self.port.write("\n")
			response = self.port.readline() 

	def setAbsolute(self, absolute=True):
		self.absolute = absolute

	def sendAbsolute(self, endline=True)
		if self.absolute:
			self.port.write("G90")
		else:
			self.port.write("G91")
		if endline:
			self.port.write("\n")
			response = self.port.readline() 

	def jogxy(self, x, y, speed):
		self.port.write("$J=")
		self.sendMillimeters(False)
		self.sendAbsolute(False)
		if x is not None:
			self.port.write("X%f" % x)
		if y is not None:
			self.port.write("Y%f" % y)
		self.port.write("F%d\n" % speed)
		response = self.port.readline() 

	def jogz(self, z, speed):
		self.port.write("$J=")
		self.sendMillimeters(False)
		self.sendAbsolute(False)
		self.port.write("Z%f" % z)
		self.port.write("F%d\n" % speed)
		response = self.port.readline() 

	def stopJog(self):
		self.port.write(0x85)
		self.port.flush()
