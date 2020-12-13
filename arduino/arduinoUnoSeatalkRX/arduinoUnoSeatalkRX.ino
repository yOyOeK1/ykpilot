
#include <SoftwareSerial9.h>
#include <DHT.h>
#include <MsTimer2.h>

#define SEATALK_RX 6
#define SEATALK_TX 7

#define DHTPIN 2
#define DHTTYPE DHT22


const int nTx = 9;
const int nRx = 8;
const int led = LED_BUILTIN;

SoftwareSerial9 SerialO(SEATALK_RX, SEATALK_TX,true);
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  pinMode(led, OUTPUT);
  SerialO.begin(4800);
  Serial.begin(115200);
  dht.begin();
  MsTimer2::set(6789,dhtChk);
  delay(200);
  MsTimer2::start();
}

int charN = 0;
char nc;
char buf[64];

uint8_t stBuf[16];
int stCharN = 0;

void dhtChk(){
	float h = dht.readHumidity();
	// Read temperature as Celsius (the default)
	float t = dht.readTemperature();
	// Read temperature as Fahrenheit (isFahrenheit = true)
	float f = dht.readTemperature(true);
	
	if (isnan(h) || isnan(t) || isnan(f)) {
		Serial.println(F("DHT error"));
		return;
	}
	Serial.print("{'dht':{'humidity':");
	Serial.print(h);
	Serial.print(",'C':");
	Serial.print(t);
	Serial.print(",'F':");
	Serial.print(f);
	Serial.println("}}");
	
}
/*
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
*/
char stChar;
int stNot = 0;
void stGot(){
	if( stCharN > 0){
		stBuf[stCharN] = 0;
		Serial.print("{'seatalk':'");
		for( int c=0; c<stCharN;c++){
			Serial.print(stBuf[c],HEX);
			Serial.print(',');
			
		}
		Serial.println("'}");
		
		//Serial.println((makeWord( stBuf[3], stBuf[2] )*0.3048) );
		
	}
	
	stCharN = 0;
	stBuf[0] = 0;
	stNot = 0;
}

void stRead(){
	if( SerialO.available() ){
		stBuf[stCharN++] = ((char)(~SerialO.read()));
		stNot = 0;
	}else{
		delay(1);
		stNot++;
	}
	
	if( stNot > 3 || stCharN >= 31 ){
		stGot();
		
	}
}

bool st_isBusy() {
	//return true;
	int c;
	for (c = 0; c < 255; c++) {
		if ( digitalRead(SEATALK_RX) == 0)
		//delay(5);
			stRead();
		else
			return false;
	}
	return true;
}

void readSeatalk(){
	stRead();
	
	
}

long iter = 0;
long hc = 0;

void loop() {
  iter++;
  
  //Serial.println('.');
  stRead();
  
  
  
	  
  //delay(1);
  
  /*
  
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
  */
  
  
  
}
