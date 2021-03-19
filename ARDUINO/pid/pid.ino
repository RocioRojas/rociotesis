
#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'
// configuracion de pines
#define pin0  4
#define pin1  0
#define pin2  2
#define pin3 14
#define pin4 12
#define pin5 13
#define pin6 15
#define pin7 3
#define bitEntrada 5
float fError, fError_1 = 0, fError_2 = 0;
float kp = 0.8817, ki = 0.7234, kd = 2.689 / 1000000;
float ut, ut_1;
float Tm = 0.61 / 1000;
float ref = 1, fLecturaAux;
bool flag;
int iLectura, i = 0;
char buff[100], datos[5];
char *ptr;
unsigned long entero;
void writeBin(long valor);

void setup()
{
  pinMode(pin0, OUTPUT);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  pinMode(pin3, OUTPUT);
  pinMode(pin4, OUTPUT);
  pinMode(pin5, OUTPUT);
  pinMode(pin6, OUTPUT);
  pinMode(pin7, OUTPUT);
  pinMode(bitEntrada, INPUT);
  Serial.begin(921600);
}

void loop()
{
  if (digitalRead(bitEntrada) == 1)
  {//Serial.print("hola");
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
  else
  {
    fLecturaAux = analogRead(1) * 5 / 1023;
    fError = ref - fLecturaAux;
    ut = (ut_1 + (kp + ki + kd) * fError - (2 * kd + kp) * fError_1 + kd * fError_2);

    if (ut > 5.0)
      ut = 5.0;

    ut_1 = ut;
    fError_2 = fError_1;
    fError_1 = fError;

    writeBin(ut * 255 * 0.2);
    delayMicroseconds(610);
  }
}
void writeBin(long valor)
{

  digitalWrite(pin0, (valor & 1) >> 0x00);
  digitalWrite(pin1, (valor & 2) >> 0x01);
  digitalWrite(pin2, (valor & 4) >> 0x02);
  digitalWrite(pin3, (valor & 8) >> 0x03);
  digitalWrite(pin4, (valor & 16) >> 0x04);
  digitalWrite(pin5, (valor & 32) >> 0x05);
  digitalWrite(pin6, (valor & 64) >> 0x06);
  digitalWrite(pin7, (valor & 128) >> 0x07);
}