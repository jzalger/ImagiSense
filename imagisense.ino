// This file implements the Particle Core firmware for Imagisense.
// It simply takes a reading from the sensor, then publishes to a Spark SSE feed.

int reading = 0;
double voltage = 0.0;
double temperature = 0;

void setup() {
    pinMode(A7, INPUT);
    Particle.variable("temperature",temperature);
    Particle.variable("reading", reading);
    Particle.variable("voltage", voltage);
}

void loop() {
    delay(5000);
    reading = analogRead(A7);
    
    // The returned value from the Core is going to be in the range from 0 to 4095
    voltage = (reading * 3.3) / 4095;

    temperature = (voltage - 0.5) * 100;
  
    char tempString[10] = {"01"};
    sprintf(tempString,"%f",temperature);
    Particle.publish("temperature",tempString);
    //delay(5000);
    delay(500);
    Particle.sleep(SLEEP_MODE_DEEP,900);
}
