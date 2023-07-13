
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
const long const_comm = 1;
const long const_comm_extra = 1000000;             //revisar
float fError, fError_1 = 0, fError_2 = 0;         //revisar
float kp, ki, kd;                                 //revisar
float ut, ut_1;                                   //revisar
float Tm = 0.00061;                               //quitar
const float max_output = 5.0 * const_comm_extra;  //revisar
float ref = 1.00 * const_comm_extra, fLecturaAux; //revisar
float o_x1 = 0.00, o_x2 = 0.00;
float error_x1 = 0.00, dTerm_x1 = 0.00, iTerm_x1 = 0.00;
float Yi_m = 0.00;   //revisar
bool flag, flagpid;  //revisar
int iLectura, i = 0; //revisar
char buff[100], datos[100];
char *ptr;
long entero;
long kaux;
void writeBin(long valor); //quitar

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
  Serial.begin(115200);
}

void loop()
{
  //if (digitalRead(bitEntrada) == 1)//quitar
  // { //Serial.print("hola");//quitar
  if (Serial.available())
  {
    iLectura = Serial.read();
    if (iLectura == CMD_CONFIGURAR_PID)
    {
      flagpid = true;
      o_x1 = 0.00;
      o_x2 = 0.00;
      // Serial.print("\x06");//quitar
    }
    else if (iLectura == CMD_ABRIR_COMUNICACION)
    {
      flag = true;
      ut = 0.00;
      o_x1 = 0.00;
      o_x2 = 0.00;
      sprintf(buff, "%d\n", ut);
      Serial.print(buff);
    }
    else if (iLectura == CMD_CERRAR_COMUNICACION)
    {
      ut = 0;
      o_x1 = 0.00;
      o_x2 = 0.00;
      memset(datos, '\0', sizeof(datos));
      memset(buff, '\0', sizeof(buff));
      flag = false;
      dTerm_x1 = 0.00; 
      iTerm_x1 = 0.00;
    }

    else if (flagpid == true || flag == true && iLectura != CMD_ABRIR_COMUNICACION && iLectura != CMD_CONFIGURAR_PID)
    {
      datos[i] = iLectura; //Datos = EEEEE /n

      if (datos[i] == '\n')

      {
        if (flagpid == true) // SE PROCESAN LOS VALORES DE CONFIGURACION DEL PID
        {
          // Serial.print(datos);
          /*//quitar
          char *separator = strchr(datos, '|');
          Serial.print(separator);
          Serial.print(++separator);
          Serial.print(datos);
          */

          char *token = strtok(datos, "|"); // obtengo  kp
          kaux = strtol(token, &ptr, 10);   //Cambio a un entero largo
          kp = kaux / const_comm / const_comm_extra;
          //kp = 0.25054;
          //Serial.println(kp);

          token = strtok(0, "|");         //  obtengo kd
          kaux = strtol(token, &ptr, 10); //Cambio a un entero largo
          kd = kaux / const_comm / const_comm_extra;
          //kd = 0.00011034;
          //Serial.println(kd);

          token = strtok(0, "|");         // obtengo ki
          kaux = strtol(token, &ptr, 10); //Cambio a un entero largo
          ki = kaux / const_comm / const_comm_extra;
          //ki = 5.4552;
          // Serial.println(ki);

          //Limpia el buffer

          memset(datos, '\0', sizeof(datos));
          i = 0;
          flagpid = false;
        }
        else // SE PROCESAN LOS VALORES DE RESPUESTA DE LA PLANTA
        {
          entero = strtol(datos, &ptr, 10); // convierte str a un entero largo
          fLecturaAux = entero / const_comm;
          fError = ref - fLecturaAux;

          ut = pid(fError); //ut_1 + (kp * Tm + ki * Tm + kd) * (fError / Tm) - (2 * kd + kp * Tm) * (fError_1 / Tm) + kd * (fError_2 / Tm);

          // ut_1 = ut;
          // fError_2 = fError_1;
          // fError_1 = fError;
          entero = ut * const_comm;

          sprintf(buff, "%15ld\n", entero);
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

float pid(float error)
{

  float Kp = 0.23676,
        Ti = 0.038959,
        Td = 0.0012415,
        N = 0.10216,
        Ts = 0.35 / 1000;

  float output, iTerm, dTerm;
  /* borrado temporalmente
 kp = 0.24753;
 kd = 4.3151/100000;
 ki = 5.4532;
  output = (kp + ki + kd) * err + o_x1;
  o_x1 = output - (kp + 2 * kd) * err + o_x2;
  o_x2 = kd * err;
  
*/

  /*
float r0 = 4.315/100000,r1 = 0.2475,r2= 5.453,s1 = 1;
output = r0*err + o_x1;
o_x1 = r1*err - s1*output + o_x2;
o_x2 = r2*err; 

  if (output > max_output)
  {
    //output = max_output;
  }
  else if (output < 0.00)
  {
    //output = 0.00;
  }

    
*/

  iTerm = Ts * (error + iTerm_x1) / Ti;
  



  dTerm = (1 / (Ts + (Td / N) )) * ( Td * error - Td * error_x1 + ( (Td / N) * dTerm_x1 ) );
 

  output = Kp * (1 + iTerm + dTerm);
  error_x1 = error;
  iTerm_x1 = iTerm;
   dTerm_x1 = dTerm;
  

  return output;
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
