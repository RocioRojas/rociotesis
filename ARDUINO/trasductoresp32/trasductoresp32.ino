#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'

int iLectura, lect, i = 0, a;
bool flag;
char buff[100], datos[100];
unsigned long entero;
float fLecturaAux, ut;

void setup()
{
  pinMode(13,OUTPUT);
  Serial.begin(9600);
  digitalWrite(13,HIGH);
}

void loop()
{

  if (Serial.available())
  {
    iLectura = Serial.read();
    if (iLectura == CMD_ABRIR_COMUNICACION)
    {
      flag = true;
      digitalWrite(13,LOW);
      ut = 0;
      sprintf(buff, "%d\n", ut);
      Serial.print(buff);
    }
    else if (iLectura == CMD_CERRAR_COMUNICACION)
    {
      flag = false;
      digitalWrite(13,HIGH);
    }
    if (flag == true && iLectura != CMD_ABRIR_COMUNICACION)
    {
      
      datos[i] = iLectura;
      if (datos[i] == '\n')
      {
        entero = atol(datos);
        fLecturaAux = entero / 100.0;
        
        memset(datos, '\0', sizeof(datos));
      }
    }
  }

  if (flag == true)
  {

    lect = ((analogRead(34)) * 3.3 * 100) / 4095;

    sprintf(buff, "%d\n", lect);
    Serial.print(buff);
  }
  dacWrite(25, fLecturaAux * 255 / 3.3);
  //  delayMicroseconds(610);
}
