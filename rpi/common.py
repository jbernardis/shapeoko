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

ErrorText = {
	1:	"Expected command letter",
	2:	"Bad number format",
	3:	"Invalid statement",
	4:	"Value < 0",
	5:	"Homing is not enabled",
	6:	"Value < 3 usec",
	7:	"EEPROM read fail",
	8:	"Not idle",
	9:	"G-code lock",
	10:	"Homing not enabled",
	11:	"Line overflow",
	12:	"Step rate > 30kHz",
	13:	"Check Door",
	14:	"Line length exceeded",
	15:	"Travel exceeded",
	16:	"Invalid jog command",
	17:	"Laser mode requires PWM output",
	20:	"Unsupported command",
	21:	"Modal group violation",
	22:	"Undefined feed rate",
	23:	"Invalid G Code:23",
	24:	"Invalid G Code:24",
	25:	"Invalid G Code:25",
	26:	"Invalid G Code:26",
	27:	"Invalid G Code:27",
	28:	"Invalid G Code:28",
	29:	"Invalid G Code:29",
	30:	"Invalid G Code:30",
	31:	"Invalid G Code:31",
	32:	"Invalid G Code:32",
	33:	"Invalid G Code:33",
	34:	"Invalid G Code:34",
	35:	"Invalid G Code:35",
	36:	"Invalid G Code:36",
	37:	"Invalid G Code:37",
	38:	"Invalid G Code:38"
}
