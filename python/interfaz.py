import tkinter as tk
from tkinter.ttk import Progressbar
import matplotlib.pyplot as plt
import numpy as np
import serial
from serial import SerialException
from PIL import ImageTk, Image

################################################################################
#            Puerto para la comunicación
################################################################################
puerto = serial.Serial()
puerto.baudrate = 115200  # 230400
puerto.timeout = 10
escalador = 100000000.0
timeout_max = 99
################################################################################
#            Valores iniciales y de las matrices
################################################################################
y_1 = 0
y_2 = 0
o_x1 = 0
o_x2 = 0
oi_x1 = 0
oi_x2 = 0
k1 = 0
k2 = 0
g = 0
gy = 0
gu = 0
ko = 0
ref = 0

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
yout = np.array([])
t = np.array([])
respinicial = np.array([])
trespinicial = np.array([])

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
bg_color = "#ebf5fa"
size_main_window = "850x550"
size_error_ventana = "250x100"
size_info_ventana = "800x700"
size_info_planta_ventana = "500x200"

window = tk.Tk()
window.title("Interfaz HIL")
window.geometry(size_main_window)
window.configure(background=bg_color)

coord_x_entry_cont = 610 + 30  # Altura inicial de espacios
coord_x_lbl_cont = 575  # Altura inicial de espacios
titulo_coord_y = 20  # Altura inicial de espacios
cont_title_coord_y = titulo_coord_y + 30
info_cont_btn_coord_y = titulo_coord_y + 30
info_cont_btn_coord_x = 805

k1_coord_y = titulo_coord_y + 60
k2_coord_y = k1_coord_y + 30
g_coord_y = k2_coord_y + 30
gy_coord_y = g_coord_y + 30
gu_coord_y = gy_coord_y + 30
ko_coord_y = gu_coord_y + 30
ref_coord_y = ko_coord_y + 30
cont_btn_coord_y = ref_coord_y + 30

coord_x_entry_planta = 380  # Altura inicial de espacios
coord_x_lbl_planta = 320  # Altura inicial de espacios
planta_title_coord_y = titulo_coord_y + 30
info_planta_btn_coord_y = titulo_coord_y + 30
info_planta_btn_coord_x = 470

a2_coord_y = titulo_coord_y + 60
a1_coord_y = a2_coord_y + 30
a0_coord_y = a1_coord_y + 30
b2_coord_y = a0_coord_y + 30
b1_coord_y = b2_coord_y + 30
b0_coord_y = b1_coord_y + 30
tm_coord_y = b0_coord_y + 30
planta_btn_coord_y = tm_coord_y + 30


################################################################################
#            Error de conexión al puerto
################################################################################
def port_error():
    puerto.close()  # no se logró conectar
    # abrir nueva ventana de diálogo
    error = tk.Tk()
    error.title('Error: 04')
    error.geometry(size_error_ventana)
    lbl_port_error = tk.Label(error, text="Error en conexión")
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
    global k1, k2, g, gy, gu, ko, ref, flagControlador
    flagControlador = True
    k1 = float(entry_k1.get()) * escalador
    k2 = float(entry_k2.get()) * escalador
    g = float(entry_g.get()) * escalador
    gy = float(entry_gy.get()) * escalador
    gu = float(entry_gu.get()) * escalador
    ko = float(entry_ko.get()) * escalador
    ref = float(entry_ref.get()) * escalador

    if puerto.is_open == 1:
        puerto.reset_input_buffer()
        puerto.write(b'p\n')
        r = ""
        while r != b'\x06':
            r = puerto.read()
        r = r
        # a2 | a1 | a0 | b2 | b1 | b0 | ref | k1 | k2 | gu | g | gy | ko \n
        enviar = str(a2) + "|" + str(a1 * escalador) + "|" \
                 + str(a0 * escalador) + "|" + str(b2 * escalador) \
                 + "|" + str(b1 * escalador) + "|" + str(b0 * escalador) \
                 + "|" + str(ref * escalador) + "|" + str(k1 * escalador) \
                 + "|" + str(k2 * escalador) + "|" + str(gu * escalador) \
                 + "|" + str(g * escalador) + "|" + str(gy * escalador) \
                 + "|" + str(ko * escalador) + "\n"

        puerto.write(enviar.encode())
        r = ""
        while r != b'\x06':
            r = puerto.read()
        r = r


