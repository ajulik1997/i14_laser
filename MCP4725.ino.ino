#include "Wire.h"
#include "math.h"

////////////////////////////////////////

// MODES OF MODULATION P[4,7,8]
//  000: none [STARTS HERE]
//  001: sine
//  010: square
//  011: triangle
//  100: sawtooth
//  111: pulse

// MODES OF OPERATION P[A0,A1]
// 00: undefined
// 10: gated (slave) - only works with mode 010
// 01: master
// 11: independant

////////////////////////////////////////

// MODULATION VARIABLES
uint16_t power = 0;      // Power of laser: 0-4095
uint32_t tot_micro = 0;  // MICROseconds that a full cycle should last
uint32_t off_micro = 0;  // MICROseconds that should be spend low during cycle

// PULSE MODE VARIABLES
uint32_t pulse_len = 0;   // MICROseconds to pulse laser for
uint32_t pulse_wait = 0;  // MICROseconds to wait between pulses

////////////////////////////////////////

// STATE VARIABLES
bool interlock_open = true;     // State of gate
bool override_on = true;        // State of interlock
bool periodic_warning = true;   // State of warning light / buzzer (blinking)
bool constant_warning = true;   // State of warning light / buzzer (constant)
char rgb_state = ' ';           // State of LED

// WAVE VARIABLES
bool needs_calibrating = true;  // Wave needs calibrating
uint32_t divisor = 2;           // Divisor of wave
unsigned long timer = 0;        // Wave timer

// WARNING BEEP VARIALBES
unsigned long warn_timer = 0;   // Warning timer (for measuring time between beeps)
uint32_t warn_delay = 5e5;      // Warning delay (time to wait between beeps)

////////////////////////////////////////

// Writes data to DAC
// 0x64 - Address of DAC
// 0x40 - Register of DAC
// 16-bit int split into two 8-bit ints

void writeToDAC(uint16_t val) {
  Wire.beginTransmission(0x62);
  Wire.write(0x40);
  Wire.write(val / 16);
  Wire.write((val % 16) << 4);
  Wire.endTransmission();
}

////////////////////////////////////////

// CONSTANT OUTPUT MODE
void none() {
  delayMicroseconds(5);
  needs_calibrating = true; // not really calibration, but reusing variable

  while (digitalRead(4) == LOW &&
         digitalRead(7) == LOW &&
         digitalRead(8) == LOW) {
    check();

    // only change the DAC value if it needs to be changed
    if (needs_calibrating) {
      writeToDAC(power);
      needs_calibrating = false;
    }

    // update LED colour accordingly
    if (power != 0) {
      setRGB('B');
    } else {
      setRGB('K');
    }
  }
}

////////////////////////////////////////

// SINE WAVE MODULATION
void sine() {
  delayMicroseconds(5);
  needs_calibrating = true;

  while (digitalRead(4) == LOW &&
         digitalRead(7) == LOW &&
         digitalRead(8) == HIGH) {
    check();

    if (power != 0) { // no point generating a 0 amplitude wave
      // ---------- NON-ZERO AMPLITUDE ----------

      if (needs_calibrating) {
        // ---------- CALIBRATION STAGE ----------
        setRGB('M');
        divisor = 2;

        while (needs_calibrating) {
          timer = micros();
          // ----------
          for (float x = -M_PI; x < M_PI; x += (2 * M_PI) / divisor) {
            uint16_t val = round(((float)power / 2) * (cos(x) + 1));
            writeToDAC(val);
          }
          delayMicroseconds(off_micro);
          // ----------
          if ((micros() - timer) < (tot_micro)) {
            divisor = divisor + 1;
          } else {
            needs_calibrating = !needs_calibrating; break;
          }
        }
        // ---------- CALIBRATION STAGE ----------
      }

      // ---------- OUTPUT STAGE ----------
      setRGB('B');
      for (float x = -M_PI; x < M_PI; x += (2 * M_PI) / divisor) {
        uint16_t val = round(((float)power / 2) * (cos(x) + 1));
        writeToDAC(val);
      }
      delayMicroseconds(off_micro);
      // ---------- OUTPUT STAGE ----------

      // ---------- NON-ZERO AMPLITUDE ----------
    } else {  // if amplitude is zero, just set it once
      // ---------- ZERO AMPLITUDE ----------
      if (needs_calibrating) {
        writeToDAC(power);
        needs_calibrating = !needs_calibrating;
      }
      setRGB('K');
      // ---------- ZERO AMPLITUDE ----------
    }
  }
}

