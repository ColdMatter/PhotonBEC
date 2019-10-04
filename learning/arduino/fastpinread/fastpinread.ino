#include <Arduino.h>

//https://forum.arduino.cc/index.php?topic=334073.0

/*
#define PIN 12
volatile uint32_t *setPin = &PORT->Group[g_APinDescription[PIN].ulPort].OUTSET.reg;
volatile uint32_t *clrPin = &PORT->Group[g_APinDescription[PIN].ulPort].OUTCLR.reg;

const uint32_t  PinMASK = (1ul << g_APinDescription[PIN].ulPin);
*/

void setup() {
  //pinMode(13, OUTPUT);
  for(int i = 0; i < 14; i++)
    pinMode(i, INPUT_PULLUP);
  Serial.begin(9600);
}

const int buffer_length = 64; //must be a power of two
char buf[buffer_length];
int i = 0;

void loop() {
  if(i == buffer_length) {
    i = 0;
    String s = String("diff=");
    for(int k = 0; k < buffer_length; k++) {
      if(buf[k] == 0x01 || buf[k] == 0x02) {
        s += String(k);
        s += " ";
      }
    }
    Serial.println(s);
    delay(250);
  } else {
    //pins 9 and 8
    buf[i++] = (REG_PORT_IN0 >> 6) & 0x03;
  }
  /*
  String s = "IN0=";
  String pins = String(REG_PORT_IN0, BIN);
  Serial.println(s + pins);
  */
}
