#ifndef INPUTBOARD_H
#define INPUTBOARD_H

#define MAX_ICHIPS 8

class InputBoard {
    public:
        InputBoard(int, int, int, int);
        void setup(int);
        void retrieve(void);
        int getBit(int);
        int getChip(int);
        int getChipBit(int, int);

    private:
        int nChips, pLatch, pClock, pClockEnable, pData;
        int chipBits[MAX_ICHIPS];
};

#endif
