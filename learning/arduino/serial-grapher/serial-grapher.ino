#include <Arduino.h>
#include <math.h>

//https://forum.arduino.cc/index.php?topic=334073.0

void setup() {
  //pinMode(13, OUTPUT);
  for(int i = 0; i < 14; i++)
    pinMode(i, INPUT_PULLUP);
  Serial.begin(9600);
}

const int header_length = 2;
const int buffer_length = 256;
unsigned short buf[header_length + buffer_length];
int i = 0;

void loop() {
  int phase = 0;
  int phase_speed = 10;
  for(;;) {
    //delay(5);
    
    for(int k = 0; k < header_length; k++) {
      buf[k] = (short)(0xCCCC);
    }
    phase = (phase + phase_speed) % buffer_length;
    for(int k = 0; k < buffer_length; k++) {
      //13 bits
      buf[header_length + k] = (unsigned short)(round(4000*sin(2*M_PI * (k + phase) / buffer_length * 2.2) + 4000));
      //buf[header_length + k] = (unsigned short)(k + phase);
      //buf[header_length + k] = (unsigned short)(round(0.001*(k+phase)*(k+phase)));
      //buf[header_length + k] = (unsigned short)( ((k + phase) / 40)%2 == 0 ? 0x2099 : 0x01aa ); //0x2099 = 8345, 0x01aa = 426
    }
    
    char* char_buf = (char*)buf;
    for(int k = 0; k < (header_length + buffer_length)*2; k++) {
      Serial.write(char_buf[k] & 0xff);
    }
    //Serial.write(char_buf, (header_length + buffer_length)*2);
    
    //sending as string
    /*
    String s = String("");
    char tmp[16];
    sprintf(tmp, "len=%d ", (header_length + buffer_length)*2);
    s += tmp;
    for(int k = 0; k < header_length + buffer_length; k++) {
      sprintf(tmp, "%04X", buf[k] & 0xffff);
      s += tmp;
    }
    Serial.println(s);
    */
  }
}