////////////////////////////////////////

void square() {
  delayMicroseconds(5);

  bool on = false;
  while (digitalRead(4) == LOW &&
         digitalRead(7) == HIGH &&
         digitalRead(8) == LOW) {

    check();
    if (power != 0) {
      setRGB('B');
      if (!on) {
        timer = micros();
        writeToDAC(power);
        on = true;
      } else {
        if (micros() - timer > tot_micro - off_micro) {
          writeToDAC(0);
        }
        if (micros() - timer > tot_micro) {
          on = false;
        }
      }
    } else {
      setRGB('K');
      writeToDAC(power);
    }
  }
}

////////////////////////////////////////

void triangle() {
  delayMicroseconds(5);
  if (!needs_calibrating) {
    needs_calibrating = true;
  }
  while (digitalRead(4) == LOW &&
         digitalRead(7) == HIGH &&
         digitalRead(8) == HIGH) {

    check();
    if (power != 0) { // no point generating a 0 amplitude wave

      // CALIBRATION STAGE
      if (needs_calibrating) {
        setRGB('M');
        divisor = 2;

        // TEST RUNS
        while (needs_calibrating) {
          timer = micros();
          // ----------
          for (float x = -(float)power; x < power; x += (float)power / divisor) {
            uint16_t val = round(-abs(x) + power);
            writeToDAC(val);
          }
          delayMicroseconds(off_micro);
          // ----------
          if ((micros() - timer) < (tot_micro)) {
            divisor++;
          } else {
            needs_calibrating = !needs_calibrating; break;
          }
        }
      }

      // CALIBRATED WAVE
      setRGB('B');
      for (float x = -(float)power; x < power; x += (float)power / divisor) {
        uint16_t val = round(-abs(x) + power);
        writeToDAC(val);
      }
      delayMicroseconds(off_micro);
    } else {
      setRGB('K');
      writeToDAC(power);
    }
  }
}

void sawtooth() {
  delayMicroseconds(5);
  if (!needs_calibrating) {
    needs_calibrating = true;
  }
  while (digitalRead(4) == HIGH &&
         digitalRead(7) == LOW &&
         digitalRead(8) == LOW) {

    check();
    if (power != 0) { // no point generating a 0 amplitude wave

      // CALIBRATION STAGE
      if (needs_calibrating) {
        setRGB('M');
        divisor = 2;

        // TEST RUNS
        while (needs_calibrating) {
          timer = micros();
          // ----------
          for (float x = 0; x < power; x += (float)power / divisor) {
            writeToDAC(x);
          }
          writeToDAC(0);
          delayMicroseconds(off_micro);
          // ----------
          if ((micros() - timer) < (tot_micro)) {
            divisor++;
          } else {
            needs_calibrating = !needs_calibrating; break;
          }
        }
      }

      // CALIBRATED WAVE
      setRGB('B');
      for (float x = 0; x < power; x += (float)power / divisor) {
        writeToDAC(x);
      }
      writeToDAC(0);
      delayMicroseconds(off_micro);
    } else {
      setRGB('K');
      writeToDAC(power);
    }
  }
}

void pulse() {
  delayMicroseconds(5);

  bool pulsed = false;
  while (digitalRead(4) == HIGH &&
         digitalRead(7) == HIGH &&
         digitalRead(8) == HIGH) {

    check();

    if (!pulsed) {
      timer = micros();
      writeToDAC(power);
      if (power != 0) {
        setRGB('B');
      }
      pulsed = true;
    } else {
      if (micros() - timer > pulse_len) {
        writeToDAC(0);
        setRGB('K');
      }
      if (micros() - timer > pulse_len + pulse_wait) {
        pulsed = false;
      }
    }
  }
}

