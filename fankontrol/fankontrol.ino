#define FAN1 10
#define FAN2 11
#define FAN1INT 2
#define FAN2INT 3

#define BUFSIZE 20
#define PWMCYC 3000

int fanCount1 = 0;
int fanComp1 = PWMCYC;
int fanCount2 = 0;
int fanComp2 = PWMCYC;

// Fan RPM things
unsigned int fanRpmCount1 = 0;
unsigned int countBuf1[BUFSIZE] = { 0 };
unsigned int fanRpmCount2 = 0;
unsigned int countBuf2[BUFSIZE] = { 0 };
char cur = 0;

//Serial communication
char incomingByte = 0;   // for incoming serial data
String inString = "";

void setup() {
  cli();//stop interrupts

  //set timer1 interrupt at 1Hz
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0
  // set compare match register for 1Hz increments
  OCR1A = 15624;//15624;// = (16*10^6) / (1*1024) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12 and CS10 bits for 1024 prescaler
  TCCR1B |= (1 << CS12) | (1 << CS10);
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  //set timer2 interrupt at 1kHz
  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  // set compare match register for 1khz increments
  OCR2A = 5;//249 = (16*10^6) / (1000*64) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set CS22 bit for 64 prescaler
  TCCR2B |= (1 << CS22);
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);

  sei();//allow interrupts

  pinMode(FAN1, OUTPUT);
  pinMode(FAN2, OUTPUT);
  digitalWrite(FAN1, HIGH);

  pinMode(FAN1INT, INPUT);
  pinMode(FAN2INT, INPUT);
  attachInterrupt(digitalPinToInterrupt(FAN2INT), rpmCall1, RISING);

  Serial.begin(9600);
}

ISR(TIMER2_COMPA_vect) {
  //Do slow manual PWM kinda thing
  if (fanCount1 == fanComp1) {
    digitalWrite(FAN1, LOW);
  }
  if (fanCount1 > PWMCYC) {
    digitalWrite(FAN1, HIGH);
    fanCount1 = 0;
  }

  if (fanCount2 == fanComp2) {
    digitalWrite(FAN2, LOW);
  }
  if (fanCount2 > PWMCYC) {
    digitalWrite(FAN2, HIGH);
    fanCount2 = 0;
  }
  
  fanCount1++;
  fanCount2++;
}

ISR(TIMER1_COMPA_vect) {
  //Check RPM speeds
  countBuf1[cur] = fanRpmCount1;
  fanRpmCount1 = 0;
  countBuf2[cur] = fanRpmCount2;
  fanRpmCount2 = 0;
  
  cur++;
  if (cur == BUFSIZE){
    cur = 0;
  }
}



void loop() {
  float rpm1, rpm2;
  
  delay(500);
  rpm2 = 0;
  for (int i = 0; i < BUFSIZE; i++) {
    rpm2 += countBuf2[i];
    //Serial.print(countBuf2[i]);
    //Serial.print(", ");
  }
  rpm2 = rpm2 / BUFSIZE;
  rpm2 = rpm2 * 60;

  delay(500);
  //Serial.print(". RPM: ");
  //Serial.println(rpm2);

  //Read commands
  cli();
  while (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (isDigit(incomingByte))
      inString += incomingByte;
    else{
      switch (incomingByte){
        case 'O'://Fan (O)ne: write to fan1
          fanComp1 = inString.toInt();
          Serial.print("O:");
          Serial.println(fanComp1);
          inString = "";
        break;
        case 'T'://Fan (T)wo: write to fan2
          fanComp2 = inString.toInt();
          Serial.print("T:");
          Serial.println(fanComp2);
          inString = "";
        break;
        case 'W'://W command: (W)hat is the device? Respond with ID
          Serial.println("1337");
        break;
        //case '\n'://newline: command done
        //  Serial.println("ok");
        //break;
        default://Invalid command: empty buffer and carry on (Error E1)
          Serial.println("E1");
          inString = "";
        break;
      }
    }


/*
    //Fan (O)ne: write to fan1
    else if (incomingByte == 'O') {
      fanComp1 = inString.toInt();
      Serial.print("f1:");
      Serial.println(fanComp1);
      inString = "";
    }
    //Fan (T)wo: write to fan2
    else if (incomingByte == 'T') {
      fanComp2 = inString.toInt();
      Serial.print("f2:");
      Serial.println(fanComp2);
      inString = "";
    }
    
    //W command: (W)hat is the device? Respond with ID
    else if (incomingByte == 'W')
      Serial.println("1337");
    
    //newline: command done
    else if (incomingByte == '\n')
      Serial.println("ok");

    //Invalid command: empty buffer and carry on (Error E1)
    else{
      Serial.println("E1");
      inString = "";
    }
*/
  }
  sei();
  
}

void rpmCall1() {
  fanRpmCount1++;
  fanRpmCount2++;
}
