from tkinter import *
from tkinter.ttk import Progressbar
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter
import serial
from serial import SerialException
import sys

################################################################################
#            Puerto para la comunicación
################################################################################
puerto = serial.Serial()
puerto.baudrate = 115200 #230400
puerto.timeout = 10
const_comm = 1
const_comm_extra = 1000000
timeout_max = 999
################################################################################
#            Valores iniciales y de las matrices
################################################################################
y_1 = 0
y_2 = 0
o_x1 = 0
o_x2 = 0
kp = 0
ki = 0
kd = 0
a2 = 0
a1 = 0
a0 = 0
b2 = 0
b1 = 0
b0 = 0
tm = 0
flagConfigurarPlanta = False
flagControlador = False

################################################################################
#            Arreglo vacío para entrada y salida
################################################################################
u = np.array([])
y_out = np.array([])
t = np.array([])
resp_inicial = np.array([])
t_resp_inicial = np.array([])

################################################################################
#             Errores
################################################################################
sError1 = 'Error: 01'  # Error. Campo de puerto está vacío
sError2 = 'Error: 02'  # Error. No hay conexión de puerto
sError4 = 'Error: 04'  # Error en conexión
sError3 = 'Error: 03'  # configure la planta
sError5 = 'Error: 05'  # Error configuración de de controlador

################################################################################
#             Ventana de Interfaz
################################################################################
font_family_bold = "Helvetica 10 bold"
font_family_italic = "Helvetica 10 italic"
comm_color = "#44bd32"
comm_active_color = '#44bd32'
comm_disabled_color = '#7f8fa6'
graph_color = '#fbc531'
fg_color = "#2f3640"
bg_color = "#0097e6"
size_error_ventana = "250x100"

window = Tk()
window.title("Interfaz")
window.geometry('800x550')
window.configure(background=bg_color)

titulo_coord_y = 20  # ALtura inicial de espacios


################################################################################
#            Error de conexión al puerto
################################################################################
def port_error():
    puerto.close()  # no se logró conectar
    # abrir nueva ventana de diálogo
    error = Tk()
    error.title('Error: 04')
    error.geometry(size_error_ventana)
    lbl_port_error = Label(error, text="Error en conexión")
    lbl_port_error.pack(padx=10, pady=30)


################################################################################
#            Función para gestionar apertura de puerto
################################################################################
def port_open():
    try:
        puerto.open()
        btn_config_planta.config(state='active')
        btn_cont.config(state='active')
        return True
    except SerialException:
        port_error()
        return None


################################################################################
#            Función para configurar el controlador
################################################################################
def setup_controlador():
    global kp, kd, ki, flagControlador
    flagControlador = True
    kp = float(entry_kp.get()) * const_comm * const_comm_extra
    kd = float(entry_kd.get()) * const_comm * const_comm_extra
    ki = float(entry_ki.get()) * const_comm * const_comm_extra

    if puerto.is_open == 1 and flagControlador:
        # puerto.reset_input_buffer()
        puerto.write(b'p')
        puerto.write(
            (str(kp) + "\x7C" + str(kd) + "\x7C" + str(ki) + "\n").encode())


################################################################################
#            Función para configuración inicial
################################################################################
def setup_init():
    global a2, a1, a0, b0, b1, b2, tm, t, flagConfigurarPlanta, resp_inicial, \
        t_resp_inicial
    flagConfigurarPlanta = True

    a2 = float(entry_A2.get())  # 1
    a1 = float(entry_A1.get())  # 2
    a0 = float(entry_A0.get())  # 3
    b0 = float(entry_B0.get())  # 5
    b1 = float(entry_B1.get())  # 5
    b2 = float(entry_B2.get())  # 5
    tm = float(entry_TM.get())  # 4

    t_resp_inicial = np.linspace(0, 1, num=timeout_max) * tm
    resp_inicial = np.array([])

    for _ in t_resp_inicial:
        y_inicial = np.array([])#planta(1.00)
        resp_inicial = np.append(resp_inicial, y_inicial)

    btn_graficar_inicio.config(state='active', bg=graph_color)


