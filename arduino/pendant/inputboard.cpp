#include <Arduino.h>

#include "inputboard.h"

#define BITS_PER_CHIP 8
#define PULSE_WIDTH_USEC   5

InputBoard::InputBoard(int pinLatch, int pinClock, int pinClockEnable, int pinData) {
    nChips = 0;
    pLatch = pinLatch;
    pClock = pinClock;
    pClockEnable = pinClockEnable;
    pData = pinData;
    for (int i = 0; i<MAX_ICHIPS; i++)
        chipBits[i] = 0;
}

void InputBoard::setup(int nchips) {
    nChips = nchips;
    pinMode(pClockEnable, OUTPUT);
    pinMode(pLatch, OUTPUT);
    pinMode(pClock, OUTPUT);
    pinMode(pData, INPUT);

	digitalWrite(pClock, LOW);
    digitalWrite(pLatch, HIGH);
    digitalWrite(pClockEnable, HIGH);
}

void InputBoard::retrieve(void) {
	digitalWrite(pClockEnable, HIGH);
    digitalWrite(pLatch, LOW);
    delayMicroseconds(5);
    digitalWrite(pLatch, HIGH);
    digitalWrite(pClockEnable, LOW);

    for(int i = 0; i < nChips; i++) {
        int cv = 0;
        for (int j = 0; j < BITS_PER_CHIP; j++) {
            int bitVal = digitalRead(pData);
            cv = (cv << 1) | bitVal;
  
            digitalWrite(pClock, HIGH);
            delayMicroseconds(PULSE_WIDTH_USEC);
            digitalWrite(pClock, LOW);
        }
        chipBits[i] = cv;
    }
}

int InputBoard::getChip(int cx) {
    if (cx < 0 || cx >= nChips)
        return(-1);
    return(chipBits[cx]);
}

int InputBoard::getChipBit(int cx, int bx) {
    if (cx < 0 || cx >= nChips)
        return(-1);

    if (bx < 0 or bx >= BITS_PER_CHIP)
        return(-1);

    int cv = chipBits[cx];
    int bv = cv & (1 << bx);
    if (bv != 0)
        return(1);
    else
        return(0);
}

int InputBoard::getBit(int cbx) {
    if (cbx < 0 || cbx >= (nChips * BITS_PER_CHIP))
        return (-1);

    int cx = int(cbx / BITS_PER_CHIP);
    int bx = cbx % BITS_PER_CHIP;
    return(getChipBit(cx, bx));
}
