
from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
from tkinter.font import Font
from control.matlab import lsim
from control import StateSpace as ss
import control
import serial
import time
import sys

flag = 2
bandera = False

# definiendo objeto para la comunicacion
puerto = serial.Serial() 		
puerto.baudrate = 115200
puerto.timeout = 10
puerto.port="COM5"
puerto.open()



y_1=0
y_2=0
A = np.array([[0, 1E4*0.2340], [-0.0061*1E4, -1E4*1.2927]])
B = np.array([[0.0], [1.2195*1E3]])
C = np.array([[1.0, 0.0]])
D = 0.0
system = ss(A, B, C, D)
u=np.array([])
yout=np.array([])


bg_color = "#9c9c9c"
size_error_ventana= "250x100"

sError1='Error: 01' # Error. Campo de puerto esta vacio
sError2='Error: 02' # Error. No hay conexion de puerto

window = Tk()

window.title("PID")

window.geometry('400x200')
window.configure(background=bg_color)
# ---------------------------------------------------------------------------
lbl1 = Label(window, text="Kp",bg=bg_color)
lbl1.grid(column=0, row=0,padx=10,pady=4)
txt1 = Entry(window,width=10)
txt1.grid(column=1, row=0,padx=10,pady=4)


lbl2 = Label(window, text="Kd",bg=bg_color)
lbl2.grid(column=0, row=1,padx=10,pady=4)
txt2 = Entry(window,width=10)
txt2.grid(column=1, row=1,padx=10,pady=4)

lbl3 = Label(window, text="Ki",bg=bg_color)
lbl3.grid(column=0, row=2,padx=10,pady=4)
txt3 = Entry(window,width=10)
txt3.grid(column=1, row=2,padx=10,pady=4)

lbl4 = Label(window, text="Tm",bg=bg_color)
lbl4.grid(column=0, row=3,padx=10,pady=4)
txt4 = Entry(window,width=10)
txt4.grid(column=1, row=3,padx=10,pady=4)


# ---------------------------------------------------------------------------
def update():
	global file_path
	res1 = txt1.get()												#	1
	res2 = txt2.get()												#	2
	res3 = txt3.get()												#	3
	res4 = txt4.get()												#	4



	updt= {
			"Kp": res1,												#	1																	 
	        "Kd": res2,													#	2				
	        "Ki": res3,													#	3					
	        "Tm": res4,	
	        }

def Prueba():

	global flag, puerto,u,A,B,C,D,x,y,t,tout,yout,y_1,y_2

	if flag == 2:
		flag = 1


	if puerto.is_open == 1:  # si esta conectado
		
			if flag == 1:		# encender led
				btn_comunicar.config(bg='green',text='Iniciar comunicación')
				puerto.write(b'o')  		   # manda msj de apagar
				timeout = 200 #time.time() + 5
				count = 0
				print("Comenzando")
				while True:
					lect=puerto.readline()
#					print(lect)
					if(len(lect)==0):
						u=np.insert(u,len(u),0)
					else:
	
#						print("antes")
#						print(u)

						u=np.append(u,float(int(lect)/100))
#						print("despues")
#						print(u)
						Tm=0.61/1000
						t = np.linspace(0, 0.1, num=len(u))*(len(u)-1)*Tm

						
						constante = 1 + (1/1.432e5)*(1/Tm/Tm) + (0.0903/Tm)

						y = (19.9232 * float(int(lect)/100.0)  + (2/1.432E5/Tm/Tm)*y_1 - (1/1.432E5/Tm/Tm)*y_2 + (0.0903/Tm)*y_1)/constante
						y_2=y_1
						y_1=y
						yout =np.append(yout,y)
#						tout, y, x = control.forced_response(system, t, u)
						#print(y)
						b=int(y*100)
#						print(b)
#						print("enviando...")
						# aux=' '.join(map(str, b))
						#env=ser.write(b)
						puerto.write((str(b) + "\n").encode())
#						print(str(env))
					count+=1	
					if count > timeout:
						print("Terminado")
						puerto.write(b'c')  		   # manda msj de apagar
						break

	else: # si no esta conectado
		# abrir nueva ventana de dialogo
		error2 = Tk()				
		error2.title(sError2)
		error2.geometry(size_error_ventana)


		myLabel5 = Label(error2,text="Debe conectarse a un puerto")
		myLabel5.pack(padx=10,pady=30)



	

def conectar():
	
	# si hay algo en el cuadro de texto, intento establecer conexion
	if puerto.is_open == 0:			# si esta desconectado entro aqui
		if portCom.get() != "":

			puerto.port = portCom.get()

			try:
				puerto.open()
				myLabel2.config(text='Conectado')
			except:
				puerto.close()		# no se logró conectar

				# abrir nueva ventana de dialogo
				error = Tk()				
				error.title('Error: 04')
				error.geometry(size_error_ventana)

				myLabel4 = Label(error,text="Error en conexión")
				myLabel4.pack(padx=10,pady=30)

		# si la entrada de texto esta vacia	
		if portCom.get() == "":

			# abrir nueva ventana de dialogo
			error = Tk()				
			error.title(sError1)
			error.geometry(size_error_ventana)

			# por favor ingrese un puerto valido
			myLabel4 = Label(error,text="Inserte puerto válido")
			myLabel4.pack(padx=10,pady=30)
	else:					# si esta conectado entro aqui
		puerto.close()
		myLabel2.config(text='Desconectado')

##################################################################
#                 Funcion para graficar

def Graficar():

	global flag, puerto,u,A,B,C,D,x,y,t,tout,yout

	# print(x)
	# print("\n\n\n")
	# print(y)
	# print("\n\n\n")
	# print(t)
	# print("\n\n\n")
	# print(tout)
	# print("\n\n\n")
	#print(u)
	#print(yout)
	plt.plot(t,yout)
	plt.grid(alpha=0.3)
	plt.xlabel('t')
	plt.show()










####################################################################
# 				BOTON PARA CONFIGURAR PID

btn = Button(window, text="Enviar PID",command = update)
btn.grid(column=1,row =5)


####################################################################
# 				BOTON PARA CONECTAR PUERTO


myLabel = Label(window,text="Inserte puerto:", bg=bg_color)
myLabel.grid(column=3,row = 0)
#myLabel.pack(padx=10,pady=20)

myLabel2 = Label(window,text="Desconectado", bg=bg_color)
myLabel2.grid(column=3,row=2)

myButton1 = Button(window, text="Conectar",command=conectar,width=9)
myButton1.grid(column=3,row=3)

portCom = Entry(window,width=10)
portCom.grid(column=3,row = 1)
#portCom.pack(padx=12,pady=15)
portC = portCom.get()


#####################################################################
# 			BOTON PARA INICIAR COMUNICACION

btn_comunicar = Button(window,text="Iniciar comunicación",bg='green',command=Prueba)
#btn_comunicar.pack(padx=20,pady=20)
btn_comunicar.grid(column=2,row=7)

#######################################################################
#               Boton para comunicación

btn_graficar = Button(window,text="Graficar",bg='green',command=Graficar)
#btn_comunicar.pack(padx=20,pady=20)
btn_graficar.grid(column=2,row=9)


window.mainloop()