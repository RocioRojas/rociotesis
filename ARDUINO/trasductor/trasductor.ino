#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'

// configuracion de pines
#define pin0 2
#define pin1 3
#define pin2 4
#define pin3 5
#define pin4 6
#define pin5 7
#define pin6 8
#define pin7 9

int iLectura, lect, i = 0;
bool flag;
char buff[100], datos[5];
char *ptr;
unsigned long entero;
float fLecturaAux, ut;
void setup()
{

  Serial.begin(115200);
}

void loop()
{

  if (Serial.available())
  {
    iLectura = Serial.read();
    if (iLectura == CMD_ABRIR_COMUNICACION)
    {
      flag = true;
      ut = 0;
      sprintf(buff, "%d\n", ut);
      Serial.print(buff);
    }
    else if (iLectura == CMD_CERRAR_COMUNICACION)
    {
      flag = false;
    }
    if (flag == true && iLectura != CMD_ABRIR_COMUNICACION)
    {
      datos[i] = iLectura;
      if (datos[i] == '\n')
      {
        entero = strtol(datos, &ptr, 10);
        fLecturaAux = entero * 0.01;

        dacWrite(25, fLecturaAux * 255 * 0.30303);
        i = 0;
        memset(datos, 0, 5);
      }
      else
      {
        i++;
      }
    }
  }
  if (flag == true)
  {

    lect = ((analogRead(34)) * 3.3) * 0.0244; // (100/ 2095)

    sprintf(buff, "%d\n", lect);
    Serial.print(buff);
  }
}
