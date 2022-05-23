from serial import Serial

class Pendant:
	def __init__(self, tty="/dev/ttyUSB0", baud=115200):
		try:
			self.port = Serial(tty, baud)
			self.connected = True

		except Exception as e:
			self.connected = False
			raise e

	def getCommand(self):
		if not self.connected:
			return None

		if self.port.in_waiting == 0:
			return None

		return self.port.read_until().strip().decode("UTF-8")
