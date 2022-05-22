import time

from shapeoko import Shapeoko
from pendant import Pendant

sh = Shapeoko()
sh.startPoll()

p = Pendant()

sh.sendCommand("$G")
sh.sendGCodeFile("square.nc")


while True:
	msg = sh.nextAsyncMessage()
	if msg is not None:
		print("Async: (%s)" % msg)

	pcmd = p.getCommand()
	if p is not None:
		print("Pendant: (%s)" % pcmd)

time.sleep(1)
sh.terminate()
