/******************************************************************************
 **                                                                          **
 **     Written by Alexander Liptak (GitHub: @ajulik1997)                    **
 **     Date: Summer 2018                                                    **
 **     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                        **
 **     Phone: +44 7901 595107                                               **
 **                                                                          **
 ******************************************************************************/

/******************* MCP4725 DAC Controller for Arduino Uno *******************/

/***** MODES OF MODULATION ***** P[4,7,8] *****
    000: none [DEFAULT]
    001: sine
    010: square
    011: triangle
    100: sawtooth
    111: pulse
 **********************************************

 ***** MODES OF OPERATION ***** P[A0,A1] ******
   00: undefined
   01: master
   10: gated (NOTE: only works with mode 010)
   11: independent [DEFAULT]
 **********************************************/

#include "I2C.h"    // instead of Wire library, as it times out instead of locks up when transmission fails
#include "math.h"   // for computing sine, rounding, etc.

/************************ Global variable declarations ************************/

// MODULATION VARIABLES
uint16_t power = 0;      // Power of laser: 0-4095
uint32_t tot_micro = 0;  // MICROseconds that a full cycle should last (period)
uint32_t off_micro = 0;  // MICROseconds delay between cycles

// WAVE VARIABLES
bool needs_calibrating = true;  // Wave needs calibrating
bool waiting = true;            // Is wave waiting until delay is complete?
float divisor = 1.0;            // How many steps per wave (more steps, nicer wave, lower frequency)
float increment = 0.01;         // How much to increment the divisor (prevents calibration from taking too long)
unsigned long timer = 0;        // Wave timer (how long did my wave take, compared to target time)
unsigned long last_timer = 0;   // Wave timer, so we can revert to this in case we overincrement during alibration
float threshold = 50.0;      // Threshold of power above which laser triggers camera

// STATE VARIABLES
bool interlock_open = true;     // State of gate
bool override_on = true;        // State of interlock
bool periodic_warning = true;   // State of warning light / buzzer (blinking)
bool constant_warning = true;   // State of warning light / buzzer (constant)
char rgb_state = ' ';           // State of LED
uint8_t modeOfModulation = 0;   // Mode of modulation (none/sine/square/triangle/sawtooth/pulse)
uint8_t modeOfOperation = 3;    // Mode of operation (gated/master/independent)

// WARNING BEEP VARIALBES
unsigned long warn_timer = 0;   // Warning timer (for measuring time between beeps)
uint32_t warn_delay = 5e5;      // Warning delay (time to wait between beeps)

/************************** Function predeclarations **************************/

// MODULATION FUNCTIONS
inline void none();
inline void sine();
inline void square();
inline void triangle();
inline void sawtooth();
inline void pulse();

// HELPER FUNCTIONS
void writeToDAC(uint16_t);
void setRGB(char);
inline void calibrate();
inline void trigger(uint16_t);
inline void genericOff();

// PERIODIC CHECK FUNCTIONS
void check();
inline void checkInterlock();
inline void checkForSerial();
inline void checkModulationMode();
inline void checkOperationMode();

/********* writeToDAC ****** writes data to DAC register (not EEPROM) *********/

void writeToDAC(uint16_t val) {
  uint8_t bytes[2] = {val / 16, (val % 16) << 4}; // 16-bit int -> 2x8-bit ints
  I2c.write(0x62, 0x40, bytes, 2);    //0x62 - DAC Address, 0x40 - DAC Register
}

/******** setRGB ****** set RGB LED to colour represented by parameter ********/

