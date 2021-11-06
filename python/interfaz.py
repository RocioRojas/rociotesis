from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter
import serial

import sys

###########################################
# definiendo el puerto para la comunicacion
puerto = serial.Serial()
puerto.baudrate = 921600
puerto.timeout = 10
# puerto.port = "COM6"
# puerto.open()
###########################################
# Valores iniciales y de las matrices
y_1 = 0
y_2 = 0

banderaConfigurar = False
banderacontrolador = False
#################################
# Arreglo vacio para entrada y salida
u = np.array([])
yout = np.array([])
t = np.array([])
y = 0
###################################
# Backgraund color y tamaño de la ventana
bg_color = "#c2dbff"
size_error_ventana = "250x100"

######################################
# Errores
sError1 = 'Error: 01'  # Error. Campo de puerto esta vacio
sError2 = 'Error: 02'  # Error. No hay conexion de puerto
sError4 = 'Error: 04'  # Error en conexión
sError3 = 'Error: 03'  # configure la planta
sError5='Error: 05'   # Error configuración de de controlador
#####################################
# Ventana de Window

window = Tk()

window.title("PID")

window.geometry('800x500')

window.configure(background=bg_color)

#######################################################################
#             Autotamano de la pantalla


###################################################################
#   Para mostrar los valores de la grafica en la ventana emergente
lbldatos = Label(window, bg=bg_color, fg="#000", text="Datos del gráfico",font="Helvetica 12 bold")
lbldatos.place(x=50, y=400)
lblSp = Label(window, bg=bg_color, fg="#000")
lblSp.place(x=50, y=420)



###############################################################
# Para mostrar en la ventana emergente donde meter los valores de a2,a1,a0,b0

lbla123 = Label(window, text="Ecuación de la planta= b0/(a2*s^2+a1*s+a0)", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=30, y=10)

lbla2 = Label(window, text="a2", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=100, y=50)
textoa2 = StringVar()
txta2 = Entry(window, width=10, textvariable=textoa2)
textoa2.set(1)
txta2.place(x=130, y=50)


textoa1 = StringVar()
lbla1 = Label(window, text="a1", bg=bg_color, fg="#000", font="Helvetica 10 bold").place(x=100, y=80)
txta1 = Entry(window, width=10, textvariable=textoa1)
textoa1.set(1.293E4)
txta1.place(x=130, y=80)


lbla0 = Label(window, text="a0", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=100, y=110)
textoa0 = StringVar()
txta0 = Entry(window, width=10, textvariable=textoa0)
textoa0.set(1.432e5)
txta0.place(x=130, y=110)


lblb0 = Label(window, text="b0", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=100, y=140)
textob0 = StringVar()
txtb0 = Entry(window, width=10, textvariable=textob0)
textob0.set(2.853e6)
txtb0.place(x=130, y=140)


lbltm = Label(window, text="Tm", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=100, y=170)
textotm = StringVar()
txttm1 = Entry(window, width=10, textvariable=textotm)
textotm.set(0.61 / 1000)
txttm1.place(x=130, y=170)
#############################################################
#                     Controlador

lblacon = Label(window, text="Ingrese los valores del PID", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=350, y=10)

lblkp = Label(window, text="Kp", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=355, y=50)
textokp = StringVar()
txtkp = Entry(window, width=10, textvariable=textokp)
textokp.set(1.06)
txtkp.place(x=390, y=50)

lblkd = Label(window, text="Kd", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=355, y=80)
textokd = StringVar()
txtkd = Entry(window, width=10, textvariable=textokd)
textokd.set(-0.08)
txtkd.place(x=390, y=80)

lblki = Label(window, text="Ki", bg=bg_color, fg="#000",font="Helvetica 10 bold").place(x=355, y=110)
textoki = StringVar()
txtki = Entry(window, width=10, textvariable=textoki)
textoki.set(215.7)
txtki.place(x=390, y=110)



# ---------------------------------------------------------------------------

