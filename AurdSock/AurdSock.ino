int c = 50;

void setup() {
  // put your setup code here, to run once:
  pinMode(11,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  analogWrite(11, c);
  if (Serial.available() > 0)
  {
    c = Serial.parseInt();
    Serial.read();
  }
 
  Serial.println(c);

  delay(20);
}