################################################################################
#            Función para obtener la respuesta de la planta
################################################################################
def respuesta_planta():
    global puerto, u, t, y_out, a2, a1, a0, b0, tm, o_x1, o_x2, \
        flagConfigurarPlanta
    o_x1 = 0
    o_x2 = 0

    if puerto.is_open == 1 and flagConfigurarPlanta and flagControlador:
        puerto.reset_input_buffer()
        t = np.array([])
        aux_y = np.array([])
        count = 0
        btn_comunicar.config(bg=comm_disabled_color, text='Espere por favor',
                             state='disabled')

        progress_bar = Progressbar(window, orient=HORIZONTAL, length=100,
                                   mode="determinate",
                                   takefocus=True, maximum=timeout_max)
        progress_bar.place(x=450, y=titulo_coord_y + 390)
        puerto.write(b'o')  # Envía el caracter "o" para iniciar la comunicación
        timeout = timeout_max  # Se realizan timeout_max antes de salir
        print("Comenzando")
        while True:
            port_lect = puerto.readline()  # lectura del puerto
            if len(port_lect) == 0:
                u = np.insert(u, len(u), 0)

            else:
                rx = float(int(port_lect) / const_comm)
                y = planta(rx)
                aux_y = np.append(aux_y, y)
                b = int(y * const_comm)
                puerto.write((str(b) + "\n").encode())
            count += 1  # Aumenta la cuenta
            t = np.append(t, count * tm)
            progress_bar.step()
            window.update()

            ####################################################################
            # Cuando la cuenta termina escribe "c"
            if count > timeout:
                print("Terminado")
                puerto.write(b'c')  # manda msj de apagar
                y_out = aux_y
                btn_comunicar.config(bg=comm_color, text='Iniciar comunicación',
                                     state='active')
                progress_bar.destroy()
                btn_graficar.config(state='active')
                del aux_y
                break

    else:  # si no esta conectado
        # abrir nueva ventana de diálogo
        if not flagConfigurarPlanta:
            error3 = Tk()
            error3.title(sError3)
            error3.geometry(size_error_ventana)

            lbl_configurar = Label(error3,
                                   text="Debe configurar la planta primero",
                                   font=font_family_bold)
            lbl_configurar.pack(padx=10, pady=30)
        elif not flagControlador:

            error_controller = Tk()
            error_controller.title(sError5)
            error_controller.geometry(size_error_ventana)
            lbl_cont = Label(error_controller,
                             text="Se debe configurar el controlador",
                             font=font_family_bold)
            lbl_cont.pack(padx=10, pady=30)
        else:
            error2 = Tk()
            error2.title(sError2)
            error2.geometry(size_error_ventana)

            lbl_conn_port = Label(error2, text="Debe conectarse a un puerto",
                                  font=font_family_bold)
            lbl_conn_port.pack(padx=10, pady=30)


################################################################################
#            Función para conectar el puerto
################################################################################
def conectar_puerto():
    # si hay algo en el cuadro de texto, intento establecer conexión
    if puerto.is_open == 0:  # si esta desconectado entro aquí
        if portCom.get() != "":
            puerto.port = portCom.get()
            if port_open() is not None:
                lbl_desconectado.config(text='Conectado')
                btn_Conectar.config(text='Desconectar')

        # si la entrada de texto está vacía
        if portCom.get() == "":
            # abrir nueva ventana de diálogo
            error = Tk()
            error.title(sError1)
            error.geometry(size_error_ventana)

            # por favor ingrese un puerto válido
            lbl_port_error = Label(error, text="Inserte un puerto válido (Ej: "
                                               "COM1)")
            lbl_port_error.pack(padx=10, pady=30)
    else:  # si está conectado entro aquí
        puerto.close()
        lbl_desconectado.config(text='Desconectado')
        btn_Conectar.config(text='Conectar')


################################################################################
#            Función para obtener los valores de la gráfica
################################################################################
def step_info(time, output):
    print("Sp: %f%s" % ((output.max() / output[-1] - 1) * 100, '%'))
    print("Tr: %fs" % (time[next(
        i for i in range(0, len(output) - 1) if output[i] > output[-1] * .90)] -
                       time[0]))
    # print(
    #     "Ts: %fs" % (time[next(
    #         len(output) - i for i in range(2, len(output) - 1) if
    #         abs(output[-i] / output[-1]) > 1.02)] - time[0]))
    #lblSp.config(text="Sp: %f%s" % ((output.max() / output[-1] - 1) * 100,
    # '%'))
    lbl_datos_sp.config(text="Sp: %f%s" % ((output.max() / output[-1] - 1) *
                                            100, '%'))
    lbl_datos_tr.config(text="Tr: %fs" % (time[next(
        i for i in range(0, len(output) - 1) if output[i] > output[-1] * .90)] -
                       time[0]))
    # lbl_datos_ts.config(text="Ts: %fs" % (time[next(
    #         len(output) - i for i in range(2, len(output) - 1) if
    #         abs(output[-i] / output[-1]) > 1.02)] - time[0]))