def Controlador():
    global kp, kd, ki, banderacontrolador
    banderacontrolador=True
    kp = float(txtkp.get())*1000
    kd = float(txtkd.get())*1000
    ki = float(txtki.get())*1000


    if puerto.is_open==1 and banderacontrolador==True:
       # puerto.reset_input_buffer()
        puerto.write(b'p')
        puerto.write((str(kp)+"\x7C"+str(kd)+"\x7C"+str(ki) + "\n").encode())
        #puerto.write((str(kd)).encode())
        #puerto.write((str(ki) + "\n").encode())









############################################################3
def configurar():
    global a2,a1,a0,b0,tm,t, banderaConfigurar, trespinicial, respinicial
    banderaConfigurar = True
    trespinicial=np.linspace(0,1,num=499)
    respinicial=np.array([])
    a2 = float(txta2.get())  # 1
    a1 = float(txta1.get())  # 2
    a0 = float(txta0.get())  # 3
    b0 = float(txtb0.get()) # 5
    tm = float(txttm1.get()) # 4

    y_1=0
    y_2=0
    for i in trespinicial:
        yinicial = (1 * b0 * tm * tm + (2 * a2 + a1 * tm) * y_1 - a2 * y_2 - a2 * y_2)/(a2 + a1 * tm + a0 * tm * tm)
        respinicial = np.append(respinicial, yinicial)
        y_2 = y_1
        y_1 = yinicial

def respuestaPlanta():
    global puerto, u, t, yout, a2 , a1 , a0, b0, tm, banderaConfigurar

    ################################################################
    # Si se abre el puerto


    if puerto.is_open == 1 and banderaConfigurar == True and banderacontrolador== True:  # si esta conectado
        puerto.reset_input_buffer()
        auxy = np.array([])
        t = np.array([])
        auxy = np.array([])
        y_2 = 0
        y_1 = 0
        count = 0

        btn_comunicar.config(bg='green', text='Iniciar comunicacion')
        puerto.write(b'o')  # Envia el caracter "o" para iniciar la comunicacion
        timeout = 999  # Se realizan 499 antes de salir del ciclo

        print("Comenzando")
        while True:
            lect = puerto.readline()  # guardar en la variable lect lo que lea el puerto

            if (len(lect) == 0):
               u = np.insert(u, len(u), 0)
            else:


                y = (float(int(lect) / 100) * b0 * tm * tm + (2 * a2 + a1 * tm) * y_1 - a2 * y_2 - a2 * y_2) / ( a2 + a1 * tm +a0 * tm * tm)

                y_2 = y_1
                y_1 = y
                auxy = np.append(auxy, y)

                # print(y)
                b = int(y * 100)

                puerto.write((str(b) + "\n").encode())
            #						print(str(env))
            count += 1  # Aumenta la cuenta
            t = np.append(t, perf_counter())


            ########################################################################
            # Cuando la cuenta termina escribe a "C"
            if count > timeout:
                print("Terminado")
                puerto.write(b'c')  # manda msj de apagar
                yout = auxy
                del auxy
                y_2 = 0
                y_1 = 0
                y = 0
                break

    else:  # si no esta conectado
        # abrir nueva ventana de dialogo
        if banderaConfigurar == False:
            error3 = Tk()
            error3.title(sError3)
            error3.geometry(size_error_ventana)

            labelconfigurar = Label(error3, text="Debe configurar la planta primero", font="Helvetica 10 bold")
            labelconfigurar.pack(padx=10, pady=30)
        elif banderacontrolador == False:


            errorcont=Tk()
            errorcont.title(sError5)
            errorcont.geometry(size_error_ventana)
            labelcont=Label(errorcont, text=" Se debe configurar el controlador", font="Helvetica 10 bold")
            labelcont.pack(padx=10,pady=30)
        else:
            error2 = Tk()
            error2.title(sError2)
            error2.geometry(size_error_ventana)

            labelconectarsep = Label(error2, text="Debe conectarse a un puerto",font="Helvetica 10 bold")
            labelconectarsep.pack(padx=10, pady=30)


