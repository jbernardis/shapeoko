#include <SimpleTimer.h>

SimpleTimer timer;

int xaxis = A0;
int yaxis = A1;
int zup = 2;
int zdown = 3;

int getBand(int v) {
	if (v > 400 and v <= 700)
		return (0);

	if (v <= 400) {
		if (v >= 300)
			return(-1);
		else if (v >= 200)
			return(-2);
		else
			return(-3);
	}
	else {
		if (v < 800)
			return(1);
		else if (v < 900)
			return(2);
		else
			return(3);
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
	int zUp = digitalRead(zup);
	int zDown = digitalRead(zdown);

	serial.print("[");
	serial.print(xVal);
	Serial.print(",");
	Serial.print(yVal);
	Serial.print(",");
	Serial.print(zUp);
	Serial.print(",");
	Serial.print(zDown);
	Serial.println("]");
}