void setRGB(char colour) {
  // override some colours on warnings
  if (colour == 'K' || colour == 'B' || colour == 'M') {
    if (periodic_warning) {
      colour = 'O';
    } else if (constant_warning) {
      colour = 'R';
    }
  }

  // if the same colour is already set, return from function, else set colour
  if (rgb_state == colour) return;
  rgb_state = colour;

  // set LED colour as requested
  switch (colour) {

    // ALWAYS ACCESSIBLE COLOURS
    case 'R': analogWrite(9, 64); analogWrite(10, 0); analogWrite(11, 0);  break; //RED     : INTERLOCK
    case 'G': analogWrite(9, 0); analogWrite(10, 0); analogWrite(11, 64);  break; //GREEN   : SERIAL
    case 'O': analogWrite(9, 64); analogWrite(10, 0); analogWrite(11, 8);  break; //ORANGE  : OVERRIDE

    // ACCESSIBLE WHEN NO WARNING
    case 'K': analogWrite(9, 0); analogWrite(10, 0); analogWrite(11, 0);   break; //KEY     : OFF
    case 'B': analogWrite(9, 0); analogWrite(10, 64); analogWrite(11, 0);  break; //BLUE    : LASER
    case 'M': analogWrite(9, 64); analogWrite(10, 64); analogWrite(11, 0); break; //MAGENTA : CALIB

      // DISABLED COLOURS
      //case 'W': analogWrite(9, 64); analogWrite(10, 64); analogWrite(11, 64); break;  //WHITE
      //case 'Y': analogWrite(9, 64); analogWrite(10, 0); analogWrite(11, 64); break;   //YELLOW
      //case 'C': analogWrite(9, 0); analogWrite(10, 64); analogWrite(11, 64); break;   //CYAN
  }
}

/*** calibrate ** adjusts steps per period of wave for requested frequency  ***/
// STILL NEED TO HAVE A LOOK AT THIS (percentage, fallback, idk idk, takes too long with low power? + comment on it!!) !!!!!!!!
inline void calibrate() {
  // to avoid micros from increasing while executing function
  unsigned long temp_timer = micros();
  
  // is the wave long enough
  if ((micros() - timer) <= (tot_micro)) {
    divisor = divisor + increment;
    return;
  }

  // did we overstep? which is closer?
  if ((fabs(temp_timer - timer) - tot_micro) > (fabs(temp_timer - last_timer) - tot_micro)){
    divisor = divisor - increment;
    return;
  }

  // finished calibrating
  needs_calibrating = !needs_calibrating;
  
}

/** trigger * if mode of operation is "master", signal pin in sync with wave **/

inline void trigger(uint16_t val) {
  if (val > threshold) {
    digitalWrite(3, HIGH);
    return;
  }
  digitalWrite(3, LOW);
}

/** genericOff *** generic function that switches off the DAC once if needed **/

inline void genericOff() {
  if (needs_calibrating) {       // resued bool to ensure this only happens once
    writeToDAC(0);               // switch DAC off
    needs_calibrating = false;
  }
  setRGB('K');                   // signal off, no longer lasing
}

/****** check ***** wrapper function for all checks that need to be done ******/

void check() {
  checkInterlock();
  checkForSerial();
  checkModulationMode();
  checkOperationMode();
}

/****** checkInterlock ***** checks the status of interlock and override ******/

inline void checkInterlock() {
  // pin status to useful variables
  interlock_open = not digitalRead(A3);
  override_on =  digitalRead(A2);

  // safety interlock is open, we need to find out if it is safe to continue
  if (interlock_open) {

    // override is on, we can continue but flash an orange warning light (and buzzer)
    if (override_on) {

      // if we came here from inerlock open and override not on, clear that
      constant_warning = false;
      // if time between waiting has elapsed toggle states
      if (micros() - warn_timer > warn_delay) {
        warn_timer = micros();
        periodic_warning = !periodic_warning;
        // LED orange and buzzer on for half a second
        if (periodic_warning) {
          analogWrite(6, 64);
          warn_delay = 5e5;
          setRGB('O');
          // LED black and buzzer off for 5 seconds
        } else {
          analogWrite(6, 0);
          warn_delay = 5e6;
          setRGB('K');
        }
      }
      return;
    } else {
      // interlock is open and override is not on, cut power and signal red (do this only once)
      if (!constant_warning) {
        constant_warning = true;
        periodic_warning = false;
        power = 0;
        analogWrite(6, 64);
        setRGB('R');
      }
      return;
    }
  } else {
    // interlock is closed, we don't care about override, switch off all warnings (only once)
    if (constant_warning || periodic_warning) {
      constant_warning = false;
      periodic_warning = false;
      analogWrite(6, 0);
      setRGB('K');
    }
    return;
  }
}

