import time

from shapeoko import Shapeoko

sh = Shapeoko()
sh.startPoll()

sh.sendCommand("$G")
sh.sendGCodeFile("square.nc")

armed = False
idle = False
idleCt = 0
while not idle:
	msg = sh.nextAsyncMessage()
	print("Async: (%s)" % msg)
	if msg.startswith("<Run"):
		armed = True
	if msg.startswith("<Idle"):
		if armed:
			idleCt += 1
			if idleCt > 5:
				idle = True

time.sleep(1)
sh.terminate()
