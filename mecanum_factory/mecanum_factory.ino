//此程序可以实现小车运行和机械臂运行，另外可以通过软串口收到数据控制小车
#include <Servo.h>
#include <SoftwareSerial.h>

volatile int Speed;  //定义车速
volatile int degree_A1;
volatile int degree_A2;
volatile int degree_A3;
volatile int degree_A4;  //四个舵机的角度变
Servo servo_A1;
Servo servo_A2;
Servo servo_A3;
Servo servo_A4;  //定义四个舵机
volatile char data;    //申明变量，串口收到的数据
SoftwareSerial mySerial(13,12);  //软串口

void uart() {                     //串口数据控制小车函数
  if (mySerial.available()) {  
    data = mySerial.read();
    Serial.println(data);
  }             //如果串口获得数据
  if (data == '2') {
    forward();
  } else if (data == '5') {
    Stop();
  } else if (data == '8') {
    back();
  } else if (data == '4') {
    left_pingyi();
  } else if (data == '6') {
    right_pingyi();
  } else if (data == '1') {
    left();
  } else if (data == '3') {
    right();
  } else if (data == '7') {
    if (degree_A4 < 135) {     //控制舵机较为缓慢的运行
      degree_A4 = degree_A4 + 1;
      servo_A4.write(degree_A4);
      delay(10);

    }
  } else if (data == '9') {
    if (degree_A4 > 45) {
      degree_A4 = degree_A4 - 1;
      servo_A4.write(degree_A4);
      delay(10);

    }
  } else if (data == 'a') {
    if (degree_A1 > 0) {
      degree_A1 = degree_A1 - 1;
      servo_A1.write(degree_A1);
      delay(10);

    }
  } else if (data == 'b') {
    if (degree_A1 < 180) {
      degree_A1 = degree_A1 + 1;
      servo_A1.write(degree_A1);
      delay(10);

    }
  } else if (data == 'c') {
    if (degree_A2 > 0) {
      degree_A2 = degree_A2 - 1;
      servo_A2.write(degree_A2);
      delay(10);

    }
  } else if (data == 'd') {
    if (degree_A2 < 180) {
      degree_A2 = degree_A2 + 1;
      servo_A2.write(degree_A2);
      delay(10);

    }
  } else if (data == 'e') {
    if (degree_A3 > 0) {
      degree_A3 = degree_A3 - 1;
      servo_A3.write(degree_A3);
      delay(10);

    }
  } else if (data == 'f') {
    if (degree_A3 < 180) {
      degree_A3 = degree_A3 + 1;
      servo_A3.write(degree_A3);
      delay(10);
    }
  }
}
//以上串口数据指令为购买本店摄像头和蓝牙，默认发送过来的数据，如果需要使用其他上位机设备，可自行定义data=='值'

void setMotor8833(int speedpin, int dirpin, int speed) {  //电机驱动函数
  if (speed == 0) {
    digitalWrite(dirpin, LOW);
    analogWrite(speedpin, 0);
  } else if (speed > 0) {
    digitalWrite(dirpin, LOW);
    analogWrite(speedpin, speed);
  } else {
    digitalWrite(dirpin, HIGH);
    analogWrite(speedpin, 255 + speed);
  }
}

void forward() {                        //本店4个电机板载引脚为 2 3     4 5     6 7     8 11
  setMotor8833(3, 2, Speed);
  setMotor8833(5, 4, Speed);
  setMotor8833(6, 7, Speed);
  setMotor8833(11, 8, Speed);
}

void left() {
  setMotor8833(3, 2, -1 * Speed);
  setMotor8833(5, 4, Speed);
  setMotor8833(6, 7, -1 * Speed);
  setMotor8833(11, 8, Speed);
}

void back() {
  setMotor8833(3, 2, -1 * Speed);
  setMotor8833(5, 4, -1 * Speed);
  setMotor8833(6, 7, -1 * Speed);
  setMotor8833(11, 8, -1 * Speed);
}

void right() {
  setMotor8833(3, 2, Speed);
  setMotor8833(5, 4, -1 * Speed);
  setMotor8833(6, 7, Speed);
  setMotor8833(11, 8, -1 * Speed);
}

void left_pingyi() {
  setMotor8833(3, 2, -1 * Speed);
  setMotor8833(5, 4, Speed);
  setMotor8833(6, 7, Speed);
  setMotor8833(11, 8, -1 * Speed);
}

void Stop() {
  setMotor8833(3, 2, 0);
  setMotor8833(5, 4, 0);
  setMotor8833(6, 7, 0);
  setMotor8833(11, 8, 0);
}

void right_pingyi() {
  setMotor8833(3, 2, Speed);
  setMotor8833(5, 4, -1 * Speed);
  setMotor8833(6, 7, -1 * Speed);
  setMotor8833(11, 8, Speed);
}

void go_test() {
  forward();
  delay(1000);
  back();
  delay(1000);
  left_pingyi();
  delay(1000);
  right_pingyi();
  delay(1000);
  left();
  delay(1000);
  right();
  delay(1000);
}

void setup(){
  Speed = 100;
  degree_A1 = 90;
  degree_A2 = 90;
  degree_A3 = 90;
  degree_A4 = 90;
  servo_A1.attach(A1);
  servo_A2.attach(A2);
  servo_A3.attach(A3);
  servo_A4.attach(A4);
  Stop();
  servo_A1.write(degree_A1);
  delay(0);
  servo_A2.write(degree_A2);
  delay(0);
  servo_A3.write(degree_A3);
  delay(0);
  servo_A4.write(degree_A4);
  delay(0);
  delay(2000);
  data = 0;
  mySerial.begin(9600);
  Serial.begin(9600);
  pinMode(3, OUTPUT);
  pinMode(2, OUTPUT);
  digitalWrite(3, LOW);
  digitalWrite(2, LOW);
  pinMode(5, OUTPUT);
  pinMode(4, OUTPUT);
  digitalWrite(5, LOW);
  digitalWrite(4, LOW);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  pinMode(11, OUTPUT);
  pinMode(8, OUTPUT);
  digitalWrite(11, LOW);
  digitalWrite(8, LOW);
}

void loop(){
  uart();
  //go_test();
}