################################################################################
#            Función para obtener emulación de la planta
################################################################################
def planta(signal):
    global o_x1, o_x2
    o2 = o_x2
    output = b2 * signal + o_x1
    o_x1 = b1 * signal - a1 * output + o_x2
    o_x2 = b0 * signal - a0 * output

    return output


################################################################################
#                 Función para graficar respuesta
################################################################################
def graficar_respuesta():
    global t, y_out
    # print(t)
    # print(y_out)
    t = (t - t[0]) * tm
    step_info(t,y_out)
    plt.plot(t, y_out)
    # plt.plot(y_out)
    # plt.plot(t)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()



################################################################################
#            Función para graficar respuesta natural
################################################################################
def graficar_inicio():
    global tm, resp_inicial, t_resp_inicial
    resp_inicial = np.array([])
    for _ in t_resp_inicial:
        y_inicial = planta(1.00 * const_comm_extra)
        resp_inicial = np.append(resp_inicial, y_inicial)
    plt.plot(t_resp_inicial, resp_inicial)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()

################################################################################
#                    título
################################################################################

lbl_title = Label(window, text="Interfaz gráfica del controlador PID",
                  bg=bg_color,
                       fg=fg_color, font="Helvetica 15 bold")
lbl_title.place(x=250, y=10)
################################################################################
#             Datos gráfico respuesta controlada
################################################################################
#   Para mostrar los valores de la gráfica en la ventana emergente
lbl_datos = Label(window, bg=bg_color, fg=fg_color, text="Datos del gráfico",
                  font="Helvetica 12 bold")
lbl_datos.place(x=30, y=titulo_coord_y +180)

lbl_datos_sp = Label(window, bg=bg_color, fg=fg_color, text="",
                  font=font_family_italic)
lbl_datos_sp.place(x=40, y=titulo_coord_y +220)

lbl_datos_tr = Label(window, bg=bg_color, fg=fg_color, text="",
                  font=font_family_italic)
lbl_datos_tr.place(x=40, y=titulo_coord_y +250)

lbl_datos_ts = Label(window, bg=bg_color, fg=fg_color, text="",
                  font=font_family_italic)
lbl_datos_ts.place(x=40, y=titulo_coord_y +280)

################################################################################
#                     ECUACIÓN DE PLANTA
################################################################################
lbl_equation1 = Label(window, text="Ecuación de la planta=",
                      bg=bg_color, fg=fg_color, font=font_family_bold)
lbl_equation1.place(x=320, y=titulo_coord_y + 30)
lbl_equation2 = Label(window, text="(b2*z^2+b1*z+b0)/(a2*z^2+a1*z+a0)",
                      bg=bg_color, fg=fg_color, font=font_family_italic)
lbl_equation2.place(x=320, y=titulo_coord_y +50)

