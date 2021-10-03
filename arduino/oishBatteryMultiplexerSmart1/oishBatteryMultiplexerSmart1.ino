


#include <DHT.h>

int swb0 = 7;
int swb1 = 6;
int swdcdc = 5;
int swNaN = 4;
int swOn = LOW;
int swOff = HIGH;

int batteryNow = -1;
int swOutNow = -1;
int b0g = A5;
int b01 = A4;
int b1p = A3;
int outStage1 = A2;
int outStage2 = A1;
int sen2 = A0;
int offsets[6];
bool swNaNstatus = false;

int b0g_=0;
int b01_=0;
int b1p_=0;
  





int bmOnHH = 0;
int bmOnMM = 1;
int bmOnSS = 10;


int bmOnHHl = 0;
int bmOnMMl = 0;
int bmOnSSl = 0;
int bmStatus = 0;
bool bmWork = true;
int bmBatSel = 1;
int bmOutStage1 = 0;
int arb0g = 0;
int arb01 = 0;
int arb1p = 0;
int arouts1 = 0;

int arbat1 = 0;
int arbat2 = 0;

int arb0g1 = 0;
int arb011 = 0;
int arb1p1 = 0;
int arouts11 = 0;

int arb0g2 = 0;
int arb012 = 0;
int arb1p2 = 0;
int arouts12 = 0;











#define DHTPIN 8
#define DHTTYPE DHT11
DHT dht( DHTPIN, DHTTYPE );


#include <TaskScheduler.h>
void dummyRaport();
void niceRaport();
void serialAction();
void dhtIter();
void batMux();

void t2Callback();
void t3Callback();

//Tasks
Task t4();
Task t_dummy(200, 3, &dummyRaport);
Task t_serial(188, TASK_FOREVER, &serialAction);
Task t_nice(5000, TASK_FOREVER, &niceRaport);
Task t_dht(10000, TASK_FOREVER, &dhtIter);
Task t_batMux(1000, TASK_FOREVER, &batMux);
//Task t2(3000, TASK_FOREVER, &t2Callback);
//Task t3(5000, TASK_FOREVER, &t3Callback);

Scheduler runner;






void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  offsets[0] = 0;
  offsets[1] = -4;
  offsets[2] = -1;
  offsets[3] = 1;
  offsets[4] = 4;
  offsets[5] = -2;
  
  pinMode(LED_BUILTIN, OUTPUT);

  pinMode( swb0, OUTPUT );
  digitalWrite( swb0, swOff);
  pinMode( swb1, OUTPUT );
  digitalWrite( swb1, swOff);
  pinMode( swdcdc, OUTPUT );
  digitalWrite( swdcdc, swOff);
  pinMode( swNaN, OUTPUT );
  digitalWrite( swNaN, swOff);


  Serial.begin(57600);

  dht.begin();

  
  runner.init();
  //runner.addTask(t_dummy);
  runner.addTask(t_serial);
  runner.addTask(t_nice);
  runner.addTask(t_dht);
  runner.addTask(t_batMux);
  delay(500);
  //t_dummy.enable();
  t_serial.enable();
  t_nice.enable();
  t_dht.enable();
  t_batMux.enable();
  
  

  
}
void dummyRaport(){
	Serial.println("dummyRaport");
	
}

void dhtIter(){
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);
  
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("{'dht': 'error'}"));
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


void p(String n){
	Serial.println(n);
}

// -------------  MULTIPLEXER START


void batMuxswTo1(){
	digitalWrite( swb0, swOff);
	digitalWrite( swb1, swOff);
}
void batMuxswTo2(){
	digitalWrite( swb0, swOn);
	digitalWrite( swb1, swOn);
}
void batMuxswOutOn(){
	digitalWrite( swdcdc, swOn);
}
void batMuxswOutOff(){
	digitalWrite( swdcdc, swOff);
}
void batMuxAdcRaw(){
	delay(1);
	arb0g = analogRead(b0g);
	delay(1);
	arb01 = analogRead(b01);
	delay(1);
	arb1p = analogRead(b1p);
	delay(1);
	arouts1 = analogRead(outStage1);
}





/*
0 - start
1 - sw to battery 1
2 - sensing make notes
3 - sw to battery 2
4 - sensing make notes , make sw to bank
5 - sw on output
6 - wait
 */

