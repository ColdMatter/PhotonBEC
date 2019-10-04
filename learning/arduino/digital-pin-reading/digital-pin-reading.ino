/*
 Input Pullup Serial

 This example demonstrates the use of pinMode(INPUT_PULLUP). It reads a
 digital input on pin 2 and prints the results to the serial monitor.

 The circuit:
 * Momentary switch attached from pin 2 to ground
 * Built-in LED on pin 13

 Unlike pinMode(INPUT), there is no pull-down resistor necessary. An internal
 20K-ohm resistor is pulled to 5V. This configuration causes the input to
 read HIGH when the switch is open, and LOW when it is closed.

 created 14 March 2012
 by Scott Fitzgerald

 http://www.arduino.cc/en/Tutorial/InputPullupSerial

 This example code is in the public domain

 */


int i = 0;
const int buf_len = 256;
int buf[buf_len];

void setup() {
  //start serial connection
  Serial.begin(9600);
  //configure pin2 as an input and enable the internal pull-up resistor
  pinMode(2, INPUT_PULLUP);
  pinMode(13, OUTPUT);
  i = 0;
}

void loop() {
  //read the pushbutton value into a variable
  int sensorVal = digitalRead(2);
  digitalWrite(13, sensorVal);
  
  /*
  buf[i++] = sensorVal;
  if(i == buf_len) {
    String out = String("buf= ");
    int j;
    for(j = 0; j < buf_len; j++) {
      out += buf[j];
    }
    Serial.println(out);
    i = 0;
  }
  */
}


