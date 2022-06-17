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

AlarmText = {
	1: "Hard Limit",
	2: "Soft Limit",
	3: "Abort during cycle",
	4: "Probe Fail(4)",
	5: "Probe Fail(5)",
	6: "Homing Fail(6)",
	7: "Homing Fail(7)",
	8: "Homing Fail(8)",
	9: "Homing Fail(9)"
}