void bmRaportSta(){
	p( "{'batMuxSta':{"\
			"'status':"+String(bmStatus)+","\
			"'on':{"
				"'hh':"+String(bmOnHH)+","
				"'mm':"+String(bmOnMM)+","
				"'ss':"+String(bmOnSS)+\
			"},"
			"'left':{"
							"'hh':"+String(bmOnHHl)+","
							"'mm':"+String(bmOnMMl)+","
							"'ss':"+String(bmOnSSl)+\
						"},"
			"'batSel':"+String(bmBatSel)+","
			"'outStage1':"+String(bmOutStage1)+","
			"'arb0g':"+String(arb0g)+","
			"'arb01':"+String(arb01)+","
			"'arb1p':"+String(arb1p)+","
			"'arouts1':"+String(arouts1)+\	
		"}}");
}

void bmRaportWait(){
	p( "{'batMuxWait':{"\
			"'on':{"
				"'hh':"+String(bmOnHH)+","
				"'mm':"+String(bmOnMM)+","
				"'ss':"+String(bmOnSS)+\
			"},"
			"'left':{"
							"'hh':"+String(bmOnHHl)+","
							"'mm':"+String(bmOnMMl)+","
							"'ss':"+String(bmOnSSl)+\
						"}"
			
		"}}");
}
void bmRaportBat12(){
	p("{'batMuxBat12':{"\
		"'arbat1':"+String(arbat1)+","
		"'arbat2':"+String(arbat2)+\
		"}}");
}

int bmRaportSkip = 2;
int bmRaportIter = 0;
void batMux(){
	if( (bmRaportIter%bmRaportSkip) == 0 )
		bmRaportSta();
	
	if( bmStatus == 0 ){
		p("0 - start sequence");
		batMuxswOutOff();
	}else if( bmStatus == 1 ){
		p("1 - sw to battery 1");
		batMuxswTo1();
		bmBatSel = 1;
	}else if( bmStatus == 2 ){
		p("2 - sensing battery 1, make notes");
		batMuxAdcRaw();
		arb0g1 = arb0g;
		arb011 = arb01;
		arb1p1 = arb1p;
		arouts11 = arouts1;
		arbat1 = arouts1;
	}else if( bmStatus == 3 ){
		p("3 - sw to battery 2");
		batMuxswTo2();
		bmBatSel = 2;
	}else if( bmStatus == 4 ){
		p("4 - sensing battery 2, make notes");
		batMuxAdcRaw();
		arb0g2 = arb0g;
		arb012 = arb01;
		arb1p2 = arb1p;
		arouts12 = arouts1;
		arbat2 = arouts1;
		bmRaportBat12();
		
		p("  - adc for bat 1:"+String(arouts11)+" bat 2:"+String(arouts12));
		if( arouts11 > arouts12 ){
			p("... use battery 1 for output");
			batMuxswTo1();
		}else{
			p("... use battery 2 for output");
			batMuxswTo2();
		}
		
	}else if( bmStatus == 5 ){
		p("5 - sw output On");
		//batMuxswOutOn();
		bmOutStage1 = 1;
	}else if( bmStatus == 6 ){
		p("6 - start counter");
		
		bmOnHHl = bmOnHH;
		bmOnMMl = bmOnMM;
		bmOnSSl = bmOnSS;
	}else if( bmStatus == 7 ){
		p("7 - waiting for end of cycle..."\
			"("+String(bmOnHH)+":"+String(bmOnMM)+":"+String(bmOnSS)+") "+\
			"left: "+\
			"("+String(bmOnHHl)+":"+String(bmOnMMl)+":"+String(bmOnSSl)+")"
			);
		if( (bmRaportIter%bmRaportSkip) == 0 )
			bmRaportWait();
			batMuxAdcRaw();

		
		if( bmOnSSl == 0 && bmOnMMl == 0 && bmOnHHl == 0 ){
			p("end of waiting !");
		}else
			bmStatus = 6;
		
		bmOnSSl-=1;
		
		if( bmOnSSl<0 ){
			bmOnMMl-=1;
			bmOnSSl = 59;
		}
		if( bmOnMMl<0 ){
			bmOnHHl-=1;
			bmOnMMl = 59;
		}
		
		
	}else if( bmStatus == 8 ){
		p("8 - sw off output stage 1");
		batMuxswOutOff();
		bmOutStage1 = 0;
	}else if( bmStatus == 9 ){
		p("9 - end work :)");
		
		bmOnHHl = 0;
		bmOnMMl = 0;
		bmOnSSl = 0;
		
		if( bmWork )
			bmStatus = -1;
		else
			bmStatus = 8;
		
	}else{
		p("battery Multiplexer status("+String(bmStatus)+")");	
	}

	if( bmWork ) 
		bmStatus++;
	
	bmRaportIter++;
	
	
}

