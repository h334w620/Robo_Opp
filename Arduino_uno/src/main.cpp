#include <Arduino.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define MAX_SPEED 40
#define MOVE_DELAY 300
#define BUFFER_SIZE 32

// defined two stepper motor instants along with the driving scheme
// and the controlling pins
AccelStepper stepper1(AccelStepper::FULL4WIRE, 4, 5, 6, 7);
AccelStepper stepper2(AccelStepper::FULL4WIRE, 8, 9, 10, 11);

// defining a non-blocking stepper instant
MultiStepper steppers;

// defined two global buffers to store the current position information
// and the recieved serial data
long positions[2];
char buffer[BUFFER_SIZE];

void setup() {
  Serial.begin(9600); // Initialize serial communication at 9600 baud rate
  pinMode(12, OUTPUT); // Init the serial pins

  // set the max speed of each of the steppers
  stepper1.setMaxSpeed(MAX_SPEED);
  stepper2.setMaxSpeed(MAX_SPEED);

  // add the steppers to the non-blocking stepper instant
  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
  
  // init motor positions
  positions[0] = 0;
  positions[1] = 0;
}

void loop() {
  // check if the serial is available, if not used a blocking while loop
  // to wait into there are serial data to read.
  while (Serial.available() == 0) {}

  // read the serial data as bytes into the buffer
  int serial_data = Serial.readBytes(buffer, BUFFER_SIZE);

  // initalize the command and value variables
  int command, value;

  // sscanf parses the serial data into command and value int data
  // then stores it to their respective variables
  if (sscanf(buffer, "%d %d", &command, &value) != 2) {
    // if failes tells the orange PI 5 to resend commands
    Serial.print("n");
  }

    
  // Perform actions based on the command
  switch (command) {
  case 1: // Move forward
    // to move one stepper spins counter clock wise and the other spins clock wise
    // this is dones as the stepper motors is mirrored across the axis of
    // symmetry. This is the same when moving backwards but in reverse.
    positions[0] = positions[0] + value;
    positions[1] = positions[1] - value;
    steppers.moveTo(positions);
    steppers.runSpeedToPosition();

    // tell the orange PI 5 that the action is complete
    Serial.print("y");
    break;
  case 2: // Move backward
    positions[0] -= value;
    positions[1] += value;
    steppers.moveTo(positions);
    steppers.runSpeedToPosition();
    
    // tell the orange PI 5 that the action is complete
    Serial.print("y");
    break;
  case 3: // Rotate clockwise
    // the steppers are mounted across the axis of symmetry, therefor, steppers
    // moving in the same direction would be opposite relative to each other.
    // this rotates the robot.
    positions[0] -= value;
    positions[1] -= value;
    steppers.moveTo(positions);
    steppers.runSpeedToPosition();
    
    // tell the orange PI 5 that the action is complete
    Serial.print("y");
    break;
  case 4: // Rotate counterclockwise
    positions[0] += value;
    positions[1] += value;
    steppers.moveTo(positions);
    steppers.runSpeedToPosition();
    
    // tell the orange PI 5 that the action is complete
    Serial.print("y");
    break;
  case 5: // FIRE
    digitalWrite(12, HIGH);
    delay(value * 1000);
    digitalWrite(12, LOW);

    // tell the orange PI 5 that the action is complete
    Serial.print("y");
    break;
  default:
    // if the commands fail tell the orange PI 5 to resend commands
    Serial.print("n");
    break;
    }

  // clear the buffer for the next incoming serial data
  memset(buffer, 0, BUFFER_SIZE);
}