void setRGB(char colour) {
  // OVERRIDE COLOURS ON WARNINGS
  if (colour == 'K' || colour == 'B' || colour == 'M') {
    if (constant_warning) {
      colour = 'R';
    } else if (periodic_warning) {
      colour = 'O';
    }
  }
  
  // DO NOTHING IF COLOUR IS ALREADY SET
  if (rgb_state == colour) {
    return;
  }
  rgb_state = colour;

  // MAIN PART
  switch (colour) {
    // ALWAYS ACCESSIBLE COLOURS
    case 'R': analogWrite(9, 64); analogWrite(10, 0); analogWrite(11, 0); Serial.println("SETTING RED!"); break;  //RED    : INTERLOCK
    case 'G': analogWrite(9, 0); analogWrite(10, 0); analogWrite(11, 64); break;  //GREEN  : SERIAL
    case 'O': analogWrite(9, 64); analogWrite(10, 0); analogWrite(11, 8); break;  //ORANGE : OVERRIDE

    // ACCESSIBLE WHEN NO WARNING
    case 'K': analogWrite(9, 0); analogWrite(10, 0); analogWrite(11, 0); Serial.println("SETTING BLACK!"); break;   //KEY     : OFF
    case 'B': analogWrite(9, 0); analogWrite(10, 64); analogWrite(11, 0); break;  //BLUE    : LASER
    case 'M': analogWrite(9, 64); analogWrite(10, 64); analogWrite(11, 0); break; //MAGENTA : CALIB


      // DISABLED COLOURS
      //case 'W': analogWrite(9, 64); analogWrite(10, 64); analogWrite(11, 64); break;  //WHITE
      //case 'Y': analogWrite(9, 64); analogWrite(10, 0); analogWrite(11, 64); break;   //YELLOW
      //case 'C': analogWrite(9, 0); analogWrite(10, 64); analogWrite(11, 64); break;   //CYAN
  }
  Serial.println(colour);
  Serial.println(rgb_state);
  Serial.println(periodic_warning);
  Serial.println(constant_warning);
}

void checkInterlock() {
  interlock_open = not digitalRead(A3);
  override_on =  digitalRead(A2);

  if (interlock_open) {
    if (override_on) {
      constant_warning = false;
      Serial.println("Periodic warning CHECK!");
      if (micros() - warn_timer > warn_delay) {
        warn_timer = micros();
        periodic_warning = !periodic_warning;
        if (periodic_warning) {
          analogWrite(6, 64);
          warn_delay = 5e5;
          setRGB('O');
          Serial.println("Periodic warning on!");
        } else {
          analogWrite(6, 0);
          warn_delay = 5e6;
          setRGB('K');
          Serial.println("Periodic warning off!");
        }
      }
    } else {
      if (!constant_warning) {
        constant_warning = true;
        periodic_warning = false;
        needs_calibrating = true;
        power = 0;
        analogWrite(6, 64);
        setRGB('R');
        Serial.println("Constant warning!");
      }
    }
  } else {
    if (constant_warning || periodic_warning) {
      constant_warning = false;
      periodic_warning = false;
      analogWrite(6, 0);
      setRGB('K');
      Serial.println("Warning off!");
    }
  }

  //  // INTERLOCK IS OPEN
  //  if (digitalRead(A3) == LOW) {
  //
  //    // INTERLOCK OVERRIDE IS ON
  //    if (digitalRead(A2) == HIGH) {
  //      if (gate_open) {
  //        gate_open = false;
  //        needs_calibrating = true;
  //      }
  //      if (micros() - warn_timer > warn_delay) {
  //        warn_timer = micros();
  //        warning = !warning;
  //        if (warning) {
  //          analogWrite(6, 64);
  //          warn_delay = 5e5;
  //          setRGB('O');
  //          return;
  //        } else {
  //          analogWrite(6, 0);
  //          warn_delay = 5e6;
  //          setRGB('K');
  //          return;
  //        }
  //      }
  //    } else {// OVERRIDE NOT ON, INTERLOCK OPEN
  //      Serial.println("OVERRIDE IS NOT ON!!!!!!");
  //      if (!gate_open || warning) {
  //        Serial.println("LETS KILL SOME LASERS!");
  //        warning = false;
  //        gate_open = true;
  //        analogWrite(6, 64);
  //        setRGB('R');
  //        power = 0;
  //        Serial.println("CALIBRATION FROM GATE");
  //        needs_calibrating = true;
  //        Serial.println("GATE IS OPEN!!!");
  //      }
  //      return;
  //    }
  //    //INTERLOCK CLOSED
  //  } else {
  //    if (warning || gate_open) {
  //      warning = false;
  //      gate_open = false;
  //      analogWrite(6, 0);
  //      setRGB('K');
  //      Serial.println("EVERYTHING OKAY NOW");
  //    }
  //    return;
  //  }
}