// -------------  MULTIPLEXER END


void swTest(){
  Serial.println("swTest ----------------");
  digitalWrite( swb0, swOn);
  digitalWrite( swb1, swOn);
  digitalWrite( swdcdc, swOn);
  digitalWrite( swNaN, swOn);
  
  delay(1000);                       // wait for a second
  
  digitalWrite( swb0, swOff);
  digitalWrite( swb1, swOff);
  digitalWrite( swdcdc, swOff);
  digitalWrite( swNaN, swOff);
}


int adcReadAvg( int apin ){
  return (
    analogRead( apin) +
    analogRead( apin) +
    analogRead( apin) \
    )/3;
}

void adcToH( int ap ){
  int a = analogRead( ap );
  Serial.print("{");
  Serial.print("'raw':");
  Serial.print(a);
  Serial.print(",");
  //Serial.print("____");
  if( ap == b0g ){
    a-= offsets[5];
  }else if( ap == b01 ){
    a-= offsets[4];
  }else if( ap == b1p ){
    a-= offsets[3];
  }else if( ap == outStage1 ){
    a-= offsets[2];
  }else if( ap == outStage2 ){
    a-= offsets[1];
  }
  Serial.print("'now':");
  Serial.print(a);
  Serial.print(",");
  float res = (1200.000/1024.000)*(float(a))-600.000;
  //Serial.print( ap );
  Serial.print("'volts':");
  Serial.print( res );
  Serial.print("}");
  
}

void adcRaw(){
  Serial.print("{'adcRaw':{");
  Serial.print("'a0':");
  adcToH( A0 );
  Serial.print(",'a1':");
  adcToH( A1 );
  Serial.print(",'a2':");
  adcToH( A2 );
  Serial.print(",'a3':");
  adcToH( A3 );
  Serial.print(",'a4':");
  adcToH( A4 );
  Serial.print(",'a5':");
  adcToH( A5 );
  Serial.println("}}");
  
}

void adcNice(){
  Serial.print("{'adcNice':{");
  Serial.print("'b0g':  ");
  adcToH( b0g );
  
  Serial.print(",'b01':  ");
  adcToH( b01 );
  
  Serial.print(",'b1p':  ");
  adcToH( b1p );
  
  Serial.print(",'outStage1':  ");
  adcToH( outStage1 );
  
  Serial.print(",'outStage2':  ");
  adcToH( outStage2 );
  
  Serial.println("}}");
}



int clickTimesIn( int clicks, int hz = 2 ){
  return 0;
  for(int c=clicks; c>0; c-- ){
    if( swNaNstatus ){
      digitalWrite( swNaN, swOff);
      swNaNstatus = false;
    }else{
      digitalWrite( swNaN, swOn );
      swNaNstatus = true; 
    }
    delay(1000/hz);
  }
}

void waitMinutes(int minutes){
  for(; minutes>0;minutes--){
    delay(60000);
  }
}

void b0b1Test(){
  digitalWrite( swb0, swOff);
  digitalWrite( swb1, swOff);
  batteryNow = 0;
  delay(1000);
  digitalWrite( swdcdc, swOn);
  swOutNow = 1;
  waitMinutes(10);
  digitalWrite( swdcdc, swOff);
  swOutNow = 0;
  delay(1000);
  
  digitalWrite( swb0, swOn);
  digitalWrite( swb1, swOn);
  batteryNow = 1;
  delay(1000);
  digitalWrite( swdcdc, swOn);
  swOutNow = 1;
  waitMinutes(5);
  digitalWrite( swdcdc, swOff);
  swOutNow = 0;
  delay(1000);
  
  
}


