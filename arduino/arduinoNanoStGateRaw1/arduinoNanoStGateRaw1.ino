#include <Alt9SoftSerial.h>
#include <SoftwareSerial9.h>

#define SEATALK_RX 8
#define SEATALK_TX 9
Alt9SoftSerial SerialI(SEATALK_RX, NULL);
SoftwareSerial9 SerialO(NULL, SEATALK_TX, true);




String uartMsg;
String uartOut;
bool stSending = false;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  SerialO.begin(4800);
  SerialO.stopListening();
  SerialI.begin(4800);
  digitalWrite(SEATALK_TX, LOW);
  
  Serial.begin(57600);
  while (!Serial);
  Serial.println(F("hello :)"));
  Serial.println(F("arduino Nano Seatalk Gate Raw v1"));
  
  uartMsg = String("");
  uartOut = String("");

}

void blink(void) {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(100);              // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW

}


bool checkStBusy() {
  //return true;
  for (int c = 0; c < 255; c++) {
    if ( digitalRead(SEATALK_RX) == 0)
      delay(5);
    //readUSART();
    else
      return false;
  }
  return true;
}


void printSt(int len, ...) {
  stSending = true;
  checkStBusy();
  //digitalWrite(SEATALK_TX, HIGH);
  va_list st;
  va_start(st, len);
  for (int i = 0; i < len; i++)
    SerialO.write9(va_arg(st, int));
  va_end(st);

  //digitalWrite(SEATALK_TX, LOW);
  stSending = false;
 }

int getCheckSum(String string) {
  int XOR = 0;
  for (int i = 0; i < string.length(); i++)
    XOR = XOR ^ string[i];

  return XOR;
}
void printWithCS(String msg) {
  Serial.print(msg);
  Serial.print("*");
  Serial.println(String(getCheckSum(msg), HEX));
}

void stMsgParse( int len, byte *msg){
  uartOut = "";
  for(int c=0; c<len; c++)
    uartOut.concat( String( msg[c], HEX )+',' );
    
  printWithCS("{'stk':'"+uartOut+"'}");
}


long stMiss = 0;
int stc = 0;
byte st[32];
int stb = 0;
long v0,v1;
boolean readSeaTalk() {
  if( stSending )
    return false;
  
  if (SerialI.available ()) {
    stb = (SerialI.read());
    //Serial.println(stb,HEX);
    if (stb & 0x100) {
      
      if(stc>1){
        stMiss = 0;
        stMsgParse( stc, st );      
      }
      
      stc = 0 ;
    }
    st[stc++] = stb ;
    stMiss = 0;
    
    if ( stc > 30 )
      stc = 0;

  }else if( stc>1 ){
    if(stMiss>490){
        stMsgParse( stc, st );   
        stc = 0;  
        stMiss=0;
      }
    
  }
  stMiss++;
  

}


uint16_t wTempI = 0;
void uartMsgParse(String msg) {
  //Serial.println("uart msg parse");
  //Serial.println(msg);

  if( msg == "?"){
    Serial.println(F("-------- help ---------"));
    Serial.println(F("? - for help"));
    Serial.println(F("-------- develop ---------"));
    Serial.println(F("stq - ask all devices in seatalk to identyfy theme selfs")); 
    Serial.println(F("2st:x,y,....., - send to seatalk"));
    Serial.println(F("  examp: 2st:a4,2,0,0,0, - query for identyfy devices in network"));
    Serial.println(F("  examp: 2st:20,1,85,0, - speed ower water 13.3 kts"));
    Serial.println(F("echo:x - x is what to print on serial"));
    Serial.println(F("lamp:x - x[0...3] is what to print on serial"));
    Serial.println(F("echoC:x - x is what to print on serial with check sum"));    
    Serial.println(F("ping - make ping pong on uart"));
    Serial.println(F("led:x - [1|0] led on arduino"));
    Serial.println(F("wait - wait 5 sec with led on"));    
    Serial.println(F("t1 - send some water temp"));
    Serial.println(F("d1 - send some depth"));

  }else if(msg.substring(0,5) == "lamp:"){
    int strength = msg.substring(5).toInt();
    //Serial.println(strength);
    if( strength == 0 )
      strength = 0;
    else if( strength == 1 )
      strength = 0x04;
    else if( strength == 2 )
      strength = 0x08;
    else if( strength == 3 )
      strength = 0x0c;
    printSt( 3, 0x180, 0x00, strength );

  }else if( msg == "stq"){
    printSt( 5, 0x1a4, 0x02, 0x00, 0x00, 0x00 );
    //{'stk':'a4,12,70,2,2,'}*2d - st60 speed
    //{'stk':'a4,12,73,7,0,'}*29 - st60 wind

  }else if(msg.substring(0,4) == "2st:"){
    //Serial.println( msg.substring(4));
    msg = msg.substring(4);
    char toS[15];
    String ss = "";
    int c =0;
    int ts = 0;
    for (uint8_t i = 0, ic = msg.length(); i < ic; i++) {
      if ( msg[i] == ',' ) {
        ss = msg.substring(c, i);
        ts = (int)(strtol( &ss[0], NULL, 16));
        if ( c == 0 )
          ts += 0x100;

        SerialO.write9(ts);
        //Serial.println(ts,HEX);
        c = i + 1;
      }
    }

  }else if(msg.substring(0,5) == "echo:"){
    Serial.println(String(msg.substring(5)));

  }else if(msg.substring(0,6) == "echoC:"){
    printWithCS(String(msg.substring(6)));
  
    
  }else if( msg == "ping"){
    printWithCS("pong");
    
  }else if( msg.substring(0,4) == "led:"){
    if(msg.substring(4,5)=="1")
      digitalWrite(LED_BUILTIN, HIGH);
    else if(msg.substring(4,5)=="0")
      digitalWrite(LED_BUILTIN, LOW);
    
  }else if( msg == "wait"){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(5000);
    digitalWrite(LED_BUILTIN, LOW);
    
  }else if( msg == "t1"){
    Serial.println("send water temp");
    printSt( 4, 0x127, 0x01, char( (wTempI)&0xff), char( (wTempI>8)&0xff) );
    wTempI++; 
      
  }else if( msg == "d1"){
    Serial.println("send depth");
    printSt( 5, 0x100, 0x02, 0x60, char( (wTempI)&0xff), char( (wTempI>8)&0xff) );
    wTempI++; 
  
  }
  
}

char uartc;
bool readUART() {
  while (Serial.available()) {
    uartc = Serial.read();
    // blink();
    if ( (uartc == '\n') || (uartc == '\r') || uartMsg.length() >= 100) {
      if ( uartMsg.length() == 0 )
        return false;
      else
        return true;
    }
    uartMsg += String((char)(uartc));
  }
  return false;
}

int iter = 0;
long currentMillis;
long lastT = 0;
void loop() {
  currentMillis = millis();

  readSeaTalk ();

  if ( readUART() != NULL ) {
    uartMsgParse(uartMsg);
    uartMsg = "";
  }


  // to be able to ingage autopilot X500 raymarine series it's pretending st6001+
  if( currentMillis > lastT ){
    lastT = currentMillis + 1990;
    printSt( 3, 0x190,0x00,0x03);
  }
  
  
 
}