def conectar():
    # si hay algo en el cuadro de texto, intento establecer conexion
    if puerto.is_open == 0:  # si esta desconectado entro aqui
        if portCom.get() != "":

            puerto.port = portCom.get()

            try:
                puerto.open()
                labeldesconectado.config(text='Conectado')
            except:
                puerto.close()  # no se logró conectar

                # abrir nueva ventana de dialogo
                error = Tk()
                error.title('Error: 04')
                error.geometry(size_error_ventana)

                labelpuerto = Label(error, text="Error en conexión")
                labelpuerto.pack(padx=10, pady=30)

        # si la entrada de texto esta vacia
        if portCom.get() == "":
            # abrir nueva ventana de dialogo
            error = Tk()
            error.title(sError1)
            error.geometry(size_error_ventana)

            # por favor ingrese un puerto valido
            labelpuerto = Label(error, text="Inserte puerto válido (Ej: Com 1)")
            labelpuerto.pack(padx=10, pady=30)
    else:  # si esta conectado entro aqui
        puerto.close()
        labeldesconectado.config(text='Desconectado')


##################################################################
#            Funcion para obtener los valores de la grafica

def step_info(t, yout):
    print("Sp: %f%s" % ((yout.max() / yout[-1] - 1) * 100, '%'))
    print("Tr: %fs" % (t[next(i for i in range(0, len(yout) - 1) if yout[i] > yout[-1] * .90)] - t[0]))
    print("Ts: %fs" % (t[next(len(yout) - i for i in range(2, len(yout) - 1) if abs(yout[-i] / yout[-1]) > 1.02)] - t[0]))
    lblSp.config(text="Sp: %f%s" % ((yout.max() / yout[-1] - 1) * 100, '%'))


##################################################################
#                 Funcion para graficar

def Graficar():
    global t, yout
    #print(t)
    #print(yout)
    t = t - t[0]
    #step_info(t,yout)
    plt.plot(t,yout)
    #plt.plot(t)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()

def Graficarinicio():
    global tm
    trespinicial = np.linspace(0, tm, num=499)
    respinicial = np.array([])
    plt.plot(trespinicial,respinicial)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()

####################################################################
# 				BOTON PARA CONFIGURAR PLANTA

btn = Button(window, text="Configurar Planta", command=configurar,font="Helvetica 10 bold")
btn.place(x=125, y=210)
# btn.grid(column=1,row =5)
#                  BOTON CONFIGURAR CONTROLADOR


btncont = Button(window, text="Configurar el controlador", command=Controlador,font="Helvetica 10 bold")
btncont.place(x=350, y=150)

####################################################################
# 				BOTON PARA CONECTAR PUERTO


labelPuerto = Label(window, text="Inserte un puerto (Ejemplo: com#):", bg=bg_color, fg="#000", font="Helvetica 10 bold").place(x=570, y=10)

portCom = Entry(window, width=10)
portCom.place(x=580, y=40)

labeldesconectado = Label(window, text="Desconectado", bg=bg_color, fg="#000",font="Helvetica 10 bold")

labeldesconectado.place(x=570, y=80)
btn_Conectar = Button(window, text="Conectar", command=conectar, width=9,font="Helvetica 10 bold")

btn_Conectar.place(x=580, y=110)


portC = portCom.get()



#####################################################################
# 			BOTON PARA INICIAR COMUNICACION

btn_comunicar = Button(window, text="Iniciar comunicación", bg='#99d160', command=respuestaPlanta, font="Helvetica 10 bold")
btn_comunicar.place(x=300, y=270)
#######################################################################
#               Boton para comunicación

btn_graficar = Button(window, text="Graficar respuesta controlada", bg='#f1d600', command=Graficar,font="Helvetica 10 bold")
btn_graficar.place(x=120, y=320)
btn_graficarinicio = Button(window, text="Graficar respuesta original", bg='#f1d600', command=Graficarinicio,font="Helvetica 10 bold")
btn_graficarinicio.place(x=420, y=320)

window.mainloop()
