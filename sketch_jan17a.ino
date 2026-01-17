int ledPins[] = {2, 3, 4, 5, 6}; // Arduino pins for 5 LEDs (LED1 on pin 2, LED2 on pin 3, etc.)
const int NUM_LEDS = 5;

void setup() {
  Serial.begin(9600); // Start serial communication with PC
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(ledPins[i], OUTPUT); // Set all LED pins as OUTPUT
    digitalWrite(ledPins[i], LOW); // Ensure all LEDs are off initially
  }
  Serial.println("Arduino ready to receive commands.");
}

void loop() {
  if (Serial.available() > 0) {
    char data = Serial.read(); // Read the incoming byte (e.g., '1', '2', '0')
    int numFingers = data - '0'; // Convert char to int (e.g., '1' becomes 1)

    Serial.print("Received: ");
    Serial.println(numFingers);

    // Turn off all LEDs first
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(ledPins[i], LOW);
    }

    // Turn on LEDs based on the number of fingers received
    for (int i = 0; i < numFingers; i++) {
      if (i < NUM_LEDS) { // Ensure we don't go out of bounds of our ledPins array
        digitalWrite(ledPins[i], HIGH);
      }
    }
  }
}