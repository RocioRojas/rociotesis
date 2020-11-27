


float cError,cErrorAnt=0.0,Kp=4.5187,Ki=627.4549,Kd=0.002,a,UdAnt=0.0,UiAnt=0.0,Up,Ui,Ud,Ut,Tm=0.61/1000,N=0;
int Ref=50;
float z,zant=0,zaux,u,g1,b1,y1,F;
float R=1.5;
int aux,Read, i=0;
float fAuxLectura;
char buff[100];

char Arredatos[100];

unsigned long entero;
bool flag = false;
void setup() {


//pinMode(3, OUTPUT);



a=Kd/(Kd+N*Tm);


Serial.begin(57600);

}

void loop() {

//if (Read==0x04){
//flag = true;
//}
//else if (Read==0x08)
//{
//  flag=false;
// }  

// if(flag)
if(Serial.available())
{
Read=Serial.read();
//Read=(analogRead(A0))/4;

Arredatos[i]=Read;



if (Arredatos[i]=='\n'){
entero=atol(Arredatos);
fAuxLectura=entero/100.0;
fAuxLectura*=255.0/5.0; 
   
cError=Ref-fAuxLectura;

//cError=Ref-Read;
//Serial.println(cError);
Up=Kp*cError;
 
Ud=Kd*(cError-cErrorAnt)/Tm;
Ui=UiAnt+Ki*cError*Tm;
Ut= Up+Ud+Ui;
//    Serial.println(Up);
//    Serial.println(Ud);
//    Serial.println(Ui);
//    Serial.println(Ut);
if (Ut>255.0) Ut=255.0;
if (Ut<0.0) Ut=0.0;
cErrorAnt=cError;
UdAnt=Ud;
UiAnt=Ui;

// Ut=999.9916;
entero=Ut*100;
//Serial.print(entero);
sprintf(buff,"%d\n",entero) ;
//Serial.println("Datos: ");
//Serial.print(Arredatos);
//analogWrite(3,Ut);
//Serial.println(convertirFloat);
entero=fAuxLectura*100;

Serial.print(buff);


memset(Arredatos, '\0', sizeof(Arredatos));
i=0;
}
else{
i++;
}

//Serial.print(Read) ;
//Serial.write(57);

}


//delayMicroseconds(8000);       
}
