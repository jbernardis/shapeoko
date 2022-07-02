#include <SoftwareSerial.h>
#define NDP 10

long aRevs[NDP];
long aMillis[NDP];
int aCount = 0;
int ax = 0;

const int gatePin = 2;  

volatile int revs = 0;
int lastRevs;
int lastMillis;

boolean atZero = true;
int zeroCount = 0;
char tempString[10]; 

int rpm;

SoftwareSerial s7s(7, 8);

void setup() {
	s7s.begin(9600);
    pinMode(gatePin, INPUT);
    attachInterrupt(digitalPinToInterrupt(gatePin), revCount, FALLING);

    lastRevs = 0;
    lastMillis = millis();
    rpm = 0;
    setBrightness(255);
    clearDisplay();
}

void loop() {
	int now = millis();
	int cRevs = revs;
	int iRevs = cRevs - lastRevs;
	int iMillis = now - lastMillis;
	if (iRevs >= 0 && iMillis > 0) {

		if (iRevs > 0) {
			if (atZero) {
				// ignore the first datapoint because it was a partial interval
				atZero = false;
			}
			else {
				aRevs[ax] = iRevs;
				aMillis[ax] = iMillis;
				if (++ax >= NDP)
					ax = 0;
				if (aCount < NDP)
					aCount++;
		
				long tRevs = 0;
				long tMillis = 0;
				for(int i=0; i<aCount; i++) {
					tRevs = tRevs + aRevs[i];
					tMillis = tMillis + aMillis[i];
				}
	
				rpm = (60000 * tRevs) / tMillis;
			}
		}

		if (iRevs == 0) {
			zeroCount++;
		}
		else {
			zeroCount = 0;
		}
		if (zeroCount < 5) {
			sprintf(tempString, "%4d", rpm);
			clearDisplay();
			s7s.print(tempString);
		}
		else {
			clearDisplay();
			aCount = 0;
			ax = 0;
			rpm = 0;
			atZero = true;
		}
		
	}

	lastMillis = now;
	lastRevs = cRevs;
	
	delay(1000);
}

void revCount() {
	revs++;
}

void setBrightness(byte value) {
  s7s.write(0x7A);  // Set brightness command byte
  s7s.write(value);  // brightness data byte
}

void clearDisplay()
{
  s7s.write(0x76);
}
