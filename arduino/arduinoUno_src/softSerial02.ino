
#include <SoftwareSerial.h>


// set pin 10 as the slave select for the digital pot:
const int nTx = 9;
const int nRx = 8;
const int led = LED_BUILTIN;

SoftwareSerial nSerial(nRx, nTx);

void setup() {
  // set the slaveSelectPin as an output:
  pinMode(led, OUTPUT);
  nSerial.begin(115200);
  Serial.begin(115200);
}

int charN = 0;
char nc;
//int waitInRow = 0;
char buf[64];

void gotMsg(){
  Serial.println("got all line !");
  buf[charN] = 0;
  Serial.println(buf);
  charN = 0;
 // waitInRow = 0;
  
}

void readUART(){

   
  
  if(nSerial.available()){
    //waitInRow = 0;
    nc = char(nSerial.read());
    buf[charN] = nc;
    Serial.print(nc);
    if( nc == "\n" ){
      gotMsg();
    }
    charN++;
  }
  
  //waitInRow++;

  if( charN >= 64 ){
    charN = 0;
    //waitInRow = 0;
  }
  
}


long iter = 0;
void loop() {
  iter++;
  //Serial.println(iter);
  if( (iter % (long)40000) == 0 ){
    Serial.println(">");
    nSerial.print("arduino sais hello !\n");
    //iter = 0;
  }
  //nSerial.println(iter);
  if( nSerial.available() ){
    readUART();
  }else{
    //Serial.println("n:- - -");
    //delay(2);
  }
  
  
  
}
