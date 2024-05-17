#include "main.h"

void app_main()
{
    initConfig();
    xTaskCreatePinnedToCore(&aproxTask, "aproxTask", BUF_SIZE * 4, NULL, 5, NULL, 0);
    xTaskCreatePinnedToCore(&controllerTask, "controllerTask", BUF_SIZE * 4, NULL, 5, NULL, 0);
    xTaskCreatePinnedToCore(&rx_task, "uart_rx_task", BUF_SIZE * 8, NULL, configMAX_PRIORITIES, NULL, 1);
}

static void rx_task(void *arg)
{
    double dato;
    // esp_log_level_set(RX_TASK_TAG, ESP_LOG_INFO);

    uint8_t *data = (uint8_t *)malloc(RX_BUF_SIZE + 1);
    while (1)
    {
#ifdef DEBUG
        static const char *RX_TASK_TAG = "RX_TASK";
        esp_log_level_set(RX_TASK_TAG, ESP_LOG_INFO);
        ESP_LOGI(RX_TASK_TAG, "RX: %3.9f", dato);
#endif
        const int rxBytes = uart_read_bytes(UART_NUM_0, data, RX_BUF_SIZE, 10 / portTICK_PERIOD_MS);
        if (rxBytes > 1)
        {
            data[rxBytes] = 0;
#ifdef DEBUG
            printf("\n\n\nrx: %s\n\n\n", data);
#endif
            if (xQueueSendToBack(uartQueue, &data, 100 / portTICK_PERIOD_MS) == pdTRUE)
            {
                switch (data[0])
                {
                case CMD_CONFIGURAR_CONTROLADOR:
                    tControl.isConfig = true;
                    sendData("\x06");
                    break;
                case CMD_ABRIR_COMUNICACION:
                    tControl.isRunning = true;
                    char sendBuff[100];
                    double init = Hue(tControl.ref - Huy(tControlParams.sec_x2)); // Gplanta(Hue(fError));
                    sprintf(sendBuff, "%ld\n", (long)((init)*FLOAT_SCALER));
                    sendData(sendBuff);
#ifdef DEBUG
                    printf("sendData: %f\n\n", init);
#endif
                    break;
                case CMD_CERRAR_COMUNICACION:
                    tControl.isRunning = false;
                    sendData("\x06");
                    // falta borrar
                    break;

                default:
                    if (tControl.isConfig == true)
                    {
                        configParams((char *)data);
                    }
                    else if (tControl.isRunning == true)
                    {
                        // controlador((char *)data);
                    }
                    else
                    {
                        memset(data, '\0', RX_BUF_SIZE + 1);
                    }

                    break;
                }
            }
#ifdef DEBUG
            else
            {
                // printf("Error queueing UART send");
            }
#endif
            // ESP_LOGI(RX_TASK_TAG, "Read %s", sendBuff);
            // ESP_LOG_BUFFER_HEXDUMP(RX_TASK_TAG, data, rxBytes, ESP_LOG_INFO);
        }
        // xSemaphoreGive(xS);
        //}
        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
    free(data);
}

int sendData(char *data)
{
    const int len = strlen(data);
    const int txBytes = uart_write_bytes(UART_NUM_0, data, len);
#ifdef DEBUG
    ESP_LOGI("", "Wrote %d bytes", txBytes);
    ESP_LOGI("", "Wrote %s", data);
#endif
    return txBytes;
}

static void controllerTask(void *arg)
{
    char *data = (char *)malloc(RX_BUF_SIZE + 1);
    // char *ptr;
    double res;
    while (1)
    {
        // resp = secanteAprox();
        if (xQueueReceive(aproxQueue, &res, 10 / portTICK_PERIOD_MS) == pdTRUE)
        {
#ifdef DEBUG
            static const char *RX_TASK_TAG = "CONTROLLER_TASK";
            ESP_LOGI(RX_TASK_TAG, "Controller: %3.9f", res);
            // printf("Secante: %3.9f\n\n", resp);
#endif
            // long plantaLong = strtol(data, &ptr, 10);
            double plantaDouble = res;
            controlador(plantaDouble);

            // xSemaphoreGive(xS);
        }
#ifdef DEBUG
        else
        {
            // printf("Error queueing Controller get ");
        }

#endif
        vTaskDelay(50 / portTICK_PERIOD_MS);
    }
    free(data);
}

static void aproxTask(void *arg)
{
    double resp;
    while (1)
    {
        if (xQueueReceive(uartQueue, &resp, 100 / portTICK_PERIOD_MS) == pdTRUE)
        {
#ifdef DEBUG
            static const char *RX_TASK_TAG = "SECANTE_TASK";
            ESP_LOGI(RX_TASK_TAG, "Secante: %3.9f", resp);
            // printf("Secante: %3.9f\n\n", resp);
#endif
            if (tControl.isRunning)
            {
                resp = secanteAprox();
                // xSemaphoreGive(xS);
                if (xQueueSendToBack(aproxQueue, &resp, 100 / portTICK_PERIOD_MS) == pdTRUE)
                {
#ifdef DEBUG
                    printf("queued Aprox send");
#endif
                }
#ifdef DEBUG
                else
                {
                    // printf("Error queueing Aprox send");
                }
#endif
            }
        }
#ifdef DEBUG
        else
        {
            // printf("Error queueing Aprox get");
        }
#endif
        vTaskDelay(50 / portTICK_PERIOD_MS);
    }
}

double Gplanta(double error)
{
    double output = Gp.b2 * error + tControlParams.planta_x1;
    tControlParams.planta_x1 = (Gp.b1 * error - Gp.a1 * output) + tControlParams.planta_x2;
    tControlParams.planta_x2 = (Gp.b0 * error - Gp.a0 * output);
    return output;
}

double plantaIterativa(double ref, double xi)
{
    double e = ref - Huy_it(xi);
    double output = Gplanta_it(Hue_it(e));
    return xi - output;
}

double Gplanta_it(double error)
{
    double output = Gp.b2 * error + tControlParams.planta_x1;
    return output;
}

double Hue_it(double i)
{
    double o = i - tControlParams.hue_x1;
    return o;
}

double Hue(double i)
{
    double o = i - tControlParams.hue_x1;
    tControlParams.hue_x1 = o * tControl.k2 * tControl.Gu;
    return o;
}

double Huy_it(double i)
{
    double o = (tControl.k2 * tControl.G + tControl.k1) * i + tControlParams.huy_x1;
    return o;
}

double Huy(double i)
{
    double o = (tControl.k2 * tControl.G + tControl.k1) * i + tControlParams.huy_x1;
    tControlParams.huy_x1 = i * tControl.k2 * tControl.Gy;
    return o;
}

double secanteAprox()
{
    tControlParams.sec_x0 = 0;
    tControlParams.sec_x1 = 1;
    tControlParams.sec_x2 = 0;
    for (int i = 0; i < 20; i++)
    {
        tControlParams.sec_x2 =
            tControlParams.sec_x0 - (plantaIterativa(tControl.ref, tControlParams.sec_x0) * (tControlParams.sec_x1 - tControlParams.sec_x0) / (plantaIterativa(tControl.ref, tControlParams.sec_x1) - plantaIterativa(tControl.ref, tControlParams.sec_x0)));
        if (fabs(tControlParams.sec_x2 - tControlParams.sec_x1) < 0.0001)
            break;
        tControlParams.sec_x0 = tControlParams.sec_x1;
        tControlParams.sec_x1 = tControlParams.sec_x2;
    }

    return tControlParams.sec_x2;
}

void initConfig()
{
    tControlParams.planta_x1 = 0;
    tControlParams.planta_x2 = 0;
    tControlParams.hue_x1 = 0;
    tControlParams.huy_x1 = 0;
    tControlParams.sec_x0 = 0;
    tControlParams.sec_x1 = 1;
    tControlParams.sec_x2 = 0;

    uartQueue = xQueueCreate(TAM_COLA_UART, TAM_MSG_UART);
    aproxQueue = xQueueCreate(TAM_COLA_SECANTE, TAM_MSG_SECANTE);

    const uart_config_t uart_config = {
        .baud_rate = BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB,
    };
    // We won't use a buffer for sending data.
    uart_driver_install(SELECTED_UART, RX_BUF_SIZE * 2, 0, 0, NULL, 0);
    uart_param_config(SELECTED_UART, &uart_config);
    uart_set_pin(SELECTED_UART, TXD_PIN, RXD_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);

#ifdef DEBUG
    printf("Init done\n\n");
#endif
}

void configParams(char *datos)
{
    char *ptr;
    char *token;
    long tokenAux;
    /**
     * Planta
     */

#ifdef DEBUG
    printf("Datos: %s\n\n", datos);
#endif

    token = strtok(datos, "|");         // obtengo  a2
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    Gp.a2 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("a2: %3.9f\n\n", Gp.a2);
#endif

    token = strtok(0, "|");             //  obtengo a1
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    Gp.a1 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("a1: %3.9f\n\n", Gp.a1);
#endif

    token = strtok(0, "|");             // obtengo a0
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    Gp.a0 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("a0: %3.9f\n\n", Gp.a0);
#endif

    token = strtok(0, "|");             // obtengo b2
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    Gp.b2 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("b2: %3.9f\n\n", Gp.b2);
#endif

    token = strtok(0, "|");             // obtengo b1
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    Gp.b1 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("b1: %3.9f\n\n", Gp.b1);
#endif

    token = strtok(0, "|");             // obtengo b0
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    Gp.b0 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("b0: %3.9f\n\n", Gp.b0);
#endif

    /**
     * Params
     */
    token = strtok(0, "|");             // obtengo ref
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.ref = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("ref: %3.9f\n\n", tControl.ref);
#endif

    token = strtok(0, "|");             // obtengo k1
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.k1 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("k1: %3.9f\n\n", tControl.k1);
#endif

    token = strtok(0, "|");             // obtengo k2
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.k2 = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("k2: %3.9f\n\n", tControl.k2);
#endif

    token = strtok(0, "|");             // obtengo Gu
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.Gu = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("Gu: %3.9f\n\n", tControl.Gu);
#endif

    token = strtok(0, "|");             // obtengo G
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.G = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("G: %3.9f\n\n", tControl.G);
#endif

    token = strtok(0, "|");             // obtengo Gy
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.Gy = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("Gy: %3.9f\n\n", tControl.Gy);
#endif

    token = strtok(0, "|");             // obtengo Ko
    tokenAux = strtol(token, &ptr, 10); // Cambio a un entero largo
    tControl.Ko = tokenAux / FLOAT_SCALER;

#ifdef DEBUG
    printf("Ko: %3.9f\n\n", tControl.Ko);
#endif

    tControl.ref = tControl.ref * tControl.Ko;
    tControl.isConfig = false;
    sendData("\x06");
}

void controlador(double plantaDouble)
{
    char *ptr;
    char sendBuff[100];
#ifdef DEBUG
    printf("plantaDouble: %3.9f\n\n sec_x2: %3.9f\n\n", plantaDouble, tControlParams.sec_x2);
#endif
    double now = Huy(plantaDouble);
    double fError = tControl.ref - now;
    double val = Hue(fError);
    long entero = val * FLOAT_SCALER;
    tControlParams.planta_x1 = (Gp.b1 * val - Gp.a1 * plantaDouble) + tControlParams.planta_x2;
    tControlParams.planta_x2 = (Gp.b0 * val - Gp.a0 * plantaDouble);
    sprintf(sendBuff, "%ld\n", entero);
    sendData(sendBuff);
#ifdef DEBUG
    printf("sendData: %ld\n\n", entero);
#endif
}