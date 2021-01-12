
#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'

float fError, fError_1 = 0, fError_2 = 0;
float kp = 0.8817, ki = 0.7234, kd = 2.689 / 1000000;
float ut, ut_1;
float Tm = 0.61 / 1000;
float ref = 1, fLecturaAux;
bool flag;
int iLectura, i = 0;
char buff[100], datos[100];
unsigned long entero;

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
        entero = atol(datos);
        fLecturaAux = entero / 100.0;
        fError = ref - fLecturaAux;
        ut = ut_1 + (kp + ki + kd) * fError - (2 * kd + kp) * fError_1 + kd * fError_2;

        if (ut > 5.0)
          ut = 5.0;
        /*
        if (ut < 0.0)
          ut = 0.0;
          */
        ut_1 = ut;
        fError_2 = fError_1;
        fError_1 = fError;
        entero = ut * 100;
        sprintf(buff, "%d\n", entero);
        Serial.print(buff);
        memset(datos, '\0', sizeof(datos));
        i = 0;
      }
      else
      {
        i++;
      }
    }
  }
}
