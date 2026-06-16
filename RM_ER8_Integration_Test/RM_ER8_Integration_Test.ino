#include <EnableInterrupt.h>

// ==============================================================================
// 1. RC RECEIVER PIN DEFINITIONS
// ==============================================================================
#define RC_CH1 A0  // Right Stick X (Roll / Strafe)
#define RC_CH2 A1  // Right Stick Y (Pitch / Forward-Backward)
#define RC_CH3 A2  // Left Stick Y  (Throttle / Master Speed)
#define RC_CH4 A3  // Left Stick X  (Yaw / Rotation)

// ==============================================================================
// 2. MOTOR BOARD PIN DEFINITIONS (Extracted from Manufacturer Code)
// ==============================================================================
#define FL_PWM 3
#define FL_DIR 2
#define FR_PWM 5
#define FR_DIR 4
#define BL_PWM 6
#define BL_DIR 7
#define BR_PWM 11
#define BR_DIR 8

// ==============================================================================
// 3. BACKGROUND INTERRUPT TRACKING
// ==============================================================================
volatile uint16_t rc_values[4];
volatile uint32_t rc_start[4];

void calc_ch1() { if (digitalRead(RC_CH1)) rc_start[0] = micros(); else rc_values[0] = micros() - rc_start[0]; }
void calc_ch2() { if (digitalRead(RC_CH2)) rc_start[1] = micros(); else rc_values[1] = micros() - rc_start[1]; }
void calc_ch3() { if (digitalRead(RC_CH3)) rc_start[2] = micros(); else rc_values[2] = micros() - rc_start[2]; }
void calc_ch4() { if (digitalRead(RC_CH4)) rc_start[3] = micros(); else rc_values[3] = micros() - rc_start[3]; }

// ==============================================================================
// 4. DRV8833 MOTOR CONTROL FUNCTION (Direct from Manufacturer)
// ==============================================================================
void setMotor8833(int speedpin, int dirpin, int speed) {  
  if (speed == 0) {
    digitalWrite(dirpin, LOW);
    analogWrite(speedpin, 0);
  } else if (speed > 0) {
    digitalWrite(dirpin, LOW);
    analogWrite(speedpin, speed);
  } else {
    // DRV8833 requires inverted PWM for reverse
    digitalWrite(dirpin, HIGH);
    analogWrite(speedpin, 255 + speed); 
  }
}

// ==============================================================================
// 5. SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);

  // Set RC Pins as inputs
  pinMode(RC_CH1, INPUT); pinMode(RC_CH2, INPUT); 
  pinMode(RC_CH3, INPUT); pinMode(RC_CH4, INPUT);

  // Attach Interrupts for smooth reading
  enableInterrupt(RC_CH1, calc_ch1, CHANGE); enableInterrupt(RC_CH2, calc_ch2, CHANGE);
  enableInterrupt(RC_CH3, calc_ch3, CHANGE); enableInterrupt(RC_CH4, calc_ch4, CHANGE);

  // Initialize Motor Pins
  pinMode(FL_DIR, OUTPUT); pinMode(FL_PWM, OUTPUT); digitalWrite(FL_DIR, LOW); digitalWrite(FL_PWM, LOW);
  pinMode(FR_DIR, OUTPUT); pinMode(FR_PWM, OUTPUT); digitalWrite(FR_DIR, LOW); digitalWrite(FR_PWM, LOW);
  pinMode(BL_DIR, OUTPUT); pinMode(BL_PWM, OUTPUT); digitalWrite(BL_DIR, LOW); digitalWrite(BL_PWM, LOW);
  pinMode(BR_DIR, OUTPUT); pinMode(BR_PWM, OUTPUT); digitalWrite(BR_DIR, LOW); digitalWrite(BR_PWM, LOW);
}

// ==============================================================================
// 6. MAIN LOOP (Proportional Kinematics)
// ==============================================================================
void loop() {
  noInterrupts();
  int ch1_roll     = rc_values[0]; 
  int ch2_pitch    = rc_values[1];
  int ch3_throttle = rc_values[2];
  int ch4_yaw      = rc_values[3];
  interrupts();

  // A. Apply Deadbands (Ignore tiny stick drifts)
  if (abs(ch1_roll - 1500) < 50) ch1_roll = 1500;
  if (abs(ch2_pitch - 1500) < 50) ch2_pitch = 1500;
  if (abs(ch4_yaw - 1500) < 50) ch4_yaw = 1500;

  // B. Convert Joysticks to Vector Multipliers (-1.0 to 1.0)
  float x = (ch1_roll - 1500) / 500.0;   // Left/Right Strafe
  float y = (ch2_pitch - 1500) / 500.0;  // Forward/Backward Pitch
  float z = (ch4_yaw - 1500) / 500.0;    // Clockwise/CCW Yaw

  // C. Determine Master Speed Limit via Throttle (0 to 255)
  int master_speed = 0;
  if (ch3_throttle > 1050 && ch3_throttle < 2100) { 
      master_speed = map(ch3_throttle, 1050, 2000, 0, 255);
      master_speed = constrain(master_speed, 0, 255);
  }

  // D. Mecanum Inverse Kinematics Math
  float raw_FL = y + x + z;
  float raw_FR = y - x - z;
  float raw_BL = y - x + z;
  float raw_BR = y + x - z;

  // E. Normalization (Preserving the vector shape if values exceed 1.0)
  float max_raw = max(max(abs(raw_FL), abs(raw_FR)), max(abs(raw_BL), abs(raw_BR)));
  if (max_raw > 1.0) {
      raw_FL /= max_raw; raw_FR /= max_raw;
      raw_BL /= max_raw; raw_BR /= max_raw;
  }

  // F. Apply Master Throttle and Convert to integer speeds
  int speed_FL = raw_FL * master_speed;
  int speed_FR = raw_FR * master_speed;
  int speed_BL = raw_BL * master_speed;
  int speed_BR = raw_BR * master_speed;

  // G. Command the DRV8833 Motor Drivers
  setMotor8833(FL_PWM, FL_DIR, speed_FL);
  setMotor8833(FR_PWM, FR_DIR, speed_FR);
  setMotor8833(BL_PWM, BL_DIR, speed_BL);
  setMotor8833(BR_PWM, BR_DIR, speed_BR);

  delay(20); // Maintain a ~50Hz control loop
}