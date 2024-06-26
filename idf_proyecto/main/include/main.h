#ifndef _MAIN_H
#define _MAIN_H
/*_MAIN_H*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "freertos/queue.h"
#include "esp_heap_caps.h"
#include "driver/uart.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include "soc/uart_struct.h"

#ifdef __cplusplus
extern "C"
{
#endif

#define TXD (4)
#define RXD (5)
#define RTS (18)
#define CTS (19)

#define BUF_SIZE (1024)
    static const int RX_BUF_SIZE = 1024;

#define TXD_PIN (GPIO_NUM_1)
#define RXD_PIN (GPIO_NUM_3)

#define BAUD_RATE 115200
#define SELECTED_UART UART_NUM_0

#define TAM_COLA_SECANTE 1 /*1 mensajes*/
#define TAM_MSG_SECANTE 8  /*Cada Mensaje 1 Double (8 bytes)*/
#define TAM_COLA_UART 10   /*10 mensajes*/
#define TAM_MSG_UART 20    /*Cada Mensaje 5 caracteres de 1 byte cada uno*/

#define CMD_CONFIGURAR_CONTROLADOR 'p'
#define CMD_ABRIR_COMUNICACION 'o'
#define CMD_CERRAR_COMUNICACION 'c'

#define FLOAT_SCALER 100000000.0

    // #define DEBUG

    /**
     * Estructura para variables de control
     */
    struct _tControl
    {
        double ref;
        double k1, k2;
        double Gu;
        double G;
        double Gy;
        double Ko;
        bool isConfig;
        bool isRunning;
        bool isAproximating;
        bool isControlling;
    };

    /**
     * Estructura de función de transferencia en dominio Z
     */
    struct _tTF
    {
        /*
            # bb2 z^2 + bb1 z + bb0      B(z)
            # -----------------------  = ----
            # z^2 + aa1 z + aa0          A(z)
        */

        double b0, b1, b2;
        double a0, a1, a2;
    };

    /**
     * Estructura para variables iniciales y mutables
     */
    struct _tControlInit
    {
        double planta_x1;
        double planta_x2;
        double hue_x1;
        double huy_x1;
        double sec_x0;
        double sec_x1;
        double sec_x2;
    };

    /**
     * Declaración de parámetros
     */
    struct _tControlInit tControlParams;
    struct _tControl tControl;
    struct _tTF Gp;

    QueueHandle_t uartQueue;
    QueueHandle_t aproxQueue;

    /**
     * Tareas
     */
    static void rx_task(void *arg);
    static void aproxTask(void *arg);
    static void controllerTask(void *arg);
    /**
     * Funciones
     */
    int sendData(char *data);
    void initConfig(void);
    double secanteAprox(void);
    double plantaIterativa(double ref, double xi);
    double Gplanta(double error);
    double Gplanta_it(double error);
    double Hue_it(double i);
    double Hue(double i);
    double Huy_it(double i);
    double Huy(double i);
    void configParams(char *datos);
    void controlador(double data);
    /*_MAIN_H*/

#ifdef __cplusplus
}
#endif

#endif