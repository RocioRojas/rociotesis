from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
from tkinter.font import Font
from control.matlab import lsim
from control import StateSpace as ss
from time import perf_counter
import control
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
A = np.array([[0, 1E4 * 0.2340], [-0.0061 * 1E4, -1E4 * 1.2927]])
B = np.array([[0.0], [1.2195 * 1E3]])
C = np.array([[1.0, 0.0]])
D = 0.0
###############################
# Creacion del espacio de estado
system = ss(A, B, C, D)
#################################
# Arreglo vacio para entrada y salida
u = np.array([])
yout = np.array([])
# t = np.linspace(0, 1, num=200)
t = np.array([])
###################################
# Backgraund color y tamaño de la ventana
bg_color = "#9c9c9c"
size_error_ventana = "250x100"

######################################
# Errores
sError1 = 'Error: 01'  # Error. Campo de puerto esta vacio
sError2 = 'Error: 02'  # Error. No hay conexion de puerto
sError4 = 'Error: 04'  # Error en conexión
#####################################
# Ventana de Window

window = Tk()

window.title("PID")

window.geometry('600x300')

window.configure(background=bg_color)

#######################################################################
#             Autotamano de la pantalla   


###################################################################
#   Para mostrar los valores de la grafica en la ventana emergente

lblSp = Label(window, bg=bg_color, fg="#fff")
lblSp.place(x=50, y=290)
# lblSp.grid(column=0, row=7,padx=10,pady=4)


###############################################################
# Para mostrar en la ventana emergente donde meter los valores de kp,ki,kd,tm

lblkp = Label(window, text="Kp", bg=bg_color, fg="#fff").place(x=50, y=50)

# lbl1.grid(column=0, row=0,padx=10,pady=4)
txtkp1 = Entry(window, width=10)
txtkp1.place(x=150, y=50)

# txt1.grid(column=1, row=0,padx=10,pady=4)


lblkd = Label(window, text="Kd", bg=bg_color, fg="#fff").place(x=50, y=80)
# lbl2.grid(column=0, row=1,padx=10,pady=4)
txtkd1 = Entry(window, width=10)
txtkd1.place(x=150, y=80)
# txt2.grid(column=1, row=1,padx=10,pady=4)

lblki = Label(window, text="Ki", bg=bg_color, fg="#fff").place(x=50, y=110)
# lbl3.grid(column=0, row=2,padx=10,pady=4)
txtki1 = Entry(window, width=10)
txtki1.place(x=150, y=110)
# txt3.grid(column=1, row=2,padx=10,pady=4)

lbltm = Label(window, text="Tm", bg=bg_color, fg="#fff").place(x=50, y=140)
# lbl4.grid(column=0, row=3,padx=10,pady=4)
txttm1 = Entry(window, width=10)
txttm1.place(x=150, y=140)


# txt4.grid(column=1, row=3,padx=10,pady=4)


# ---------------------------------------------------------------------------
def update():
    global file_path
    kp = txtkp1.get()  # 1
    kd = txtkd1.get()  # 2
    ki = txtki1.get()  # 3
    tm = txttm1.get()  # 4

    updt = {
        "Kp": kp,  # 1
        "Kd": kd,  # 2
        "Ki": ki,  # 3
        "Tm": tm,
    }