void niceRaport(){
  adcRaw();
  adcNice();
  
}

int bmpiter = 0;
void basicMultiplexer(){
  int onFor = 2;// min
  long w = 1000;
  

  //Serial.print("o.O basic multiplexer iter: ");
  Serial.println(bmpiter++);
  \ 

  //Serial.println("- battery test...");
  
  digitalWrite( swb0, swOff);
  digitalWrite( swb1, swOff);
  batteryNow = 0;
 
  
  delay(w);
  int a = analogRead(outStage1);
  digitalWrite( swb0, swOn);
  digitalWrite( swb1, swOn);
  batteryNow = 1;


 
  delay(w);
  int b = analogRead(outStage1);

  //Serial.println("  - results from test:");
  //Serial.print("    - battery 0: ");
  //Serial.println(a);
  
  //Serial.print("    - battery 1: ");
  //Serial.println(b);

  //Serial.print("- setting multiplexer to battery: ");
  clickTimesIn( 3, 6 );
  if( a >= b ){
    Serial.println(0);    
    digitalWrite( swb0, swOff);
    digitalWrite( swb1, swOff);
    batteryNow = 0;
    clickTimesIn( 1, 2 );
  }else{
     Serial.println(1);    
    digitalWrite( swb0, swOn);
    digitalWrite( swb1, swOn);
    batteryNow = 1;
    clickTimesIn( 2, 2 );
  }
  
  delay(w);

  digitalWrite( swdcdc, swOn);
  swOutNow = 1;

  


  delay(w);
  Serial.println("- reading adc values for reference ...");
  delay(w);
  b0g_ = analogRead( b0g );
  delay(w);
  b01_ = analogRead( b01 );
  delay(w);
  b1p_ = analogRead( b1p );
  Serial.println("  readings are: ");
  Serial.println( b0g_ );
  Serial.println( b01_ );
  Serial.println( b1p_ );

  int adcSame = 0; 
  while( true ){
    Serial.print("- goind waint now for ");
    Serial.println(onFor);
    waitMinutes(onFor);

    Serial.println("- waining done ! chk status on adc ");
    adcSame = 0;
    
    if( analogRead( b0g ) == b0g_ ){
      Serial.println("b0g ok !");
      adcSame++;  
    } 
    if( analogRead( b01) == b01_ ){
      Serial.println("b01 ok !");
      adcSame++;
    }
    if( analogRead( b1p ) == b1p_ ){
      Serial.println("b1p ok !");
      adcSame++;
    }
    if( adcSame != 3) {
      Serial.println("- buuu no optimalization loop  :( klik :(");
      break;
    }

  }


  
  
  digitalWrite( swdcdc, swOff);
  swOutNow = 0;
  delay(w);

  Serial.println("Iter done...");
}


bool cmdLed(String cmd){
	if(cmd.substring(0,4) == "led:"){
		if(cmd.substring(4,5)=="1"){
			digitalWrite(LED_BUILTIN, HIGH);
			return true;
		}else if(cmd.substring(4,5)=="0"){
			digitalWrite(LED_BUILTIN, LOW);
			return true;
		}
	}
	return false;
}


String cmd = "";
char nc;
char buf[33];
int charN = 0;

int serialGot(){
	Serial.print("serialGot:");
	Serial.print(buf);
	Serial.println("<<");

	if( buf[0] == '$' ){
		Serial.println("got command, processing ...");
		Serial.print("command:");
		cmd = String(buf).substring(1);
		Serial.println(cmd);
		
		if( cmdLed(cmd) )
			return 0;
		
	}
		
	return -1;

}


void serialAction(){
	while(Serial.available()){
		nc = char(Serial.read());
		buf[charN] = nc;
		if( nc == '\n' || charN > 32 ){
			buf[charN] = 0;
			Serial.println("got Line");
			serialGot();
			charN=0;
		}else
			charN++;
	}
}



// the loop function runs over and over again forever
void loop() {
  //delay(500); 

  runner.execute();
  //adcRaw();
  //adcNice();

  //basicMultiplexer();
  
  //b0b1Test();
  //digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)

  //swTest();
  
  //delay(100); // wait for a second
}
