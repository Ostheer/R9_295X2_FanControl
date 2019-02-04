// pin definitions
#define FAN0 9
#define FAN1 10
#define FAN2 11
#define FAN0INT 2
#define FAN1INT 3
//#define FAN2INT hahadieiserniet
//max value for soft pwm
#define PWMCYC 3000

//For the soft PWM (fan0 has normal pwm)
int fanCount1 = 0;
int fanComp1 = PWMCYC;
int fanCount2 = 0;
int fanComp2 = PWMCYC;

//Serial communication
char incomingByte = 0;
String inString = "";

void setup() {
  cli();
  //set timer2 interrupt
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
  sei();

  pinMode(FAN0, OUTPUT);
  pinMode(FAN1, OUTPUT);
  pinMode(FAN2, OUTPUT);

  pinMode(FAN0INT, INPUT);
  pinMode(FAN1INT, INPUT);
  digitalWrite(FAN0INT,HIGH);
  digitalWrite(FAN1INT,HIGH);

  analogWrite(FAN0, 200);
  
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


void loop() {
  int rpm;
  
  cli();
  while (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (isDigit(incomingByte))
      inString += incomingByte;
    else{
      switch (incomingByte){
        case 'Z'://Fan (Z)ero: write to fan0
          analogWrite(FAN0,inString.toInt());
          Serial.print("Z:");
          Serial.println(inString);
        break;
        case 'O'://Fan (O)ne: write to fan1
          fanComp1 = inString.toInt();
          Serial.print("O:");
          Serial.println(fanComp1);
        break;
        case 'T'://Fan (T)wo: write to fan2
          fanComp2 = inString.toInt();
          Serial.print("T:");
          Serial.println(fanComp2);
        break;
        case 'W'://W command: (W)hat is the device? Respond with ID
          Serial.println("1337");
        break;
        case 'R'://R command: (R)PM of a fan.
          rpm = getRpm(inString.toInt());
          Serial.print("R:");
          Serial.println(rpm);
        break;
        default://Invalid command: empty buffer and carry on (Error E1)
          Serial.println("E1");
        break;
      }
      inString = "";
    }
  }
  sei();
  
  delay(500);
}

int getRpm(int fan) {
  unsigned long pulseDuration;
  unsigned int rpm = 0;

  //Fan2 doesn't have rpm sensor (not enough external interrupt pins)
  for(int i = 0; i < 5; i++){
    switch (fan){
      case 0:
        pulseDuration = pulseIn(FAN0INT, LOW);
        break;
      case 1:
        pulseDuration = pulseIn(FAN1INT, LOW);
        break;
      default:
        return 0;
    }
    
    double frequency = 1000000/pulseDuration;
    rpm+= frequency;
    delay(75);
  }
  return rpm/2*60/5;
}
