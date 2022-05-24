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
}

void loop() {
	timer.run();
}

void pulse() {
	inBd.retrieve();
	for (int i=0; i<ibits; i++) {
		int bv = inBd.getBit(i);
		if (bv != *(inputValues+i)) {
			checkJog(i, bv);
			*(inputValues+i) = bv;
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
