
#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'

float cError,cErrorAnt=0.0,Kp=0.8817,Ki=40.96,Kd=2.689/1000000,a,UdAnt=0.0,UiAnt=0.0,Up,Ui,Ud,Ut,Tm=0.61/1000,N=0,cError_2=0,Ut_1=0;
float Ref=0.98;
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


Serial.begin(115200);

}

void loop() {
    
    
    if(Serial.available())
    {
        Read=Serial.read();
        //Read=(analogRead(A0))/4;
        if (Read== CMD_ABRIR_COMUNICACION){
          flag = true;
          Ut=0;
          sprintf(buff,"%d\n",Ut) ;
          Serial.print(buff);
        }
        else if (Read== CMD_CERRAR_COMUNICACION)//
        {
          flag = false;
        }  
        
        if( flag == true && Read != CMD_ABRIR_COMUNICACION  ){
          Arredatos[i]=Read; 
          
          if (Arredatos[i]=='\n'){
            entero=atol(Arredatos);
            fAuxLectura=entero/100.0;
            //fAuxLectura*=255.0/5.0; 
               
            cError=Ref-fAuxLectura;
            
            //cError=Ref-Read;
            //Serial.println(cError);
            
             
            Ud=Kd*(cError-cErrorAnt)/Tm;
            Ui=Ki*cErrorAnt*Tm+Ki*cError*Tm;
            Ut= Ut_1+(Kp+Ki+Kd)*cError-(2*Kd+Kp)*cErrorAnt+Kd*cError_2;
            //    Serial.println(Up);
            //    Serial.println(Ud);
            //    Serial.println(Ui);
            //    Serial.println(Ut);
            if (Ut>5.0) Ut=5.0;
            if (Ut<0.0) Ut=0.0;
            cError_2=cErrorAnt;
            cErrorAnt=cError;
            Ut_1=Ut;
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
    }
}

//delayMicroseconds(8000);       
