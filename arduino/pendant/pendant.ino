#include <SimpleTimer.h>

SimpleTimer timer;

int xaxis = A0;
int yaxis = A1;
int zup = 2;
int zdown = 3;

int getBand(int v) {
	if (v > 412 and v <= 612)
		return (0);

	if (v <= 412) {
		if (v >= 312)
			return(-1);
		else if (v >= 212)
			return(-2);
		else if (v > 112)
			return(-3);
		else
			return(-4);
	}
	else {
		if (v < 712)
			return(1);
		else if (v < 812)
			return(2);
		else if (v < 912)
			return(3);
		else
			return(4);
	}
}

void setup() {
	pinMode(zup, INPUT_PULLUP);
	pinMode(zdown, INPUT_PULLUP);
    timer.setInterval(500, report);
	Serial.begin(115200);
}

void loop() {
	timer.run();
}

void report() {
	int xVal = getBand(analogRead(xaxis));
	int yVal = getBand(1024-analogRead(yaxis));
	int zup = digitalRead(zup);
	int zdown = digitalRead(zdown);

	serial.print("[");
	serial.print(xval);
	Serial.print(",");
	Serial.print(yval);
	Serial.print(",");
	Serial.print(zup);
	Serial.print(",");
	Serial.print(zdown);
	Serial.println("]");
}