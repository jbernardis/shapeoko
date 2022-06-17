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

Settings = {
	0: {
		"setting": "Step pulse time",
		"units": "microseconds",
		"description": "Sets time length per step. Minimum 3usec."
	},
	1: {
		"setting": "Step idle delay",
		"units": "milliseconds",
		"description": "Sets a short hold delay when stopping to let dynamics settle before disabling steppers. Value 255 keeps motors enabled with no delay."
	},
	2: {
		"setting": "Step pulse invert",
		"units": "mask",
		"description": "Inverts the step signal. Set axis bit to invert (00000ZYX)."
	},
	3: {
		"setting": "Step direction invert",
		"units": "mask",
		"description": "Inverts the direction signal. Set axis bit to invert (00000ZYX)."
	},
	4: {
		"setting": "Invert step enable pin",
		"units": "boolean",
		"description": "Inverts the stepper driver enable pin signal."
	},
	5: {
		"setting": "Invert limit pins",
		"units": "boolean",
		"description": "Inverts the all of the limit input pins."
	},
	6: {
		"setting": "Invert probe pin",
		"units": "boolean",
		"description": "Inverts the probe input pin signal."
	},
	10: {
		"setting": "Status report options",
		"units": "mask",
		"description": "Alters data included in status reports."
	},
	11: {
		"setting": "Junction deviation",
		"units": "millimeters",
		"description": "Sets how fast Grbl travels through consecutive motions. Lower value slows it down."
	},
	12: {
		"setting": "Arc tolerance",
		"units": "millimeters",
		"description": "Sets the G2 and G3 arc tracing accuracy based on radial error. Beware: A very small value may effect performance."
	},
	13: {
		"setting": "Report in inches",
		"units": "boolean",
		"description": "Enables inch units when returning any position and rate value that is not a settings value."
	},
	20: {
		"setting": "Soft limits enable",
		"units": "boolean",
		"description": "Enables soft limits checks within machine travel and sets alarm when exceeded. Requires homing."
	},
	21: {
		"setting": "Hard limits enable",
		"units": "boolean",
		"description": "Enables hard limits. Immediately halts motion and throws an alarm when switch is triggered."
	},
	22: {
		"setting": "Homing cycle enable",
		"units": "boolean",
		"description": "Enables homing cycle. Requires limit switches on all axes."
	},
	23: {
		"setting": "Homing direction invert",
		"units": "mask",
		"description": "Homing searches for a switch in the positive direction. Set axis bit (00000ZYX) to search in negative direction."
	},
	24: {
		"setting": "Homing locate feed rate",
		"units": "mm/min",
		"description": "Feed rate to slowly engage limit switch to determine its location accurately."
	},
	25: {
		"setting": "Homing search seek rate",
		"units": "mm/min",
		"description": "Seek rate to quickly find the limit switch before the slower locating phase."
	},
	26: {
		"setting": "Homing switch debounce delay",
		"units": "milliseconds",
		"description": "Sets a short delay between phases of homing cycle to let a switch debounce."
	},
	27: {
		"setting": "Homing switch pull-off distance",
		"units": "millimeters",
		"description": "Retract distance after triggering switch to disengage it. Homing will fail if switch isn't cleared."
	},
	30: {
		"setting": "Maximum spindle speed",
		"units": "RPM",
		"description": "Maximum spindle speed. Sets PWM to 100% duty cycle."
	},
	31: {
		"setting": "Minimum spindle speed",
		"units": "RPM",
		"description": "Minimum spindle speed. Sets PWM to 0.4% or lowest duty cycle."
	},
	32: {
		"setting": "Laser-mode enable",
		"units": "boolean",
		"description": "Enables laser mode. Consecutive G1/2/3 commands will not halt when spindle speed is changed."
	},
	100: {
		"setting": "X-axis travel resolution",
		"units": "step/mm",
		"description": "X-axis travel resolution in steps per millimeter."
	},
	101: {
		"setting": "Y-axis travel resolution",
		"units": "step/mm",
		"description": "Y-axis travel resolution in steps per millimeter."
	},
	102: {
		"setting": "Z-axis travel resolution",
		"units": "step/mm",
		"description": "Z-axis travel resolution in steps per millimeter."
	},
	110: {
		"setting": "X-axis maximum rate",
		"units": "mm/min",
		"description": "X-axis maximum rate. Used as G0 rapid rate."
	},
	111: {
		"setting": "Y-axis maximum rate",
		"units": "mm/min",
		"description": "Y-axis maximum rate. Used as G0 rapid rate."
	},
	112: {
		"setting": "Z-axis maximum rate",
		"units": "mm/min",
		"description": "Z-axis maximum rate. Used as G0 rapid rate."
	},
	120: {
		"setting": "X-axis acceleration",
		"units": "mm/sec^2",
		"description": "X-axis acceleration. Used for motion planning to not exceed motor torque and lose steps."
	},
	121: {
		"setting": "Y-axis acceleration",
		"units": "mm/sec^2",
		"description": "Y-axis acceleration. Used for motion planning to not exceed motor torque and lose steps."
	},
	122: {
		"setting": "Z-axis acceleration",
		"units": "mm/sec^2",
		"description": "Z-axis acceleration. Used for motion planning to not exceed motor torque and lose steps."
	},
	130: {
		"setting": "X-axis maximum travel",
		"units": "millimeters",
		"description": "Maximum X-axis travel distance from homing switch. Determines valid machine space for soft-limits and homing search distances."
	},
	131: {
		"setting": "Y-axis maximum travel",
		"units": "millimeters",
		"description": "Maximum Y-axis travel distance from homing switch. Determines valid machine space for soft-limits and homing search distances."
	},
	132: {
		"setting": "Z-axis maximum travel",
		"units": "millimeters",
		"description": "Maximum Z-axis travel distance from homing switch. Determines valid machine space for soft-limits and homing search distances."
	}
}

