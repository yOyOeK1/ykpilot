
#include <MsTimer2.h>

int led = 13;
int audioPin = A0;
int aMax = 0;
int aRead = 0;
int pPin = 8;
int mPin = 9;
int mosPin = 12;
int lPin = A1;
int loadOnArm = 0;


long firstTone;
long toneTime;
 

boolean apStatus = false;
int apDirection = 0;
int apDirOld = 0;


void setup() {         

  analogReference(INTERNAL);
  
  pinMode(led, OUTPUT);  
  //pinMode(mosPin, OUTPUT);
  //digitalWrite(mosPin, LOW);
  pinMode(pPin, OUTPUT);
  digitalWrite(pPin, LOW);
  pinMode(mPin, OUTPUT);
  digitalWrite(mPin,LOW);
  
  
  Serial.begin(9600);
  
  MsTimer2::set(100, takeChk);
  MsTimer2::start();
  
}

void ledOn(){
  digitalWrite(led, HIGH);
}

void ledOff(){
  digitalWrite(led, LOW);
}
 
long peakDetect(){
  while( analogRead(audioPin) > 25 ){}
  delay(2);
  while( analogRead(audioPin) < 15 ){}
  firstTone = millis();
  delay(2);
  while( analogRead(audioPin) > 25 ){}
  delay(2);
  while( analogRead(audioPin) < 15 ){}
  return millis()-firstTone;
  
}

int loadP(){
  return analogRead(lPin);
}
 
void takeChk(){
  if( (millis()-firstTone) > 40 ){
    apStatus = false;
    ledOff();
  }else{
    apStatus = true;
    ledOn();
  }
  
  loadOnArm = loadP();
  if( loadOnArm > 200 ){
    digitalWrite(mPin,HIGH);
    digitalWrite(pPin,HIGH);
  } else {
      
    if( apDirection == 0 || apStatus == false ){
      digitalWrite(mPin,HIGH);
      digitalWrite(pPin,HIGH);
    
    }else if( apDirection == 1 ){
      digitalWrite(mPin,HIGH);
      digitalWrite(pPin,LOW);
          
    }else if( apDirection == -1 ){
      digitalWrite(mPin,LOW);
      digitalWrite(pPin,HIGH);
        
    }
  }
  
  if( 0 ) {
    Serial.print(" s:");
    Serial.print(apStatus);
    Serial.print(" d:");
    Serial.print(apDirection);
    Serial.print(" m:");
    Serial.print(digitalRead(mosPin));
    Serial.print(" l:");
    Serial.print(loadOnArm);
    Serial.println();
  }
  
  apDirOld = apDirection;
}
 
// the loop routine runs over and over again forever:
void loop() {
  
  while( true ){    
      toneTime = peakDetect();
      
      if( toneTime <= 6 && toneTime >= 3 ){
        apDirection = 1;
        apStatus = true; 
      }else if( toneTime <= 25 && toneTime >= 16 ){
        apDirection = -1;
        apStatus = true;
      }else 
        apDirection = 0;
      
      if( 0 ){
        Serial.println(analogRead(lPin));
      }
      
      if( 0 ){
        Serial.println(toneTime);
      }
  }
  
}
