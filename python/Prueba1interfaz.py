
from tkinter import *
from tkinter import filedialog
from tkinter.font import Font
import serial
flag = 1

# definiendo objeto para la comunicacion
puerto = serial.Serial() 		
puerto.baudrate = 115200
puerto.timeout = 200


window = Tk()

window.title("PID")

window.geometry('600x600')
window.configure(background="LightSteelBlue3")
# ---------------------------------------------------------------------------
lbl1 = Label(window, text="Kp")
lbl1.grid(column=0, row=0)
txt1 = Entry(window,width=40)
txt1.grid(column=1, row=0)


lbl2 = Label(window, text="Kd")
lbl2.grid(column=0, row=1)
txt2 = Entry(window,width=40)
txt2.grid(column=1, row=1)

lbl3 = Label(window, text="Ki",bg="LightSteelBlue3")
lbl3.grid(column=0, row=2)
txt3 = Entry(window,width=40)
txt3.grid(column=1, row=2)

lbl4 = Label(window, text="Tm")
lbl4.grid(column=0, row=3)
txt4 = Entry(window,width=40)
txt4.grid(column=1, row=3)


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

	global flag, puerto

	if puerto.is_open == 1:  # si esta conectado
		while 1==1:
			if flag == 1:		# encender led
				myButton2.config(bg='green',text='Enviado')
				flag = 2
				puerto.write(b'o')		   # manda msj de apagar
				break
			if flag == 2:		# apagar led
				myButton2.config(bg='red',text='Apagado')
				flag = 1
				puerto.write(b'c')		   # manda msj de apagar	   
				break
	else: # si no esta conectado
		# abrir nueva ventana de dialogo
		error2 = Tk()				
		error2.title('errox02')
		error2.geometry("250x100")


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
				error.title('errox04')
				error.geometry("200x100")

				myLabel4 = Label(error,text="Error en conexión")
				myLabel4.pack(padx=10,pady=30)

		# si la entrada de texto esta vacia	
		if portCom.get() == "":

			# abrir nueva ventana de dialogo
			error = Tk()				
			error.title('errox01')
			error.geometry("200x100")

			# por favor ingrese un puerto valido
			myLabel4 = Label(error,text="Inserte puerto válido")
			myLabel4.pack(padx=10,pady=30)
	else:					# si esta conectado entro aqui
		puerto.close()
		myLabel2.config(text='Desconectado')




myLabel = Label(window,text="Inserte puerto:", bg="LightSteelBlue3")
myLabel.grid(column=2)
#myLabel.pack(padx=10,pady=20)

portCom = Entry(window,width=12)
portCom.grid(column=2)
#portCom.pack(padx=12,pady=15)
portC = portCom.get()

btn = Button(window, text="Actualizar",command = update)
btn.grid(column=1)

myButton2 = Button(window, text="comienzo",bg='green',command=Prueba)
#myButton2.pack(padx=20,pady=20)
myButton2.grid(column=2)

myLabel2 = Label(window,text="Desconectado", bg="LightSteelBlue3")
myLabel2.grid(column=2)

myButton1 = Button(window, text="Conectar",command=conectar,width=9)
myButton1.grid(column=2)
window.mainloop()