devMode = True

XAXIS = "X"
YAXIS = "Y"
ZAXIS = "Z"
AxisList = [ XAXIS, YAXIS, ZAXIS ]

MachineStates = [ "idle", "run", "hold", "jog", "alarm", "door", "check", "home", "sleep" ]

__bk = [0, 0, 0]
__gr = [97, 191, 19]
__or = [235, 129, 153]
__rd = [235, 20, 20]

StateColors = { 
	"idle": __gr,
	"run": __gr,
	"hold": __or,
	"jog": __gr,
	"alarm": __rd,
	"door": __bk,
	"check": __or,
	"home": __bk,
	"sleep": __bk,
}