################################################################################
#            Función para la info del controlador
################################################################################
def setup_info_controlador():
    info = tk.Tk()
    info.title('Diagrama de bloques del observador')
    info.geometry(size_info_ventana)

    lbl_port_info = tk.Label(info, text="Diagrama general")
    lbl_port_info.pack()

    img_diagramafinal = Image.open("diagramafinal.jpg")
    img_diagramafinal = img_diagramafinal.resize((800, 333), Image.ANTIALIAS)
    img_diagramafinal = ImageTk.PhotoImage(img_diagramafinal, master=info)
    lbl_diagramafinal = tk.Label(info, image=img_diagramafinal)
    lbl_diagramafinal.image = img_diagramafinal
    lbl_diagramafinal.pack()

    lbl_port_info = tk.Label(info, text="Diagrama interno del observador")
    lbl_port_info.pack()

    img_diagramaobservador = Image.open("observadorreducido.jpg")
    img_diagramaobservador = img_diagramaobservador.resize((800, 333),
                                                           Image.ANTIALIAS)
    img_diagramaobservador = ImageTk.PhotoImage(img_diagramaobservador,
                                                master=info)
    lbl_diagramaobservador = tk.Label(info, image=img_diagramaobservador)
    lbl_diagramaobservador.image = img_diagramaobservador
    lbl_diagramaobservador.pack()


def setup_info_planta():
    info = tk.Tk()
    info.title('Ecuación de la planta')
    info.geometry(size_info_planta_ventana)

    img_planta = Image.open("infoplanta.png")
    img_planta = img_planta.resize((500, 200), Image.ANTIALIAS)
    img_planta = ImageTk.PhotoImage(img_planta, master=info)
    lbl_info_planta = tk.Label(info, image=img_planta)
    lbl_info_planta.image = img_planta
    lbl_info_planta.pack()