/***** checkForSerial ***** checks for incoming serial data and parses it *****/

inline void checkForSerial() {
  // only do anything if data is waiting to be parsed
  if (Serial.available() > 0) {
    setRGB('G');                                    // we are busy with serial communication
    String str = Serial.readString();               // get one line from Serial
    uint8_t str_index = 0;                          // start from first character
    while (str_index != str.indexOf("\r\n")) {      // if we have not reached the end
      while (str.indexOf(" ", str_index) != -1) {   // if we have not reached the last space
        float val = str.substring(str_index + 1, str.indexOf(" ", str_index)).toFloat();  // extract float
        switch (str.charAt(str_index)) {            // first character signals what float means, sort accordingly
          case 'A': power = round(4095 * (val / 100.0)); break;
          case 'T': threshold = val; break;
          case 'P': tot_micro = round(val * 1e3); increment = pow(tot_micro, 2) / (5e9) + 0.001; break;
          case 'D': off_micro = round(val * 1e3); break;
        }
        str_index = str.indexOf(" ", str_index) + 1; // continue to next space
      }
    }
    Serial.println("OK");       // signal transmission successful
    needs_calibrating = true;   // set calibration flag
    divisor = 1.0;              // reset wave divisor
    setRGB('K');                // LED off, transmission complete
  }
}

/***** checkModulationMode ****** detects the mode of modulation of laser *****/

inline void checkModulationMode() {
  // gets mode of modulation as a number from combination of three pins
  modeOfModulation = 4 * (uint8_t)(digitalRead(4)) +
                     2 * (uint8_t)(digitalRead(7)) +
                     1 * (uint8_t)(digitalRead(8));
}

/****** checkOperationMode ****** detects the mode of operation of laser ******/

inline void checkOperationMode() {
  // gets mode of operation as a number from combination of two pins
  modeOfOperation = 2 * (uint8_t)(digitalRead(A0)) +
                    1 * (uint8_t)(digitalRead(A1));
}

/*************************** MODE 000: No modulation **************************/

inline void none() {
  delayMicroseconds(16);    // necessary for Pi to settle pins before reading
  needs_calibrating = true; // not really calibration, but reusing variable

  // should stay in this loop until modulation mode is changed
  while (modeOfModulation == 0) {
    check();

    // only change the DAC value if it needs to be changed
    if (needs_calibrating) {
      writeToDAC(power);
      needs_calibrating = false;
    }

    // if power is off, set LED to black
    if (power == 0) {
      setRGB('K');
      continue;
    }

    // set LED to blue, we a lasing
    setRGB('B');
  }
}

/*********************** MODE 001: Sine wave modulation ***********************/

inline void sine() {
  delayMicroseconds(16);    // necessary for Pi to settle pins before reading
  needs_calibrating = true; // wave will need to be calibrated on first start
  divisor = 1.0;            // reset divisor, this will be calibrated later
  waiting = true;
  timer = micros();

  // should stay in this loop until modulation mode is changed
  while (modeOfModulation == 1) {
    check();
    
    // if power is zero, no point generating wave, set DAC to 0 once, LED off
    if (power == 0) {
      genericOff();
      continue;
    }

    // do not proceede with the wave if we need to delay
    if (waiting){
      if ((micros() - timer) > off_micro) waiting = false;
      continue;
    }

    // if wave needs calibrating, set LED to magenta, record start time
    if (needs_calibrating) {
      timer = micros();
      last_timer = timer;
      setRGB('M');
      // will need to call generic calibration function after wave is donw
    }

    // one full period of sine wave is generated here, number of steps decided by divisor
    for (float x = -M_PI; x < M_PI; x += (2.0 * M_PI) / divisor) {
      uint16_t val = round(((float)power / 2.0) * (cos(x) + 1.0));
      writeToDAC(val);
      if (modeOfOperation == 1) trigger(val);
    }

    // call generic calibration function, if required previously
    if (needs_calibrating) {
      calibrate();
      continue;
    }

    // if wave is calibrated, set LED to blue, we are lasing, get ready for next cycle
    setRGB('B');
    timer = micros();
    waiting = true;
  }
}

