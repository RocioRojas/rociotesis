
#define CMD_CONFIGURAR_PID 'p'
#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'

/*// configuracion de pines
#define pin0 4  //quitar
#define pin1 0  //quitar
#define pin2 2  //quitar
#define pin3 14 //quitar
#define pin4 12 //quitar
#define pin5 13 //quitar
#define pin6 15 //quitar
#define pin7 3
#define bitEntrada 5*/
float fError, fError_1 = 0, fError_2 = 0;
float kp, ki, kd;
float ut, ut_1;
float Tm = 0.00061;
float ref = 1, fLecturaAux;
bool flag, flagpid;
int iLectura, i = 0;
char buff[100], datos[100];
char *ptr;
unsigned long entero;
long kaux;
void writeBin(long valor);

void setup()
{
  /* pinMode(pin0, OUTPUT); //quitar
  pinMode(pin1, OUTPUT); //quitar
  pinMode(pin2, OUTPUT); //quitar
  pinMode(pin3, OUTPUT); //quitar
  pinMode(pin4, OUTPUT); //quitar
  pinMode(pin5, OUTPUT); //quitar
  pinMode(pin6, OUTPUT); //quitar
  pinMode(pin7, OUTPUT); //quitar
  // pinMode(bitEntrada, INPUT);*/
  Serial.begin(921600);
}

void loop()
{
  //if (digitalRead(bitEntrada) == 1)
  // { //Serial.print("hola");
  if (Serial.available())
  {
    iLectura = Serial.read();
    if (iLectura == CMD_CONFIGURAR_PID)
    {
      flagpid = true;
      // Serial.print("\x06");
    }
    else if (iLectura == CMD_ABRIR_COMUNICACION)
    {

      flag = true;
      ut = 0;
      sprintf(buff, "%d\n", ut);
      Serial.print(buff);
    }
    else if (iLectura == CMD_CERRAR_COMUNICACION)
    {
      ut = 0;
      memset(datos, '\0', sizeof(datos));
      memset(buff, '\0', sizeof(buff));
      flag = false;
    }

    else if (flagpid == true || flag == true && iLectura != CMD_ABRIR_COMUNICACION && iLectura != CMD_CONFIGURAR_PID)
    {
      datos[i] = iLectura; //Datos = EEEEE /n

      if (datos[i] == '\n')

      {
        if (flagpid == true) // SE PROCESAN LOS VALORES DE CONFIGURACION DEL PID
        {
          Serial.print(datos);
          /*
          char *separator = strchr(datos, '|');
          Serial.print(separator);
          Serial.print(++separator);
          Serial.print(datos);
          */

          char *token = strtok(datos, "|"); // obtengo  kp
          kaux = strtol(token, &ptr, 10);   //Cambio a un entero largo
          kp = kaux / 1000.0;
          //Serial.println(kp);

          token = strtok(0, "|");         //  obtengo kd
          kaux = strtol(token, &ptr, 10); //Cambio a un entero largo
          kd = kaux / 1000.0;
          //Serial.println(kd);

          token = strtok(0, "|");         // obtengo ki
          kaux = strtol(token, &ptr, 10); //Cambio a un entero largo
          ki = kaux / 1000.0;
          // Serial.println(ki);

          //Limpia el buffer

          memset(datos, '\0', sizeof(datos));
          i = 0;
          flagpid = false;
        }
        else // SE PROCESAN LOS VALORES DE RESPUESTA DE LA PLANTA
        {
          entero = strtol(datos, &ptr, 10); // convierte str a un entero largo
          fLecturaAux = entero / 100.0;
          fError = ref - fLecturaAux;
          ut = ut_1 + (kp + ki + kd) * fError - (2 * kd + kp) * fError_1 + kd * fError_2;
          //ut = (kp) * fError;
          // ut = 1.0;
          if (ut > 5.0)
            ut = 5.0;

          if (ut < 0.0)
            ut = 0.0;

          ut_1 = ut;
          fError_2 = fError_1;
          fError_1 = fError;
          entero = ut * 100;

          sprintf(buff, "%d\n", entero);
          Serial.print(buff);
          memset(datos, '\0', sizeof(datos));
          i = 0;
        }
      }
      else
      {
        i++;
      }
    }
  }
  // }
  /* else
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
  } */
}
/*void writeBin(long valor)
{

  digitalWrite(pin0, (valor & 1) >> 0x00);
  digitalWrite(pin1, (valor & 2) >> 0x01);
  digitalWrite(pin2, (valor & 4) >> 0x02);
  digitalWrite(pin3, (valor & 8) >> 0x03);
  digitalWrite(pin4, (valor & 16) >> 0x04);
  digitalWrite(pin5, (valor & 32) >> 0x05);
  digitalWrite(pin6, (valor & 64) >> 0x06);
  digitalWrite(pin7, (valor & 128) >> 0x07);
}*/
