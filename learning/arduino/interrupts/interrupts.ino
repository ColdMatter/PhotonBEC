const byte ledPin = 13;
const byte interruptPin = 3;
volatile byte state = LOW;
 
void setup() {
  Serial.begin(9600);
  Serial.println("setting up interrupts");
  pinMode(ledPin, OUTPUT);
  pinMode(interruptPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin), blink, FALLING);
  Serial.println("set up interrupts");
}
 
void loop() {
  Serial.println("loop()");
  digitalWrite(ledPin, state);
  delay(500);
}
 
void blink() {
  state = !state;
  Serial.println("interrupt fired");
}