################################################################################
#                     COEFICIENTE A2
################################################################################
lbl_A2 = Label(window, text="a2", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_A2.place(x=370, y=titulo_coord_y +90)
text_A2 = StringVar()
text_A2.set('1')
entry_A2 = Entry(window, width=10, textvariable=text_A2, state=DISABLED)
entry_A2.place(x=400, y=titulo_coord_y +90)

################################################################################
#                     COEFICIENTE A1
################################################################################
lbl_A1 = Label(window, text="a1", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_A1.place(x=370, y=titulo_coord_y +120)
text_A1 = StringVar()
text_A1.set('-1.007')
entry_A1 = Entry(window, width=10, textvariable=text_A1)
entry_A1.place(x=400, y=titulo_coord_y +120)

################################################################################
#                     COEFICIENTE A0
################################################################################
lbl_A0 = Label(window, text="a0", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_A0.place(x=370, y=titulo_coord_y +150)
text_A0 = StringVar()
text_A0.set('0.01084')
entry_A0 = Entry(window, width=10, textvariable=text_A0)
entry_A0.place(x=400, y=titulo_coord_y +150)

################################################################################
#                     COEFICIENTE B2
################################################################################
lbl_B2 = Label(window, text="b2", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_B2.place(x=370, y=titulo_coord_y +180)
text_B2 = StringVar()
text_B2.set('0')
entry_B2 = Entry(window, width=10, textvariable=text_B2)
entry_B2.place(x=400, y=titulo_coord_y +180)

################################################################################
#                     COEFICIENTE B1
################################################################################
lbl_B1 = Label(window, text="b1", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_B1.place(x=370, y=titulo_coord_y +210)
text_B1 = StringVar()
text_B1.set('0.0603')
entry_B1 = Entry(window, width=10, textvariable=text_B1)
entry_B1.place(x=400, y=titulo_coord_y +210)

################################################################################
#                     COEFICIENTE B0
################################################################################
lbl_B0 = Label(window, text="b0", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_B0.place(x=370, y=titulo_coord_y +240)
text_B0 = StringVar()
text_B0.set('0.01603')
entry_B0 = Entry(window, width=10, textvariable=text_B0)
entry_B0.place(x=400, y=titulo_coord_y +240)

################################################################################
#                     TIEMPO DE MUESTREO
################################################################################
lbl_TM = Label(window, text="Tm", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_TM.place(x=370, y=titulo_coord_y +270)
text_TM = StringVar()
text_TM.set('3.5e-4')
entry_TM = Entry(window, width=10, textvariable=text_TM)
entry_TM.place(x=400, y=titulo_coord_y +270)

################################################################################
#                     CONTROLADOR
################################################################################
lbl_controller = Label(window, text="Ingrese los valores del PID", bg=bg_color,
                       fg=fg_color, font=font_family_bold)
lbl_controller.place(x=570, y=titulo_coord_y + 30)

################################################################################
#                     K PROPORCIONAL
################################################################################
lbl_kp = Label(window, text="Kp", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_kp.place(x=575, y=titulo_coord_y +60)
text_kp = StringVar()
text_kp.set('0.24753')
entry_kp = Entry(window, width=10, textvariable=text_kp)
entry_kp.place(x=610, y=titulo_coord_y +60)

################################################################################
#                     K DERIVATIVA
################################################################################
lbl_kd = Label(window, text="Kd", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_kd.place(x=575, y=titulo_coord_y +90)
text_kd = StringVar()
text_kd.set('4.3151e-5')
entry_kd = Entry(window, width=10, textvariable=text_kd)
entry_kd.place(x=610, y=titulo_coord_y +90)

################################################################################
#                     K INTEGRAL
################################################################################
lbl_ki = Label(window, text="Ki", bg=bg_color, fg=fg_color,
               font=font_family_bold)
lbl_ki.place(x=575, y=titulo_coord_y +120)
text_ki = StringVar()
text_ki.set('5.4532')
entry_ki = Entry(window, width=10, textvariable=text_ki)
entry_ki.place(x=610, y=titulo_coord_y +120)

################################################################################
# 				BOTÓN PARA CONFIGURAR PLANTA
################################################################################
btn_config_planta = Button(window, text="Configurar Planta", command=setup_init,
             font=font_family_bold, state='disabled')
btn_config_planta.place(x=380, y=titulo_coord_y +310)
# btn.grid(column=1,row =5)

################################################################################
#                BOTÓN CONFIGURAR CONTROLADOR
################################################################################
btn_cont = Button(window, text="Configurar el controlador",
                  command=setup_controlador, font=font_family_bold,
                  state='disabled')
btn_cont.place(x=570, y=titulo_coord_y +150)

################################################################################
# 				BOTÓN PARA CONECTAR PUERTO
################################################################################

lbl_port = Label(window, text="Inserte un puerto (Ejemplo: COM#):",
                 bg=bg_color, fg=fg_color, font=font_family_bold)
lbl_port.place(x=30, y=titulo_coord_y + 30)
portCom = Entry(window, width=10)
portCom.place(x=40, y=titulo_coord_y + 60)
lbl_desconectado = Label(window, text="Desconectado", bg=bg_color, fg=fg_color,
                         font=font_family_bold)
lbl_desconectado.place(x=30, y=titulo_coord_y + 100)
btn_Conectar = Button(window, text="Conectar", command=conectar_puerto, width=9,
                      font=font_family_bold)
btn_Conectar.place(x=40, y=titulo_coord_y + 130)

################################################################################
# 			BOTÓN PARA INICIAR COMUNICACIÓN
################################################################################
btn_comunicar = Button(window, text="Iniciar comunicación", bg=comm_color,
                       command=respuesta_planta, font=font_family_bold)
btn_comunicar.place(x=300, y=titulo_coord_y + 390)

################################################################################
# 			BOTÓN PARA GRAFICAR RESPUESTA
################################################################################
btn_graficar = Button(window, text="Graficar respuesta controlada",
                      bg=graph_color, command=graficar_respuesta,
                      font=font_family_bold, state='disabled')
btn_graficar.place(x=120, y=titulo_coord_y +440)

################################################################################
# 			BOTÓN PARA GRAFICAR RESPUESTA INICIAL
################################################################################
btn_graficar_inicio = Button(window, text="Graficar respuesta original",
                             bg=graph_color, command=graficar_inicio,
                             font=font_family_bold, state='disabled')
btn_graficar_inicio.place(x=420, y=titulo_coord_y +440)

if __name__ == '__main__':
    window.mainloop()
