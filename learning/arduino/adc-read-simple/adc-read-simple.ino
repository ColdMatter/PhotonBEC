#include <Arduino.h>

//https://forum.arduino.cc/index.php?topic=334073.0

void setup() {
  //pinMode(13, OUTPUT);
  for(int i = 0; i < 14; i++)
    pinMode(i, INPUT_PULLUP);
  Serial.begin(9600);
}

const int buffer_length = 256;
int buf[buffer_length];
int i = 0;

void loop() {
  for(;;) {
    if(REG_PORT_IN0 & PORT_PA21) { //pin D7
    
      //read pins into buffer
      for(int k = 0; k < buffer_length; k++) {
        buf[k] = REG_PORT_IN0;
      }
      
      /*
      //parse pins for data
      for(int k = 0; k < buffer_length; k++) {
        buf[k] = (buf[k] >> 6) & 0x38 | (buf[k] >> 16) & 0x07; //0x38 == binary 111000
        //pins D0, D1, D3 and D11, D12, D13
      }
      */

      //sending only 1 bit
      for(int k = 0; k < buffer_length; k++) {
        buf[k] = (buf[k] >> 19) & 0x01;
      }
      
      String s = String("");
      char tmp[16];
      for(int k = 0; k < buffer_length; k++) {
        sprintf(tmp, "%1X", buf[k] & 0x1);
        s += tmp;
      }
      Serial.println(s);


      //sending whole 13-bit readings
      /*
      //parse pins for data
      for(int k = 0; k < buffer_length; k++) {
        buf[k] = (buf[k] >> 8) & 0x3FC0 | (buf[k] >> 6) & 0x3F;
        //0x3F   = binary 000000111111
        //0x3FC0 = binary 111111000000
      }

      String s = String("");
      char tmp[16];
      for(int k = 0; k < buffer_length; k++) {
        sprintf(tmp, "%03X", buf[k] & 0x1FF);
        s += tmp;
      }
      Serial.println(s);
      */
    }
  }
}

