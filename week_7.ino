#include <Servo.h>

// Pin Motor 
#define PWMA 3   // PWM Motor Kanan (harus pin PWM)
#define PWMB 10  // PWM Motor Kiri (harus pin PWM)
#define DA 6     // Arah Motor Kanan
#define DB 7     // Arah Motor Kiri

// Pin Sensor Garis
#define SENSOR1 A0
#define SENSOR2 A1
#define SENSOR3 A2
#define SENSOR4 A3
#define SENSOR5 A4

#define SERVO_PIN 9  // Pin Servo (PWM)

Servo myServo;

void setup() {
  Serial.begin(115200);
  
  // Inisialisasi Motor
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(DA, OUTPUT);
  pinMode(DB, OUTPUT);
  stopMotors();

  // Inisialisasi Servo
  myServo.attach(SERVO_PIN);
  myServo.write(90);  // Posisi netral
}

void loop() {
  bacaSensor();
  bacaSerial();
}

void bacaSerial() {
  if (Serial.available() > 0) {
    String buff = Serial.readStringUntil('\n');
    
    if (buff.startsWith("R:")) {  // Motor Kanan
      int speed = buff.substring(2).toInt();
      setMotorKanan(speed);
    } 
    else if (buff.startsWith("L:")) {  // Motor Kiri
      int speed = buff.substring(2).toInt();
      setMotorKiri(speed);
    }
    else if (buff.startsWith("S:")) {  // Servo
      int angle = buff.substring(2).toInt();
      angle = constrain(angle, 0, 180);  // Batasi 0-180°
      myServo.write(angle);
    }
  }
}

// Fungsi untuk motor kanan (nilai + = CW, nilai - = CCW)
void setMotorKanan(int speed) {
  if (speed > 0) {
    digitalWrite(DA, HIGH);  // CW
    analogWrite(PWMA, speed);
  } else if (speed < 0) {
    digitalWrite(DA, LOW);   // CCW
    analogWrite(PWMA, abs(speed));
  } else {
    analogWrite(PWMA, 0);    // Stop
  }
}

// Fungsi untuk motor kiri (nilai + = CW, nilai - = CCW)
void setMotorKiri(int speed) {
  if (speed > 0) {
    digitalWrite(DB, HIGH);  // CW
    analogWrite(PWMB, speed);
  } else if (speed < 0) {
    digitalWrite(DB, LOW);   // CCW
    analogWrite(PWMB, abs(speed));
  } else {
    analogWrite(PWMB, 0);    // Stop
  }
}

void stopMotors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
}

void bacaSensor() {
  static unsigned long lastSend = 0;
  if (millis() - lastSend >= 100) {
    Serial.print("S1:"); Serial.print(analogRead(SENSOR1));
    Serial.print(",S2:"); Serial.print(analogRead(SENSOR2));
    Serial.print(",S3:"); Serial.print(analogRead(SENSOR3));
    Serial.print(",S4:"); Serial.print(analogRead(SENSOR4));
    Serial.print(",S5:"); Serial.println(analogRead(SENSOR5));
    lastSend = millis();
  }
}
