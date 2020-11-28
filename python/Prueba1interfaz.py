
from tkinter import *
from tkinter import filedialog
from tkinter.font import Font

window = Tk()

window.title("PID")

window.geometry('1000x600')

# ---------------------------------------------------------------------------
lbl1 = Label(window, text="Kp")
lbl1.grid(column=0, row=0)
txt1 = Entry(window,width=40)
txt1.grid(column=1, row=0)


lbl2 = Label(window, text="Kd")
lbl2.grid(column=0, row=1)
txt2 = Entry(window,width=40)
txt2.grid(column=1, row=1)

lbl3 = Label(window, text="Ki")
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



btn = Button(window, text="Actualizar",command = update)
btn.grid(column=1)

window.mainloop()