def Prueba():
    global puerto, u, A, B, C, D, x, y, t, tout, yout, y_1, y_2
    ################################################################
    # Si se abre el puerto

    if puerto.is_open == 1:  # si esta conectado
        start_time = perf_counter()
        btn_comunicar.config(bg='green', text='Iniciar comunicacion')
        puerto.write(b'o')  # Envia el caracter "o" para iniciar la comunicacion
        timeout = 499  # Se realizan 999 antes de salir del ciclo
        count = 0
        print("Comenzando")
        while True:
            lect = puerto.readline()  # guardar en la variable lect lo que lea el puerto

            #					print(lect)
            if (len(lect) == 0):
                u = np.insert(u, len(u), 0)
            else:

                #						print("antes")
                #						print(u)

                u = np.append(u, float(int(lect) / 100))
                #						print("despues")
                #						print(u)
                Tm = 0.61 / 1000  # tiempo de muestreo

                constante = 1 + (1 / 1.432e5) * (1 / Tm / Tm) + (0.0903 / Tm)

                y = (19.9232 * float(int(lect) / 100.0) + (2 / 1.432E5 / Tm / Tm) * y_1 - (
                        1 / 1.432E5 / Tm / Tm) * y_2 + (0.0903 / Tm) * y_1) / constante  # planta
                y_2 = y_1
                y_1 = y
                yout = np.append(yout, y)
                #						tout, y, x = control.forced_response(system, t, u)
                # print(y)
                b = int(y * 100)
                #						print(b)
                #						print("enviando...")
                # aux=' '.join(map(str, b))
                # env=ser.write(b)
                puerto.write((str(b) + "\n").encode())
            #						print(str(env))
            count += 1  # Aumenta la cuenta
            t = np.append(t, perf_counter())

            ########################################################################
            # Cuando la cuenta termina escribe a "C"
            if count > timeout:
                print("Terminado")
                puerto.write(b'c')  # manda msj de apagar
                break

    else:  # si no esta conectado
        # abrir nueva ventana de dialogo
        error2 = Tk()
        error2.title(sError2)
        error2.geometry(size_error_ventana)

        labelconectarsep = Label(error2, text="Debe conectarse a un puerto")
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
    print(
        "Ts: %fs" % (t[next(len(yout) - i for i in range(2, len(yout) - 1) if abs(yout[-i] / yout[-1]) > 1.02)] - t[0]))
    lblSp.config(text="Sp: %f%s" % ((yout.max() / yout[-1] - 1) * 100, '%'))


##################################################################
#                 Funcion para graficar

def Graficar():
    global flag, puerto, u, A, B, C, D, x, y, t, tout, yout

    # print(x)
    # print("\n\n\n")
    # print(y)
    # print("\n\n\n")
    print(t)
    # print("\n\n\n")
    # print(tout)
    # print("\n\n\n")
    # print(u)
    # print(yout)

    Tm = 0.61 / 1000
    # t = t * 199 * Tm
    #	step_info(t,yout)
    plt.plot(t, yout)
    #plt.plot(t)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()


####################################################################
# 				BOTON PARA CONFIGURAR PID

btn = Button(window, text="Enviar PID", command=update)
btn.place(x=150, y=180)
# btn.grid(column=1,row =5)


####################################################################
# 				BOTON PARA CONECTAR PUERTO


labelPuerto = Label(window, text="Inserte puerto (Ejemplo: com#):", bg=bg_color, fg="#fff").place(x=350, y=50)
# myLabel.grid(column=3,row = 0)
# myLabel.pack(padx=10,pady=20)
portCom = Entry(window, width=10)
portCom.place(x=360, y=80)

labeldesconectado = Label(window, text="Desconectado", bg=bg_color, fg="#fff")
# myLabel2.grid(column=3,row=2)
labeldesconectado.place(x=350, y=110)
btn_Conectar = Button(window, text="Conectar", command=conectar, width=9)
# myButton1.grid(column=3,row=3)
btn_Conectar.place(x=355, y=140)

# portCom.grid(column=3,row = 1)
# portCom.pack(padx=12,pady=15)
portC = portCom.get()

#####################################################################
# 			BOTON PARA INICIAR COMUNICACION

btn_comunicar = Button(window, text="Iniciar comunicación", bg='green', command=Prueba)
# btn_comunicar.pack(padx=20,pady=20)
# btn_comunicar.grid(column=2,row=7)
btn_comunicar.place(x=220, y=210)
#######################################################################
#               Boton para comunicación

btn_graficar = Button(window, text="Graficar", bg='green', command=Graficar)
btn_graficar.place(x=250, y=250)
# btn_comunicar.pack(padx=20,pady=20)
# btn_graficar.grid(column=2,row=9)


window.mainloop()
