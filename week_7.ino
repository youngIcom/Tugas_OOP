#include <Servo.h>

// ========== PIN DEFINITIONS ==========
#define SENSOR_PIN A0    // Sensor analog di A0
#define MOTOR_IN1 5      // IN1 L298N -> Arduino 5 (PWM)
#define MOTOR_IN2 6      // IN2 L298N -> Arduino 6 (PWM)
#define MOTOR_IN3 7      // IN3 L298N -> Arduino 7
#define MOTOR_IN4 8      // IN4 L298N -> Arduino 8
#define SERVO_PIN 9      // Servo di pin 9

// ========== VARIABEL GLOBAL ==========
Servo myServo;
int lastSensorValue = 0;

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);
  
  // Inisialisasi pin motor
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_IN3, OUTPUT);
  pinMode(MOTOR_IN4, OUTPUT);
  
  // Inisialisasi servo
  myServo.attach(SERVO_PIN);
  myServo.write(90);  // Posisi netral
  
  // Stop motor saat startup
  stopMotors();
  
  Serial.println("System Ready - Waiting for commands...");
}

// ========== LOOP UTAMA ==========
void loop() {
  // 1. Baca sensor dan kirim ke Python
  readAndSendSensor();
  
  // 2. Handle perintah dari Python
  handleSerialCommands();
  
  delay(50);  // Jeda untuk stabilitas
}

// ========== FUNGSI BACA SENSOR ==========
void readAndSendSensor() {
  int sensorValue = analogRead(SENSOR_PIN);
  
  // Hanya kirim jika nilai berubah (untuk efisiensi)
  if(abs(sensorValue - lastSensorValue) > 5) {
    Serial.println(sensorValue);
    lastSensorValue = sensorValue;
  }
}

// ========== FUNGSI HANDLE SERIAL ==========
void handleSerialCommands() {
  if(Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    // Debug: Tampilkan perintah yang diterima
    Serial.print("CMD: ");
    Serial.println(command);
    
    if(command.startsWith("Motor:")) {
      int speed = command.substring(6).toInt();
      speed = constrain(speed, 0, 255);
      forward(speed);
    } 
    else if(command.startsWith("Servo:")) {
      int angle = command.substring(6).toInt();
      angle = constrain(angle, 0, 180);
      myServo.write(angle);
    }
    else if(command == "STOP") {
      stopMotors();
    }
  }
}

// ========== FUNGSI KONTROL MOTOR ==========
void forward(int speed) {
  analogWrite(MOTOR_IN1, speed);
  digitalWrite(MOTOR_IN2, LOW);
  analogWrite(MOTOR_IN3, speed);
  digitalWrite(MOTOR_IN4, LOW);
}

void backward(int speed) {
  digitalWrite(MOTOR_IN1, LOW);
  analogWrite(MOTOR_IN2, speed);
  digitalWrite(MOTOR_IN3, LOW);
  analogWrite(MOTOR_IN4, speed);
}

void stopMotors() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
  digitalWrite(MOTOR_IN3, LOW);
  digitalWrite(MOTOR_IN4, LOW);
}
