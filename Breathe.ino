/*Jonathan Hurwitz
 * 1-13-17
 * v0.01
 */

#include <SoftwareSerial.h>
SoftwareSerial BT(3,2);

//Pin Declarations
#define HR_in A4
#define BR_in A1
#define BT_out A6

//Constants for calibration
const int CAL_NUM = 5000;   //in ms??
const int ONE_SEC = 1000; //in ms

//Varying values for measured resistance of stretch sensor
int MIN_RES = 20000;
int cur_res = 0;
int val_being_read = 0;

void setup() {

  //Setup pins
  pinMode(HR_in, INPUT);  //heart rate
  pinMode(BR_in, INPUT);  //breath rate
  pinMode(BT_out, OUTPUT); //bluetooth

  //LED
  pinMode(13, OUTPUT);
  BT.begin(9600);
  BT.println("Welcome to Monitor v0.01");
  
  
  //Calibration stage
  for(int i = 0; i < CAL_NUM; i++){    
    //read resistor values (convert from analog val)
    cur_res = 42;
     
    //obtain min
    val_being_read = analogRead(BR_in);
    if(val_being_read < MIN_RES){
      MIN_RES = val_being_read;
    }
    
   // BT.println(MIN_RES);
   // BT.println("\n");
    
    //running average ?
  }
  
}

/*Process Data */
float processRawData(int type){
  int raw = analogRead(BR_in);
  int Vin = 5;
  float Vout = 0;
  float R1 = 10000;
  float R2 = 0;
  float buffer = 0;
  
//types: 1 = Vout, 2 = R_eq
  
  if(raw) {
    buffer= raw * Vin;
    Vout= (buffer)/1024.0;
    buffer= (Vin/Vout) -1;
    R2= R1 * buffer;

  //  BT.print("MIN_RES: ");
   // BT.println(MIN_RES);
   // BT.print("Vout: ");
   // BT.println(Vout);
   // BT.print("R2: ");
   // BT.println(R2);
  }
  
  //Return Vout
  if(type == 1){
    return Vout;
  }
  //Return R_eq
  else if(type == 2){ 
    return R2;
  }

}

/*Main Processing Loop*/

char input;


int HR = 0;
int BR = 0;

void loop() {
  //Read HR data
  HR = analogRead(HR_in);
 // BT.println("HR:");
 // BT.println(HR);
  
 
  //Read stretch data
  BR = analogRead(BR_in);
//  BT.println("BR: ");
  //BT.println(BR);





  delay(50);
  //Package into two bit groups 0xa<shit>a
//Check BT connection (send request and wait for reply)
  if(BT.available() > 0){
        //BT.println("BT available");
        input = BT.read();
        //Host requests HR (1)
        if(input == '1'){
          BT.println("This is HR \n");
        }
        //Host requests BR (2)
        else if(input == '2'){
          BT.println("This is BR \n");
        }
        else if(input == '3'){
          digitalWrite(13, HIGH);
        }
        else if(input == '4'){
          digitalWrite(13, LOW);
        }
        else if(input == '5'){
          BT.println(processRawData(1));
        }
        else if(input == '6'){
          BT.println(processRawData(2));
        }
        else{
          BT.println("Unknown request");
           // BT.println(processRawData(2));

        }


  }
}






