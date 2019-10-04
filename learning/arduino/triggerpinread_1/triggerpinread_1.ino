#include <Arduino.h>

//https://forum.arduino.cc/index.php?topic=334073.0

void setup() {
  //pinMode(13, OUTPUT);
  for(int i = 0; i < 14; i++)
    pinMode(i, INPUT_PULLUP);
  Serial.begin(9600);
}

const int buffer_length = 256; //must be a power of two
char buf[buffer_length];
int i = 0;

void loop() {
  
  while(1) {
    if(REG_PORT_IN0 & PORT_PA06) { //pin D8
      for(int k = 0; k < buffer_length; k++) {
        buf[k] = (REG_PORT_IN0 >> 7) & 0x01; //pin D9
      }
      
      String s = String("o=");
      for(int k = 0; k < buffer_length; k++) {
        s += String(buf[k], HEX);
      }
      Serial.println(s);
    }
  }
  
  /*
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
  */
}