/********************** MODE 010: Square wave modulation **********************/

inline void square() {
  delayMicroseconds(16);    // necessary for Pi to settle pins before reading
  needs_calibrating = true; // not a calibration, but reusing bool to save memory
  bool on = false;          // whether the laser is currently on or off
  waiting = true;
  timer = micros();

  // should stay in this loop until modulation mode is changed
  while (modeOfModulation == 2) {
    check();

    // if power is zero, no point generating wave, set DAC to 0 once, LED off
    if (power == 0) {
      genericOff();
      continue;
    }

    // do not proceede with the wave if we need to delay
    if (waiting){
      if ((micros() - timer) > off_micro) waiting = false;
      continue;
    }

    // power is nonzero, alternate between on and off (on phase)
    if (!on && modeOfOperation != 2) {
      writeToDAC(power);
      timer = micros();
      if (modeOfOperation == 1) trigger(power);
      on = true;
      needs_calibrating = true;
      setRGB('B');
      continue;
    }

    // same as previous block but saves some overhead when triggering externally
    if (modeOfOperation == 2 && digitalRead(2) == HIGH) {
      writeToDAC(power);
      needs_calibrating = true;
      setRGB('B');
      continue;
    }

    // (wait for off, switch off)
    if ((micros() - timer > tot_micro/2.0) && needs_calibrating) {
      writeToDAC(0);
      timer = micros();
      if (modeOfOperation == 1) trigger(0);
      needs_calibrating = false;
      setRGB('K');
      continue;
    }

    // same as previous block but saves some overhead when triggering externally
    if ((modeOfOperation == 2 && digitalRead(2) == LOW) && needs_calibrating) {
      writeToDAC(0);
      needs_calibrating = false;
      setRGB('K');
      continue;
    }

    // (off phase)
    // this is ignored when camera is controlled externally
    if ((micros() - timer > tot_micro/2.0) && modeOfOperation != 2) {
      on = false;
      waiting = true;
    }
  }
}

/********************* MODE 011: Triangle wave modulation *********************/

inline void triangle() {
  delayMicroseconds(16);    // necessary for Pi to settle pins before reading
  needs_calibrating = true; // wave will need to be calibrated on first start
  divisor = 1.0;            // reset divisor, this will be calibrated later
  waiting = true;
  timer = micros();

  while (modeOfModulation == 3) {
    check();

    // if power is zero, no point generating wave, set DAC to 0 once, LED off
    if (power == 0) {
      genericOff();
      continue;
    }

    // do not proceede with the wave if we need to delay
    if (waiting){
      if ((micros() - timer) > off_micro) waiting = false;
      continue;
    }

    // if wave needs calibrating, set LED to magenta, record start time
    if (needs_calibrating) {
      timer = micros();
      setRGB('M');
      // will need to call generic calibration function after wave is donw
    }

    // one full period of sine wave is generated here, number of steps decided by divisor
    for (float x = -(float)power; x < power; x += (float)power / divisor) {
      uint16_t val = round(-fabs(x) + power);
      writeToDAC(val);
      if (modeOfOperation == 1) trigger(val);
    }

    // call generic calibration function, if required previously
    if (needs_calibrating) {
      calibrate();
      continue;
    }

    // if wave is calibrated, set LED to blue, we are lasing, get ready for next cycle
    setRGB('B');
    timer = micros();
    waiting = true;
  }
}

/********************* MODE 100: Sawtooth wave modulation *********************/