////////////////////////////////////////

void checkForSerial() {
  if (Serial.available() > 0) {
    setRGB('G');
    String str = Serial.readString();
    uint8_t str_index = 0;
    while (str_index != str.indexOf("\r\n")) {
      while (str.indexOf(" ", str_index) != -1) {
        float val = str.substring(str_index + 1, str.indexOf(" ", str_index)).toFloat();
        switch (str.charAt(str_index)) {
          case 'A': power = round(4095 * (val / 100)); break;
          case 'F': tot_micro = round((1 / val) * 1e6); break;
          case 'D': off_micro = round(tot_micro * (1 - (val / 100))); break;
          case 'P': pulse_len = val * 1e6; break;
          case 'W': pulse_wait = val * 1e6; break;
        }
        str_index++;
      }
    }
    Serial.println("OK");
    needs_calibrating = true;
    setRGB('K');
  }
}

////////////////////////////////////////

void check() {
  checkInterlock();
  checkForSerial();
}

////////////////////////////////////////

void setup() {
  // POWER LED
  pinMode(5, OUTPUT);
  analogWrite(5, 127);

  // WARNING BUZZER
  pinMode(6, OUTPUT);
  analogWrite(6, 0);

  // RGB LED
  pinMode(9, OUTPUT);  //RED
  pinMode(10, OUTPUT); //BLUE
  pinMode(11, OUTPUT); //GREEN
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);

  // MODULATION MODE INPUTS
  pinMode(4, INPUT);
  pinMode(7, INPUT);
  pinMode(8, INPUT);

  // OPERATION MODE INPUTS
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  // INTERLOCK MONITORING INPUTS
  pinMode(A2, INPUT); //INTERLOCK
  pinMode(A3, INPUT); //OVERRIDE


  // CAMERA CONTROL PINS
  pinMode(2, INPUT);  //CAMERA -> LASER
  pinMode(3, OUTPUT); //LASER -> CAMERA

  // I2C communication with DAC
  Wire.begin();
  Wire.setClock(400000);

  // Wait until serial becomes available
  Serial.begin(9600);
  while (!Serial) {
    ;
  }

  // LED Sweep (signal ready)
  uint8_t rgb[3] = {127, 0, 0};
  for (uint8_t less = 0; less < 3; less++) {
    uint8_t more = less == 2 ? 0 : less + 1;
    for (uint8_t i = 0; i < 127; i++) {
      rgb[less] -= 1;
      rgb[more] += 1;
      analogWrite(9, rgb[0]);
      analogWrite(11, rgb[1]);
      analogWrite(10, rgb[2]);
      delay(5);
    }
  }

  // Initial check to set state variables
  checkInterlock();
}

////////////////////////////////////////

void loop() {
  check();
  if (!interlock_open && power != 0) {
    // ===================================
    none();               // IS NOT A WAVE
    // ===================================
    if (tot_micro != 0) { //     IS A WAVE
      sine();
      square();
      triangle();
      sawtooth();
    } // ==================================
    if (pulse_len != 0) { //     IS A PULSE
      pulse();
    } // ==================================
  }
}