################################################################################
#            Función para configuración inicial
################################################################################
def setup_init():
    global a2, a1, a0, b0, b1, b2, tm, t, flagConfigurarPlanta, trespinicial, \
        respinicial
    flagConfigurarPlanta = True
    trespinicial = np.linspace(0, 1, num=499)
    respinicial = np.array([])

    a2 = float(entry_A2.get())  # 1
    a1 = float(entry_A1.get())  # 2
    a0 = float(entry_A0.get())  # 3
    b0 = float(entry_B0.get())  # 5
    b1 = float(entry_B1.get())  # 5
    b2 = float(entry_B2.get())  # 5
    tm = float(entry_TM.get())  # 4

    #y_1 = 0
    #y_2 = 0
    for _ in trespinicial:
        yinicial = planta(1.00)
        respinicial = np.append(respinicial, yinicial)
        #y_2 = y_1
        #y_1 = yinicial

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
        auxy = np.array([])
        count = 0

        btn_comunicar.config(bg=comm_disabled_color, text='Espere por favor',
                             state='disabled')

        btn_comunicar.config(bg='green', text='Iniciar comunicacion')
        progress_bar = Progressbar(window, orient=tk.HORIZONTAL, length=100,
                                   mode="determinate",
                                   takefocus=True, maximum=timeout_max)
        progress_bar.place(x=450, y=titulo_coord_y + 390)
        puerto.write(
            b'o\n')  # Envia el caracter "o" para iniciar la comunicacion
        timeout = timeout_max  # Se realizan timeout_max vueltas

        print("Comenzando")

        while True:
            rxBuf = []
            recv = ""
            puerto.reset_input_buffer()
            while True:
                rx = puerto.read()
                rxBuf.append(rx)
                if rx != b'\x0A':
                    recv = b''.join(rxBuf).decode("utf-8")
                else:
                    break
            lect = recv

            if (len(lect) == 0):
                u = np.insert(u, len(u), 0)
            else:
                y = Gp(float(int(lect) / escalador))
                auxy = np.append(auxy, y)
                b = int(y * escalador)
                puerto.write((str(b) + "\n").encode())
            count += 1  # Aumenta la cuenta
            t = np.append(t, count * tm)
            progress_bar.step()
            window.update()

            ########################################################################
            # Cuando la cuenta termina escribe a "C"
            if count > timeout:
                print("Terminado")
                puerto.write(b'c\n')  # manda msj de apagar
                yout = auxy
                btn_comunicar.config(bg=comm_color, text='Iniciar comunicación',
                                     state='active')
                progress_bar.destroy()
                btn_graficar.config(state='active')
                del auxy
                break

    else:  # si no esta conectado
        # abrir nueva ventana de diálogo
        if not flagConfigurarPlanta:
            error3 = tk.Tk()
            error3.title(sError3)
            error3.geometry(size_error_ventana)

            lbl_configurar = tk.Label(error3,
                                      text="Debe configurar la planta primero",
                                      font=font_family_bold)
            lbl_configurar.pack(padx=10, pady=30)
        elif not flagControlador:

            error_controller = tk.Tk()
            error_controller.title(sError5)
            error_controller.geometry(size_error_ventana)
            lbl_cont = tk.Label(error_controller,
                                text="Se debe configurar el controlador",
                                font=font_family_bold)
            lbl_cont.pack(padx=10, pady=30)
        else:
            error2 = tk.Tk()
            error2.title(sError2)
            error2.geometry(size_error_ventana)

            lbl_conn_port = tk.Label(error2, text="Debe conectarse a un puerto",
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
            error = tk.Tk()
            error.title(sError1)
            error.geometry(size_error_ventana)

            # por favor ingrese un puerto válido
            lbl_port_error = tk.Label(error,
                                      text="Inserte un puerto válido (Ej: "
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
    print("Sp: %f%s" % ((yout.max() / yout[-1] - 1) * 100, '%'))
    print("Tr: %fs" % (t[next(
        i for i in range(0, len(yout) - 1) if yout[i] > yout[-1] * .90)] - t[
                           0]))
    print("Ts: %fs" % (t[next(len(yout) - i for i in range(2, len(yout) - 1) if
                              abs(yout[-i] / yout[-1]) > 1.02)] - t[0]))
    lbl_datos_sp.config(
        text="Sp: %f%s" % ((yout.max() / yout[-1] - 1) * 100, '%'))
    lbl_datos_tr.config(text="Tr: %fs" % (time[next(
        i for i in range(0, len(output) - 1) if output[i] > output[-1] * .90)] -
                                          time[0]))


################################################################################
#            Función para obtener emulación de la planta
################################################################################
def planta(signal):
    global b2, b1, b0, a1, a0, oi_x1, oi_x2
    oi2 = oi_x2
    output = b2 * signal + oi_x1
    oi_x2 = b0 * signal - a0 * output
    oi_x1 = b1 * signal - a1 * output + oi2

    return output


def Gp(error):
    global b2, b1, b0, a1, a0, o_x1, o_x2

    # bb2 z^2 + bb1 z + bb0      Y(z)
    # -----------------------  = ----
    # z^2 + aa1 z + aa0          E(z)

    aa1 = a1  # -0.06544
    aa0 = a0  # -0.8723
    bb0 = b0  # 0.3099
    bb1 = b1  # 0.6199
    bb2 = b2  # 0.3099

    output = bb2 * error + o_x1
    o_x1 = (bb1 * error - aa1 * output) + o_x2
    o_x2 = (bb0 * error - aa0 * output)

    return output


################################################################################
#                 Función para graficar respuesta
################################################################################
def graficar_respuesta():
    global t, yout
    # print(t)
    # print(yout)
    t = t - t[0]
#    step_info(t, yout)
    plt.plot(t, yout)
    # plt.plot(yout)
    # plt.plot(t)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()


################################################################################
#            Función para graficar respuesta natural
################################################################################
def graficar_inicio():
    global tm, respinicial, trespinicial
    # trespinicial = np.linspace(0, tm, num=499)
    # respinicial = np.array([])
    plt.plot(trespinicial, respinicial)
    plt.grid(alpha=0.3)
    plt.xlabel('t')
    plt.show()


################################################################################
#                    título
################################################################################

lbl_title = tk.Label(window, text="Interfaz gráfica del sistema HIL",
                     bg=bg_color,
                     fg=fg_color, font="Helvetica 15 bold")
lbl_title.place(x=250, y=10)
################################################################################
#             Datos gráfico respuesta controlada
################################################################################
#   Para mostrar los valores de la gráfica en la ventana emergente
lbl_datos = tk.Label(window, bg=bg_color, fg=fg_color, text="Datos del gráfico",
                     font="Helvetica 12 bold")
lbl_datos.place(x=30, y=titulo_coord_y + 180)

lbl_datos_sp = tk.Label(window, bg=bg_color, fg=fg_color, text="",
                        font=font_family_italic)
lbl_datos_sp.place(x=40, y=titulo_coord_y + 220)

lbl_datos_tr = tk.Label(window, bg=bg_color, fg=fg_color, text="",
                        font=font_family_italic)
lbl_datos_tr.place(x=40, y=titulo_coord_y + 250)

lbl_datos_ts = tk.Label(window, bg=bg_color, fg=fg_color, text="",
                        font=font_family_italic)
lbl_datos_ts.place(x=40, y=titulo_coord_y + 280)

################################################################################
#                     ECUACIÓN DE PLANTA
################################################################################
lbl_equation1 = tk.Label(window, text="Ecuación de la planta",
                         bg=bg_color, fg=fg_color, font=font_family_bold)
lbl_equation1.place(x=coord_x_lbl_planta, y=planta_title_coord_y)
# lbl_equation2 = tk.Label(window, text="(b2*z^2+b1*z+b0)/(a2*z^2+a1*z+a0)",
#                      bg=bg_color, fg=fg_color, font=font_family_italic)
# lbl_equation2.place(x=320, y=titulo_coord_y +50)

################################################################################
#                BOTÓN INFO PLANTA
################################################################################
btn_info_planta = tk.Button(window, text="i",
                            command=setup_info_planta, font=font_family_bold)
btn_info_planta.place(x=info_planta_btn_coord_x, y=info_planta_btn_coord_y)

################################################################################
#                     COEFICIENTE A2
################################################################################
lbl_A2 = tk.Label(window, text="a2", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_A2.place(x=coord_x_lbl_planta, y=a2_coord_y)
text_A2 = tk.StringVar()
text_A2.set('1')
entry_A2 = tk.Entry(window, width=10, textvariable=text_A2, state=tk.DISABLED)
entry_A2.place(x=coord_x_entry_planta, y=a2_coord_y)

################################################################################
#                     COEFICIENTE A1
################################################################################
lbl_A1 = tk.Label(window, text="a1", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_A1.place(x=coord_x_lbl_planta, y=a1_coord_y)
text_A1 = tk.StringVar()
text_A1.set('-0.06544')
entry_A1 = tk.Entry(window, width=10, textvariable=text_A1)
entry_A1.place(x=coord_x_entry_planta, y=a1_coord_y)

################################################################################
#                     COEFICIENTE A0
################################################################################
lbl_A0 = tk.Label(window, text="a0", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_A0.place(x=coord_x_lbl_planta, y=a0_coord_y)
text_A0 = tk.StringVar()
text_A0.set('-0.8723')
entry_A0 = tk.Entry(window, width=10, textvariable=text_A0)
entry_A0.place(x=coord_x_entry_planta, y=a0_coord_y)

################################################################################
#                     COEFICIENTE B2
################################################################################
lbl_B2 = tk.Label(window, text="b2", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_B2.place(x=coord_x_lbl_planta, y=b2_coord_y)
text_B2 = tk.StringVar()
text_B2.set('0.3099')
entry_B2 = tk.Entry(window, width=10, textvariable=text_B2)
entry_B2.place(x=coord_x_entry_planta, y=b2_coord_y)

################################################################################
#                     COEFICIENTE B1
################################################################################
lbl_B1 = tk.Label(window, text="b1", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_B1.place(x=coord_x_lbl_planta, y=b1_coord_y)
text_B1 = tk.StringVar()
text_B1.set('0.6199')
entry_B1 = tk.Entry(window, width=10, textvariable=text_B1)
entry_B1.place(x=coord_x_entry_planta, y=b1_coord_y)

################################################################################
#                     COEFICIENTE B0
################################################################################
lbl_B0 = tk.Label(window, text="b0", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_B0.place(x=coord_x_lbl_planta, y=b0_coord_y)
text_B0 = tk.StringVar()
text_B0.set('0.3099')
entry_B0 = tk.Entry(window, width=10, textvariable=text_B0)
entry_B0.place(x=coord_x_entry_planta, y=b0_coord_y)

################################################################################
#                     TIEMPO DE MUESTREO
################################################################################
lbl_TM = tk.Label(window, text="Tm", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_TM.place(x=coord_x_lbl_planta, y=tm_coord_y)
text_TM = tk.StringVar()
text_TM.set('3.3e-3')
entry_TM = tk.Entry(window, width=10, textvariable=text_TM)
entry_TM.place(x=coord_x_entry_planta, y=tm_coord_y)

################################################################################
#                     CONTROLADOR
################################################################################
lbl_controller = tk.Label(window, text="Ingrese los valores del controlador",
                          bg=bg_color,
                          fg=fg_color, font=font_family_bold)
lbl_controller.place(x=coord_x_lbl_cont, y=cont_title_coord_y)

################################################################################
#                           Kacker 1
################################################################################
lbl_k1 = tk.Label(window, text="Kacker 1", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_k1.place(x=coord_x_lbl_cont, y=k1_coord_y)
text_k1 = tk.StringVar()
text_k1.set('0.0870')
entry_k1 = tk.Entry(window, width=10, textvariable=text_k1)
entry_k1.place(x=coord_x_entry_cont, y=k1_coord_y)

################################################################################
#                           Kacker 2
################################################################################
lbl_k2 = tk.Label(window, text="Kacker 2", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_k2.place(x=coord_x_lbl_cont, y=k2_coord_y)
text_k2 = tk.StringVar()
text_k2.set('-7.4854')
entry_k2 = tk.Entry(window, width=10, textvariable=text_k2)
entry_k2.place(x=coord_x_entry_cont, y=k2_coord_y)

################################################################################
#                           G
################################################################################
lbl_g = tk.Label(window, text="G", bg=bg_color, fg=fg_color,
                 font=font_family_bold)
lbl_g.place(x=coord_x_lbl_cont, y=g_coord_y)
text_g = tk.StringVar()
text_g.set('-2.6657')
entry_g = tk.Entry(window, width=10, textvariable=text_g)
entry_g.place(x=coord_x_entry_cont, y=g_coord_y)

################################################################################
#                      G_{Y}
################################################################################
lbl_gy = tk.Label(window, text="Gy", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_gy.place(x=coord_x_lbl_cont, y=gy_coord_y)
text_gy = tk.StringVar()
text_gy.set('2.5828')
entry_gy = tk.Entry(window, width=10, textvariable=text_gy)
entry_gy.place(x=coord_x_entry_cont, y=gy_coord_y)

################################################################################
#                     G_{u}
################################################################################
lbl_gu = tk.Label(window, text="Gu", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_gu.place(x=coord_x_lbl_cont, y=gu_coord_y)
text_gu = tk.StringVar()
text_gu.set('1.8291')
entry_gu = tk.Entry(window, width=10, textvariable=text_gu)
entry_gu.place(x=coord_x_entry_cont, y=gu_coord_y)

################################################################################
#                     K_{o}
################################################################################
lbl_ko = tk.Label(window, text="Ko", bg=bg_color, fg=fg_color,
                  font=font_family_bold)
lbl_ko.place(x=coord_x_lbl_cont, y=ko_coord_y)
text_ko = tk.StringVar()
text_ko.set('0.0702')
entry_ko = tk.Entry(window, width=10, textvariable=text_ko)
entry_ko.place(x=coord_x_entry_cont, y=ko_coord_y)

################################################################################
#                     Ref
################################################################################
lbl_ref = tk.Label(window, text="Ref", bg=bg_color, fg=fg_color,
                   font=font_family_bold)
lbl_ref.place(x=coord_x_lbl_cont, y=ref_coord_y)
text_ref = tk.StringVar()
text_ref.set('1')
entry_ref = tk.Entry(window, width=10, textvariable=text_ref)
entry_ref.place(x=coord_x_entry_cont, y=ref_coord_y)

################################################################################
# 				BOTÓN PARA CONFIGURAR PLANTA
################################################################################
btn_config_planta = tk.Button(window, text="Configurar Planta",
                              command=setup_init,
                              font=font_family_bold, state='disabled')
btn_config_planta.place(x=coord_x_lbl_planta, y=planta_btn_coord_y)
# btn.grid(column=1,row =5)w

################################################################################
#                BOTÓN CONFIGURAR CONTROLADOR
################################################################################
btn_cont = tk.Button(window, text="Configurar el controlador",
                     command=setup_controlador, font=font_family_bold,
                     state='disabled')
btn_cont.place(x=coord_x_lbl_cont, y=cont_btn_coord_y)

################################################################################
#                BOTÓN INFO CONTROLADOR
################################################################################
btn_info_cont = tk.Button(window, text="i",
                          command=setup_info_controlador, font=font_family_bold)
btn_info_cont.place(x=info_cont_btn_coord_x, y=info_cont_btn_coord_y)

################################################################################
# 				BOTÓN PARA CONECTAR PUERTO
################################################################################

lbl_port = tk.Label(window, text="Inserte un puerto (Ejemplo: COM#):",
                    bg=bg_color, fg=fg_color, font=font_family_bold)
lbl_port.place(x=30, y=titulo_coord_y + 30)
portCom = tk.Entry(window, width=10)
portCom.place(x=40, y=titulo_coord_y + 60)

lbl_desconectado = tk.Label(window, text="Desconectado", bg=bg_color,
                            fg=fg_color,
                            font=font_family_bold)
lbl_desconectado.place(x=30, y=titulo_coord_y + 100)

btn_Conectar = tk.Button(window, text="Conectar", command=conectar_puerto,
                         width=9,
                         font=font_family_bold)
btn_Conectar.place(x=40, y=titulo_coord_y + 130)

################################################################################
# 			BOTÓN PARA INICIAR COMUNICACIÓN
################################################################################
btn_comunicar = tk.Button(window, text="Iniciar comunicación", bg=comm_color,
                          command=respuesta_planta, font=font_family_bold)
btn_comunicar.place(x=300, y=titulo_coord_y + 390)

################################################################################
# 			BOTÓN PARA GRAFICAR RESPUESTA
################################################################################
btn_graficar = tk.Button(window, text="Graficar respuesta controlada",
                         bg=graph_color, command=graficar_respuesta,
                         font=font_family_bold, state='disabled')
btn_graficar.place(x=120, y=titulo_coord_y + 440)

################################################################################
# 			BOTÓN PARA GRAFICAR RESPUESTA INICIAL
################################################################################
btn_graficar_inicio = tk.Button(window, text="Graficar respuesta original",
                                bg=graph_color, command=graficar_inicio,
                                font=font_family_bold, state='disabled')
btn_graficar_inicio.place(x=420, y=titulo_coord_y + 440)

if __name__ == '__main__':
    window.mainloop()