inline void sawtooth() {
  delayMicroseconds(16);    // necessary for Pi to settle pins before reading
  needs_calibrating = true; // wave will need to be calibrated on first start
  divisor = 1.0;            // reset divisor, this will be calibrated later
  waiting = true;
  timer = micros();

  while (modeOfModulation == 4) {
    check();

    // if power is zero, no point generating wave, set DAC to 0 once, LED off
    if (power == 0) {
      genericOff();
      continue;
    }
    
    // do not proceede with the wave if we need to delay
    writeToDAC(0);
    if (waiting){
      if ((micros() - timer) > off_micro) waiting = false;
      continue;
    }
    
    // if wave needs calibrating, set LED to magenta, record start time
    if (needs_calibrating) {
      timer = micros();
      setRGB('M');
      // will need to call generic calibration function after wave is donw
    }

    // one full period of sine wave is generated here, number of steps decided by divisor
    for (float x = 0; x < power; x += (float)power / divisor) {
      writeToDAC(x);
      if (modeOfOperation == 1) trigger(x);
    }

    // call generic calibration function, if required previously
    if (needs_calibrating) {
      calibrate();
      continue;
    }

    // if wave is calibrated, set LED to blue, we are lasing, get ready for next cycle
    setRGB('B');
    timer = micros();
    waiting = true;
  }
}

/**************************** MODE 111: Pulse mode ****************************/

// basically almost the same as square wave mode, with some very subtle changes
inline void pulse() {
  delayMicroseconds(16);        // necessary for Pi to settle pins before reading
  needs_calibrating = true;     // not a calibration, but reusing bool to save memory
  //bool pulsed = false;          // whether the pulse has already occured
  waiting = false;
  //??? timer = micros();

  while (modeOfModulation == 7) {
    check();
    // if power is zero, no point generating wave, set DAC to 0 once, LED off
    if (power == 0) {
      genericOff();
      continue;
    }

    // power is nonzero, alternate between on and off (on phase)
    if (!waiting && modeOfOperation != 2) {
      timer = micros();
      writeToDAC(power);
      if (modeOfOperation == 1) trigger(power);
      waiting = true;
      needs_calibrating = true;
      setRGB('B');
      continue;
    }

    // same as previous block but saves some overhead when triggering externally
    if (modeOfOperation == 2 && digitalRead(2) == HIGH) {
      writeToDAC(power);
      needs_calibrating = true;
      setRGB('B');
      continue;
    }

    // (wait for off, switch off)
    if ((micros() - timer > tot_micro) && needs_calibrating) {
      writeToDAC(0);
      timer = micros();
      if (modeOfOperation == 1) trigger(0);
      needs_calibrating = false;
      setRGB('K');
      continue;
    }

    // same as previous block but saves some overhead when triggering externally
    if ((modeOfOperation == 2 && digitalRead(2) == LOW) && needs_calibrating) {
      writeToDAC(0);
      needs_calibrating = false;
      setRGB('K');
      continue;
    }

    // (off phase)
    // this is ignored when camera is controlled externally
    if ((micros() - timer > off_micro) && modeOfOperation != 2) {
      waiting = false;
    }
  }
}

/********************************* SETUP CODE *********************************/

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
  I2c.begin();
  I2c.setSpeed(1); // Set to high-speed mode
  I2c.pullup(1);
  I2c.timeOut(10); // 10ms timeout
  writeToDAC(0);   // Set DAC to known state ASAP

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
}

/***************************** INFINITE MAIN LOOP *****************************/

void loop() {
  check();

  if (power == 0) return;

  switch (modeOfModulation) {
    case 0: none();
    case 1: if (tot_micro != 0) sine();
    case 2: if (tot_micro != 0 || modeOfOperation == 2) square();
    case 3: if (tot_micro != 0) triangle();
    case 4: if (tot_micro != 0) sawtooth();
    case 7: if (tot_micro != 0 || modeOfOperation == 2) pulse();
  }
}

