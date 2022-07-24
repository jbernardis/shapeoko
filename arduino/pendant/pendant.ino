#include <SimpleTimer.h>
#include "inputboard.h"
#include "button.h"

SimpleTimer timer;

InputBoard inBd(8, 9, 11, 12);

Button bResetX(3, 50);
Button bResetY(4, 50);
Button bResetZ(5, 50);

int ibits = 24;
int ichips = 3;
int * inputValues;

#define DIR_NONE ""
#define DIR_N  "Y 4"
#define DIR_NE "XY 4 4"
#define DIR_E  "X 4"
#define DIR_SE "XY 4 -4"
#define DIR_S  "Y -4"
#define DIR_SW "XY -4 -4"
#define DIR_W  "X -4"
#define DIR_NW "XY -4 4"

char joggingDir[9];
char requestedDir[9];

void setup() {
	Serial.begin(115200);
	
	bResetX.begin();
	bResetY.begin();
	bResetZ.begin();

	inputValues = (int *) malloc(ibits * sizeof(int));
	inBd.setup(ichips);

	// retrieve initial switch positions
	inBd.retrieve();
	for (int i=0; i<ibits; i++) {
		*(inputValues+i) = inBd.getBit(i);
	}
	timer.setInterval(250, pulse);

	strcpy(joggingDir, DIR_NONE);
}

void loop() {
	timer.run();
}

void pulse() {
	inBd.retrieve();
	if (strcmp(joggingDir, DIR_NONE) == 0) {
		for (int i=0; i<ibits; i++) {
			int bv = inBd.getBit(i);
			if (i == 0 || i == 7 || i == 8 || i == 15) {
				// green continuous jog buttons
				*(inputValues+i) = bv;
			}
			if (bv != *(inputValues+i)) {
				checkJog(i, bv);
				*(inputValues+i) = bv;
			}
		}
	}
	else {
		*(inputValues+0) = inBd.getBit(0);
		*(inputValues+7) = inBd.getBit(7);
		*(inputValues+8) = inBd.getBit(8);
		*(inputValues+15) = inBd.getBit(15);
	}
	bool reqN = *(inputValues+15) == 0;
	bool reqS = *(inputValues+8) == 0;
	bool reqE = *(inputValues+7) == 0;
	bool reqW = *(inputValues+0) == 0;

	if ((reqN && reqS) || (reqE && reqW)){
		if (strcmp(joggingDir, DIR_NONE) != 0) {
			Serial.println("JOG STOP");
			strcpy(joggingDir, DIR_NONE);
		}
	}
	else {
		strcpy(requestedDir, DIR_NONE);
		if (reqN) {
			if (reqE) {
				strcpy(requestedDir, DIR_NE);
			}
			else if (reqW) {
				strcpy(requestedDir, DIR_NW);
			}
			else {
				strcpy(requestedDir, DIR_N);
			}
		}
		else if (reqS) {
			if (reqE) {
				strcpy(requestedDir, DIR_SE);
			}
			else if (reqW) {
				strcpy(requestedDir, DIR_SW);
			}
			else {
				strcpy(requestedDir, DIR_S);
			}
		}
		else if (reqE) {
			strcpy(requestedDir, DIR_E);
		}
		else if (reqW) {
			strcpy(requestedDir, DIR_W);
		}

		if (strcmp(requestedDir, joggingDir) != 0) {
			if (strcmp(requestedDir, DIR_NONE) == 0) {
				strcpy(joggingDir, DIR_NONE);
				Serial.println("JOG STOP");
			}
			else {
				if (strcmp(joggingDir, DIR_NONE) != 0) {
					Serial.println("JOG STOP");
				}
				strcpy(joggingDir, requestedDir);
				Serial.print("JOG ");
				Serial.println(requestedDir);
			}
		}
		
	}

	if (bResetX.pressed()) {
		Serial.println("RESET X");
	}

	if (bResetY.pressed()) {
		Serial.println("RESET Y");
	}

	if (bResetZ.pressed()) {
		Serial.println("RESET Z");
	}
}

void checkJog(int ix, int val) {
	int distance;
	char axis;

	axis = '\0';
	
	switch (ix) {
	case 0:
	case 7:
	case 8:
	case 15:
		if (val == 1) {
			Serial.println("JOG STOP");
		}
		else {
			axis = (ix <= 7 ? 'X' : 'Y');
			distance = (ix == 0 || ix == 8 ? -4 : 4);
		}
		break;
		
	case 1:
	case 6:
	case 9:
	case 14:
		if (val == 0) {
			axis = (ix <= 7 ? 'X' : 'Y');
			distance = (ix == 1 || ix == 9 ? -3 : 3);
		}
		break;
		
	case 2:
	case 5:
	case 10:
	case 13:
		if (val == 0) {
			axis = (ix <= 7 ? 'X' : 'Y');
			distance = (ix == 2 || ix == 10 ? -2 : 2);
		}
		break;
		
	case 3:
	case 4:
	case 11:
	case 12:
		if (val == 0) {
			axis = (ix <= 7 ? 'X' : 'Y');
			distance = (ix == 3 || ix == 11 ? -1 : 1);
		}
		break;
		
	case 16:
	case 21:
		if (val == 0) {
			axis = 'Z';
			distance = (ix == 16 ? -3 : 3);
		}
		break;
		
	case 17:
	case 20:
		if (val == 0) {
			axis = 'Z';
			distance = (ix == 17 ? -2 : 2);
		}
		break;
		
	case 18:
	case 19:
		if (val == 0) {
			axis = 'Z';
			distance = (ix == 18 ? -1 : 1);
		}
		break;
	}
	
	if (axis != '\0') {
		Serial.print("JOG ");
		Serial.print(axis);
		Serial.print(" ");
		Serial.println(distance);
	}
}
