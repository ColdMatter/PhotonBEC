#include <Arduino.h>

//https://forum.arduino.cc/index.php?topic=334073.0

#define PIN 12

volatile uint32_t *setPin = &PORT->Group[g_APinDescription[PIN].ulPort].OUTSET.reg;
volatile uint32_t *clrPin = &PORT->Group[g_APinDescription[PIN].ulPort].OUTCLR.reg;

const uint32_t  PinMASK = (1ul << g_APinDescription[PIN].ulPin);

void setup() {
  pinMode(PIN, OUTPUT);
}

void loop() {
  while(1) {
    *setPin = PinMASK;
    *clrPin = PinMASK;
  }
}
